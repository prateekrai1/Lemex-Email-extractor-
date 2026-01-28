import json
import time
import re
from typing import List, Optional

from groq import Groq
from dotenv import load_dotenv
from pydantic import ValidationError

from schemas import LLMExtraction, ShipmentExtraction
from prompts import PROMPT_V1
from ports import PortResolver

MAX_RETRIES = 3
INITIAL_BACKOFF = 2
PORTS_PATH = "data/port_codes_reference.json"

def call_llm(client: Groq, prompt: str) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            return response.choices[0].message.content
        except Exception:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(INITIAL_BACKOFF * (2 ** (attempt - 1)))
    raise RuntimeError("Unreachable")

def extract_json(text: str) -> str:
    """
    Extract first JSON object from model output.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return text[start:end + 1]
    raise ValueError("No JSON found")


VALID_INCOTERMS = {
    "FOB", "CIF", "CFR", "EXW", "DDP", "DAP",
    "FCA", "CPT", "CIP", "DPU"
}


def normalize_incoterm(raw: Optional[str]) -> str:
    if not raw:
        return "FOB"

    raw = raw.upper()

    if " OR " in raw:
        return "FOB"

    for term in sorted(VALID_INCOTERMS):
        if raw == term or raw.startswith(term):
            return term

    return "FOB"


def infer_product_line(
    origin_code: Optional[str],
    dest_code: Optional[str]
) -> Optional[str]:
    if not origin_code or not dest_code:
        return None

    if origin_code.startswith("IN") and not dest_code.startswith("IN"):
        return "pl_sea_export_lcl"

    if dest_code.startswith("IN") and not origin_code.startswith("IN"):
        return "pl_sea_import_lcl"

    return None


def normalize_weight(
    value: Optional[float],
    unit: Optional[str]
) -> Optional[float]:
    if value is None or unit is None:
        return None

    unit = unit.lower()

    if unit in {"kg", "kgs", "kilogram", "kilograms"}:
        return round(value, 2)

    if unit in {"lbs", "pounds"}:
        return round(value * 0.453592, 2)

    if unit in {"tonne", "tonnes", "mt"}:
        return round(value * 1000, 2)

    return None


def detect_dg(body: str, mentions: List[str]) -> bool:
    text = body.lower()

    if any(neg in text for neg in [
        "non-dg", "non dg",
        "non-hazardous", "non hazardous",
        "not dangerous"
    ]):
        return False

    if mentions:
        return True

    if re.search(r"class\s*\d", text):
        return True

    if re.search(r"\bun\s*\d{4}\b", text):
        return True

    if any(k in text for k in ["imo", "imdg", "hazardous", "dangerous"]):
        return True

    return False


def empty_shipment(email_id: str) -> ShipmentExtraction:
    return ShipmentExtraction(
        id=email_id,
        product_line=None,
        origin_port_code=None,
        origin_port_name=None,
        destination_port_code=None,
        destination_port_name=None,
        incoterm="FOB",
        cargo_weight_kg=None,
        cargo_cbm=None,
        is_dangerous=False,
    )

def main():
    load_dotenv()

    client = Groq()
    port_resolver = PortResolver(PORTS_PATH)

    with open("data/emails_testing.json", "r") as f:
        emails = json.load(f)

    results: List[dict] = []

    for i, email in enumerate(emails, 1):
        email_id = email["id"]
        subject = email.get("subject", "")
        body = email.get("body", "")

        prompt = PROMPT_V1.format(subject=subject, body=body)

        try:
            raw_response = call_llm(client, prompt)

            try:
                llm_data = LLMExtraction.model_validate_json(raw_response)
            except ValidationError:
                llm_data = LLMExtraction.model_validate_json(
                    extract_json(raw_response)
                )

            origin_code = port_resolver.resolve(llm_data.origin_port_raw)
            dest_code = port_resolver.resolve(llm_data.destination_port_raw)

            origin_name = (
                port_resolver.get_name(origin_code)
                if origin_code else None
            )
            dest_name = (
                port_resolver.get_name(dest_code)
                if dest_code else None
            )

            shipment = ShipmentExtraction(
                id=email_id,
                product_line=infer_product_line(origin_code, dest_code),
                origin_port_code=origin_code,
                origin_port_name=origin_name,
                destination_port_code=dest_code,
                destination_port_name=dest_name,
                incoterm=normalize_incoterm(llm_data.incoterm_raw),
                cargo_weight_kg=normalize_weight(
                    llm_data.cargo_weight_value,
                    llm_data.cargo_weight_unit
                ),
                cargo_cbm=(
                    round(llm_data.cargo_cbm_value, 2)
                    if llm_data.cargo_cbm_value is not None
                    else None
                ),
                is_dangerous=detect_dg(
                    body,
                    llm_data.dangerous_goods_mentions
                ),
            )

        except (ValidationError, json.JSONDecodeError, ValueError):
            shipment = empty_shipment(email_id)

        results.append(shipment.model_dump())
        print(f"[{i}/{len(emails)}] Processed {email_id}")

    with open("output.json", "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
