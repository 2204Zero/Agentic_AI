import requests
import json
import re

def extract_json(text: str):
    try:
        # Direct parse attempt
        return json.loads(text)
    except:
        pass

    # Try extracting JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    return {
        "error": "Could not extract JSON",
        "raw_output": text
    }
async def call_llm(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]