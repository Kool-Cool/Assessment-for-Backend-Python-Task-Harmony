import json, time, os
from groq import Groq
from dotenv import load_dotenv
from pprint import pprint
import re
from datetime import datetime

from schemas import Shipment
from groq_setup import call_llm
from prompts import prompt_v3
from port_resolve import PortResolver




""" 
Business Rules:
"""
PORTCODE_JSON = "./port_codes_reference.json"
EMAIL_INPUT_JSON = "./emails_input.json"
VALID_INCOTERMS = {"FOB","CIF","CFR","EXW","DDP","DAP","FCA","CPT","CIP","DPU"}

ordered_keys = [
    "id",
    "product_line",
    "incoterm",
    "origin_port_code",
    "origin_port_name",
    "destination_port_code",
    "destination_port_name",
    "cargo_weight_kg",
    "cargo_cbm",
    "is_dangerous"
]




def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found")


def assign_product_line(origin_code, destination_code):

    if destination_code and destination_code.upper().startswith("IN"):
        return "pl_sea_import_lcl"
    if origin_code and origin_code.upper().startswith("IN"):
        return "pl_sea_export_lcl"
    return None

    # if destination_code and destination_code.startswith("IN"):
    #     return "pl_sea_import_lcl"
    # elif origin_code and origin_code.startswith("IN"):
    #     return "pl_sea_export_lcl"
    # return None


def normalize_incoterm(incoterm_text):
    if not incoterm_text:
        return "FOB"
    incoterm = incoterm_text.strip().upper()
    if incoterm in VALID_INCOTERMS:
        return incoterm
    # ambiguous like "FOB or CIF" → default to FOB
    if "FOB" in incoterm_text.upper():
        return "FOB"
    return "FOB"


def detect_dangerous(text):
    text_lower = text.lower()
    negations = ["non-hazardous","non hazardous","non-dg","not dangerous"]
    if any(n in text_lower for n in negations):
        return False
    keywords = ["dg","dangerous","hazardous","imo","imdg"]
    if any(k in text_lower for k in keywords):
        return True
    if re.search(r"class\s*\d+", text_lower):
        return True
    return False


def resolve_conflict(subject_value, body_value):
    return body_value if body_value else subject_value


# def normalize_weight(weight_text):
#     if not weight_text or weight_text.lower() in ["tbd","n/a","to be confirmed"]:
#         return None
#     if "lbs" in weight_text.lower():
#         num = float(re.findall(r"\d+\.?\d*", weight_text)[0])
#         return round(num * 0.453592, 2)
#     if "mt" in weight_text.lower() or "tonne" in weight_text.lower():
#         num = float(re.findall(r"\d+\.?\d*", weight_text)[0])
#         return round(num * 1000, 2)
#     if "kg" in weight_text.lower():
#         num = float(re.findall(r"\d+\.?\d*", weight_text)[0])
#         return round(num, 2)
#     return None


def normalize_weight(weight_text):
    if not weight_text:
        return None

    text = weight_text.lower()

    if text in ["tbd", "n/a", "to be confirmed"]:
        return None

    # ✅ extract full number including commas
    match = re.search(r"[\d,]+\.?\d*", text)
    if not match:
        return None

    num = float(match.group().replace(",", ""))

    if "lbs" in text:
        return round(num * 0.453592, 2)

    if "mt" in text or "tonne" in text:
        return round(num * 1000, 2)

    if "kg" in text:
        return round(num, 2)

    return None


def normalize_cbm(cbm_text):
    if not cbm_text or cbm_text.lower() in ["tbd","n/a","to be confirmed"]:
        return None
    num = float(re.findall(r"\d+\.?\d*", cbm_text)[0])
    return round(num, 2)



with open(PORTCODE_JSON,encoding="utf-8") as f:
    port_data = json.load(f)

ports = {p["name"].lower(): p["code"] for p in port_data}
code_to_name = {p["code"]: p["name"] for p in port_data}

resolver = PortResolver(port_data)

def map_port(port_text):
    if not port_text:
        return None, None

    port_text = port_text.lower().strip()

    #Exact match first
    if port_text in ports:
        code = ports[port_text]
        return code, code_to_name[code]

    #Word-based match (safer than substring)
    for name, code in ports.items():
        if port_text == name:
            return code, code_to_name[code]

    #Fallback: contains full word
    for name, code in ports.items():
        if name in port_text.split():
            return code, code_to_name[code]

    return None, None




def enforce_rules(email, llm_output):
    subj, body = email["subject"], email["body"]


    # origin_code, origin_name = map_port(llm_output.get("origin_port"))
    # dest_code, dest_name = map_port(llm_output.get("destination_port"))

    origin_code, origin_name = resolver.resolve(
        llm_output.get("origin_port"),
        context_role="origin"
    )

    dest_code, dest_name = resolver.resolve(
        llm_output.get("destination_port"),
        context_role="destination"
    )
    product_line = assign_product_line(origin_code, dest_code)

    incoterm = normalize_incoterm(
        resolve_conflict(llm_output.get("incoterm_text"),
        llm_output.get("incoterm_from_body")))

    weight = normalize_weight(llm_output.get("cargo_weight_text"))
    cbm = normalize_cbm(llm_output.get("cargo_cbm_text"))

    dangerous = detect_dangerous(subj + " " + body)

    return {
        "id": email["id"],
        "product_line": product_line,
        "origin_port_code": origin_code,
        "origin_port_name": origin_name,
        "destination_port_code": dest_code,
        "destination_port_name": dest_name,
        "incoterm": incoterm,
        "cargo_weight_kg": weight,
        "cargo_cbm": cbm,
        "is_dangerous": dangerous
    }









def process_emails():
    with open(EMAIL_INPUT_JSON) as f:
        emails = json.load(f)
    print(f"Processing {len(emails)} emails...")

    results = []
    for email in emails:
        raw = call_llm(email=email, prompt=prompt_v3)
        try:
            llm_dict = extract_json(raw)            
            shipment_dict = enforce_rules(email, llm_dict)
            shipment = Shipment(**shipment_dict)
            # results.append(shipment.dict())
            ordered_dict = {k: getattr(shipment, k, None) for k in ordered_keys}
            results.append(ordered_dict)

        except Exception:
            # results.append(Shipment(id=email["id"], is_dangerous=False).dict())
            fallback = Shipment(id=email["id"], is_dangerous=False)
            ordered_dict = {k: getattr(fallback, k, None) for k in ordered_keys}
            results.append(ordered_dict)

    # Create timestamped filename
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"extract/output_{ts}.json"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Results written to {output_file}")




if __name__ == "__main__":
    process_emails()
