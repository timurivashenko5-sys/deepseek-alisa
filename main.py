import os
import sys
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": user_text}],
            },
            timeout=4
        )

        # Логируем всё, что вернул DeepSeek
        print("DEEPSEEK STATUS:", response.status_code, file=sys.stderr, flush=True)
        print("DEEPSEEK BODY:", response.text, file=sys.stderr, flush=True)

        answer = response.json()["choices"][0]["message"]["content"]

    except KeyError:
        print("DEEPSEEK KEYERROR:", response.text, file=sys.stderr, flush=True)
        answer = "Ошибка: нейросеть вернула неожиданный ответ."

    except requests.exceptions.Timeout:
        print("DEEPSEEK TIMEOUT", file=sys.stderr, flush=True)
        answer = "Нейросеть не успела ответить. Попробуйте ещё раз."

    except Exception as e:
        print("DEEPSEEK EXCEPTION:", repr(e), file=sys.stderr, flush=True)
        answer = f"Ошибка: {e}"

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }
