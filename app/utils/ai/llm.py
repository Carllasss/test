import logging

import httpx

OLLAMA_HOST = "http://ollama:11434"

def classify_question_ollama(question: str) -> str:
    prompt = f"""
    Классифицируй вопрос как 'general' если общий про компанию,
    или 'product' если про товар. Вопрос: "{question}"
    """
    url = f"{OLLAMA_HOST}/v1/chat"
    data = {
        "model": "llama3.2:1b",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        result = httpx.post(url, json=data, timeout=30.0)
        result.raise_for_status()  # выбросит httpx.HTTPStatusError при 404/500
        answer = result.json()
        logging.info(answer)
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return "Не удалось классифицировать"
    except Exception as e:
        logging.exception("Ошибка запроса к Ollama")
        return "Не удалось классифицировать"
    return answer['choices'][0]['message']['content'].strip().lower()

# Генерация ответа на основе контекста
def generate_answer_ollama(context: str, question: str) -> str:
    prompt = f"""
    У тебя есть следующие данные: {context}
    Ответь на вопрос пользователя: "{question}"
    Если ответа нет в данных — скажи "Не знаю".
    """
    url = f"{OLLAMA_HOST}/v1/chat"
    data = {
        "model": "llama3.2:1b",
        "messages": [{"role": "user", "content": prompt}]
    }
    result = httpx.post(url, json=data)
    answer = result.json()
    logging.info(answer)

    logging.error(answer)
    # result = chat(model="llama2", messages=[{"role": "user", "content": prompt}], host=OLLAMA_HOST)
    return answer['choices'][0]['message']['content'].strip()
