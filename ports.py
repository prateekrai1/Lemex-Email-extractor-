import json
import re
from typing import Optional


class PortResolver:
    def __init__(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            ports = json.load(f)

        # Normalized name → code
        self.name_to_code: dict[str, str] = {}

        # Code → canonical name (first seen wins)
        self.code_to_name: dict[str, str] = {}

        for entry in ports:
            code = entry["code"]
            name = entry["name"]

            norm_name = self._normalize(name)
            self.name_to_code[norm_name] = code

            if code not in self.code_to_name:
                self.code_to_name[code] = name

        # High-value hard aliases (derived from dataset)
        self.aliases = {
            # Chennai / India
            "maa": "INMAA",
            "chennai": "INMAA",
            "chennai port": "INMAA",
            "chennai icd": "INMAA",
            "india": "INMAA",
            "india chennai": "INMAA",

            # Bangalore / ICD
            "blr": "INBLR",
            "bangalore": "INBLR",
            "icd bangalore": "INBLR",
            "bangalore icd": "INBLR",

            # Hyderabad
            "hyd": "INHYD",
            "hyderabad": "INHYD",
            "icd hyderabad": "INHYD",

            # Shanghai
            "sha": "CNSHA",
            "shanghai": "CNSHA",

            # Singapore
            "sin": "SGSIN",
            "singapore": "SGSIN",

            # Hong Kong
            "hkg": "HKHKG",
            "hong kong": "HKHKG",

            # Jebel Ali
            "jbl": "AEJEA",
            "jebel ali": "AEJEA",

            # Bangkok
            "bkk": "THBKK",
            "bangkok": "THBKK",
            "bangkok icd": "THBKK",

            # Xingang / Tianjin
            "xingang": "CNTXG",
            "tianjin": "CNTXG",

            # Shenzhen / Guangzhou
            "shenzhen": "CNSZX",
            "guangzhou": "CNGZG",

            # Busan
            "pus": "KRPUS",
            "busan": "KRPUS",

            # Ho Chi Minh
            "hcm": "VNSGN",
            "hochiminh": "VNSGN",
            "ho chi minh": "VNSGN",

            # Yokohama
            "yok": "JPYOK",
            "yokohama": "JPYOK",

            # Osaka
            "osa": "JPOSA",
            "osaka": "JPOSA",

            # Izmir / Ambarli
            "izmir": "TRIZM",
            "ambarli": "TRAMR",

            # Genoa
            "genoa": "ITGOA",

            # Qingdao
            "qingdao": "CNQIN",

            # Surabaya
            "sub": "IDSUB",
            "surabaya": "IDSUB",

            # Port Klang
            "port klang": "MYPKG",
            "pkg": "MYPKG",

            # Cape Town
            "cpt": "ZACPT",

            # Houston / USA
            "hou": "USHOU",
            "houston": "USHOU",
            "lax": "USLAX",
            "los angeles": "USLAX",
        }

    # -----------------------
    # Public API
    # -----------------------
    def resolve(self, raw_name: Optional[str]) -> Optional[str]:
        """
        Resolve raw port text → UN/LOCODE
        """
        if not raw_name:
            return None

        key = self._normalize(raw_name)

        # 1️⃣ Exact alias match
        if key in self.aliases:
            return self.aliases[key]

        # 2️⃣ Exact normalized name match
        if key in self.name_to_code:
            return self.name_to_code[key]

        # 3️⃣ Substring match (very important)
        for name_key, code in self.name_to_code.items():
            if name_key in key:
                return code

        # 4️⃣ India fallback
        if any(k in key for k in ["india", "chennai", "maa", "icd"]):
            return "INMAA"

        return None

    def get_name(self, code: Optional[str]) -> Optional[str]:
        """
        Resolve UN/LOCODE → canonical port name
        """
        if not code:
            return None
        return self.code_to_name.get(code)

    # -----------------------
    # Internal helpers
    # -----------------------
    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"\(.*?\)", "", text)  # remove parentheses
        text = text.replace("→", " ")
        text = text.replace("/", " ")
        text = text.replace("-", " ")
        text = text.replace(",", " ")
        text = text.replace("via", " ")
        text = text.replace("icd", "")
        text = re.sub(r"\s+", " ", text)
        return text.strip()
