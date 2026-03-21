import json
from pprint import pprint

PORTCODE_JSON = "./port_codes_reference.json"

with open(PORTCODE_JSON, encoding="utf-8") as f:
    port_data = json.load(f)

    pprint(port_data)

ports = {p["name"].lower(): p["code"] for p in port_data}
pprint(ports)
code_to_name = {p["code"]: p["name"] for p in port_data}
pprint(code_to_name)



import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("GROQ_API_KEY"))
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",   # safer default
    messages=[{"role": "user", "content": "Say hello in JSON format"}],
    temperature=0
)

print(response)
print("Output:", response.choices[0].message.content)
