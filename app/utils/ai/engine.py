import logging

from app.utils.ai.filter import build_products_context
from app.utils.ai.llm import classify_question_ollama, generate_answer_ollama
from app.config.settings import settings
from app.utils.ai.sheets import  get_sheet_all_values, get_sheet_all_data

sheet_url = settings.SHEET_DOC_ID
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def ask_questioin(msg: str) -> str:

    category = classify_question_ollama(msg)
    if category == 'general' or category == 'general.':
        data = get_sheet_all_values(sheet_url, 'Общая информация о компании')
    elif category == 'product' or category == 'product.':
        data = get_sheet_all_data(sheet_url, 'Товары')
        # Передаём все товары в LLM для поиска по всей информации
        data = build_products_context(data)
        logger.debug(data)
    else:
        return "Не удалось определить категорию"


    answer = generate_answer_ollama(data, msg)

    # Возвращаем только текст ответа, без обёртки в словарь
    return answer
