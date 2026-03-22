from groq import Groq
import os
from dotenv import load_dotenv
import json, time, os
from pprint import pprint


load_dotenv()
api_key=os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
model=os.getenv("model","llama-3.3-70b-versatile")


def call_llm(email, prompt , retries=3):
    prompt_with_email = f"{prompt}\n\nSubject: {email['subject']}\nBody: {email['body']}"
    # print("\n\nPrompt sent to LLM:\n", prompt_with_email)
    
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_with_email}],
                temperature=0
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"\nAttempt {attempt+1} failed:")
            print(type(e).__name__, "-", e)
            wait = 2 ** attempt
            time.sleep(wait)
    raise RuntimeError("LLM call failed after retries")