import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Say 'Gemini key works' and nothing else.")
print("GEMINI:", response.text)

from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Say 'Groq key works' and nothing else."}]
)
print("GROQ:", completion.choices[0].message.content)