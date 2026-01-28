from typing import Optional, List
from pydantic import BaseModel, Field

class LLMExtraction(BaseModel):
    origin_port_raw: Optional[str] = Field(
        None, description="Raw origin port as mentioned in the email"
    )
    destination_port_raw: Optional[str] = Field(
        None, description="Raw destination port as mentioned in the email"
    )

    incoterm_raw: Optional[str] = Field(
        None, description="Incoterm mentioned in the email, may be ambiguous"
    )

    cargo_weight_value: Optional[float] = Field(
        None, description="Numeric weight value if mentioned"
    )
    cargo_weight_unit: Optional[str] = Field(
        None, description="Weight unit (kg, lbs, tonnes, mt)"
    )

    cargo_cbm_value: Optional[float] = Field(
        None, description="Cargo volume in CBM if mentioned"
    )

    dangerous_goods_mentions: List[str] = Field(
        default_factory=list,
        description="Keywords indicating dangerous goods, if any"
    )

class ShipmentExtraction(BaseModel):
    id: str

    product_line: Optional[str]

    origin_port_code: Optional[str]
    origin_port_name: Optional[str]

    destination_port_code: Optional[str]
    destination_port_name: Optional[str]

    incoterm: Optional[str]

    cargo_weight_kg: Optional[float]
    cargo_cbm: Optional[float]

    is_dangerous: bool
