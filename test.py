import os
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

print("Key loaded:", bool(api_key))
print("Key prefix:", api_key[:10] if api_key else None)

client = ChatMistralAI(
    model="mistral-small-latest",
    api_key=api_key
)

response = client.invoke("Say hello")

print(response.content)