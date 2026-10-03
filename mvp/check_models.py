"""
Check which OpenAI models are available on this account.
Run this script to see what the instructor has unlocked.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# models we care about for this project
MODELS_TO_CHECK = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4o-2024-11-20",
    "gpt-4.5-preview",
    "gpt-4.5",
    "o1",
    "o1-mini",
    "o1-preview",
    "o3-mini",
    "o3",
    "o1-pro",
]

print("Checking available OpenAI models...\n")

# list all models
try:
    all_models = client.models.list()
    available = {m.id for m in all_models.data}

    print("ALL AVAILABLE MODELS ON YOUR ACCOUNT:")
    print("=" * 50)
    for m in sorted(available):
        print(f"  {m}")

    print("\nMODELS RELEVANT FOR THIS PROJECT:")
    print("=" * 50)
    for model in MODELS_TO_CHECK:
        status = "✅ AVAILABLE" if model in available else "❌ not available"
        print(f"  {model}: {status}")

except Exception as e:
    print(f"Error: {e}")
