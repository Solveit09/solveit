
import requests

# API 키와 URL 설정
API_KEY = "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"
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# 요청 헤더
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "https://your-website.com"  # 본인의 도메인으로 수정
}

# 요청 데이터 (예: GPT-4 사용)
data = {
    "model": "openai/gpt-4",  # OpenRouter에서 지원하는 모델 이름
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "OpenRouter API에 제한이 있나요?"}
    ],
    "max_tokens": 100
}

# API 호출
response = requests.post(BASE_URL, headers=headers, json=data)

# API 응답 처리
if response.status_code == 200:
    # JSON 응답에서 content 추출
    content = response.json()["choices"][0]["message"]["content"]
    print("응답 내용:", content)
else:
    print(f"오류 발생: {response.status_code}, {response.text}")
