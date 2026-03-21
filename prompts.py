prompt_v3 = """
Extract shipment details from the email.

STRICT INSTRUCTIONS:
- Return ONLY valid JSON
- No explanation, no markdown, no extra text
- Extract values EXACTLY as written (do NOT normalize, convert, or infer)
- If missing → return null
- Extract FIRST shipment only
- If subject and body conflict → BODY wins

DO NOT:
- Do NOT convert units
- Do NOT assign product_line
- Do NOT map port codes
- Do NOT normalize incoterms
- Do NOT round numbers

OUTPUT SCHEMA:
{
  "origin_port": string,
  "destination_port": string,
  "incoterm_text": string,
  "cargo_weight_text": string,
  "cargo_cbm_text": string,
  "goods_description": string,
  "is_dangerous_hint": boolean
}

DANGEROUS GOODS:
- true if text contains: DG, dangerous, hazardous, IMO, IMDG, Class + number
- false if contains: non-DG, non-hazardous, not dangerous
- else false


"""
