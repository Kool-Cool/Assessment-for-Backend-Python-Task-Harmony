prompt_v6 = """
Extract shipment details from the email.

Return ONLY valid JSON. No explanation.

Rules:
- Use exact text where possible
- If missing → null
- All keys MUST be present
- Do NOT guess or infer values

Ports:
- Extract from patterns like "A→B", "POL", "POD"
- Use the SAME route pair for origin and destination
- Ports must appear in the text
- Do NOT substitute with similar ports
- If abbreviation is clear (e.g., SHA, MAA), map to standard code
- If unclear → return null

Dangerous goods:
- true if DG, dangerous, hazardous, IMO, IMDG, Class
- false if non-DG, non-hazardous
- else false

Schema:
{
  "origin_port": string | null,
  "destination_port": string | null,
  "incoterm_text": string | null,
  "cargo_weight_text": string | null,
  "cargo_cbm_text": string | null,
  "goods_description": string | null,
  "is_dangerous_hint": boolean
}
"""
















prompt_v4 = """
Extract shipment details from the email.
STRICT INSTRUCTIONS:
- Return ONLY valid JSON
- No explanation, no markdown, no extra text
- Extract values EXACTLY as written (do NOT normalize, convert, or infer)
- If missing → return null
- If subject and body conflict → BODY wins
IMPORTANT:
- If email contains multiple "A→B" patterns, DO NOT guess a single shipment.
- Extract ONLY the first explicit valid route pair.
- If no clean full route exists, return null for ports.
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
