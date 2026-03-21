from pydantic import BaseModel
from typing import Optional


class Shipment(BaseModel):
    id: str
    product_line: Optional[str] = None
    origin_port_code: Optional[str] = None
    origin_port_name: Optional[str] = None
    destination_port_code: Optional[str] = None
    destination_port_name: Optional[str] = None
    incoterm: Optional[str] = None
    cargo_weight_kg: Optional[float] = None
    cargo_cbm: Optional[float] = None
    is_dangerous: bool = False





