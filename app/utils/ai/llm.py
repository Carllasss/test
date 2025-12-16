import json
import logging

import httpx

OLLAMA_HOST = "http://ollama:11434"
OLLAMA_MODEL= "llama3.2:3b"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def classify_question_ollama(question: str) -> str:
    prompt = f"""
    Ты — точный ассистент.
    Классифицируй вопрос как 'general' если общий про компанию,
    или 'product' если про товар. Ответь строго одним словом: general или product 
    Не добавляй в конце точку.
    Не добавляй знаков, точек, других слов или символов.
    Вопрос: "{question}"
    
    Правила:
    - Никогда не придумывай, не дополняй, не объясняй и не извиняйся.
    - Не добавляй пунктуацию, кроме необходимой (например, точки в конце не ставь).

    """
    url = f"{OLLAMA_HOST}/api/chat"
    data = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    try:
        with httpx.stream("POST", url, json=data, timeout=120.0) as resp:
            resp.raise_for_status()

            full_text = ""

            for line in resp.iter_lines():
                if not line.strip():
                    continue
                logger.debug(line)
                try:
                    chunk = json.loads(line)

                except json.JSONDecodeError:
                    logging.error(f"Не могу распарсить строку: {line}")
                    continue

                msg = chunk.get("message", {})
                if "content" in msg:
                    full_text += msg["content"]

            return full_text.strip().lower()

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return "Не удалось классифицировать"

    except Exception as e:
        logger.error(e)
        logging.exception("Ошибка запроса к Ollama")
        return "Не удалось классифицировать"

def generate_answer_ollama(context: str, question: str) -> str:
    prompt = f"""\
    Ты — точный ассистент по товарам и бизнесу. Тебе даны только следующие данные:

    {context}

    Ответь **строго и только** на основе этих данных на вопрос: "{question}"

    Правила:
    - Если в данных есть точный ответ — выведи его кратко и без пояснений.
    - Если данных недостаточно или ответа нет — ответь только: "Не знаю".
    - Никогда не придумывай, не дополняй, не объясняй и не извиняйся.
    - Не добавляй пунктуацию, кроме необходимой (например, точки в конце не ставь).
    - Ответ должен быть **одним предложением или фразой**, максимум — коротким перечислением.

    Ответ:"""


    logger.debug(prompt)
    url = f"{OLLAMA_HOST}/api/chat"
    data = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    try:
        with httpx.stream("POST", url, json=data, timeout=120.0) as resp:
            resp.raise_for_status()

            full_text = ""

            for line in resp.iter_lines():
                if not line.strip():
                    continue
                logger.debug(line)
                try:
                    chunk = json.loads(line)

                except json.JSONDecodeError:
                    logging.error(f"Не могу распарсить строку: {line}")
                    continue

                msg = chunk.get("message", {})
                if "content" in msg:
                    full_text += msg["content"]

            return full_text.strip().lower()

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return "Не удалось классифицировать"

