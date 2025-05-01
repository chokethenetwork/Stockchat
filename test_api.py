import requests

api_key = "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"
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://localhost:8501",
    "Content-Type": "application/json"
}

# Dairy farming specific prompt about mastitis
messages = [
    {"role": "system", "content": "You are a knowledgeable dairy farming assistant. Provide clear, practical advice about livestock health and management."},
    {"role": "user", "content": "How should I treat a cow with mastitis? What are the steps and precautions?"}
]

data = {
    "model": "openchat/openchat-7b",  # Changed to OpenChat model which is free
    "messages": messages,
    "temperature": 0.7,
    "max_tokens": 500
}

try:
    print("Sending request to OpenRouter API...")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ API Connection Successful!")
        print("Model Used:", result.get('model', 'Not specified'))
        print("Total Tokens:", result.get('usage', {}).get('total_tokens', 'Not specified'))
        print("\n=== Mastitis Treatment Advice ===")
        print(result['choices'][0]['message']['content'])
        print("\n=== Response Details ===")
        print(f"Response Time: {response.elapsed.total_seconds():.2f} seconds")
    else:
        print(f"❌ Error {response.status_code}")
        print("Error Details:", response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Network Error: {str(e)}")
except Exception as e:
    print(f"❌ Unexpected Error: {str(e)}")