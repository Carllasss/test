import logging

from app.utils.ai.filter import filter_products, build_products_context
from app.utils.ai.llm import classify_question_ollama, generate_answer_ollama
from app.config.settings import settings
from app.utils.ai.sheets import  get_sheet_all_values, get_sheet_all_data

sheet_url = settings.SHEET_DOC_ID
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

async def ask_questioin(msg: str):

    category = classify_question_ollama(msg)
    if category == 'general':
        data = get_sheet_all_values(sheet_url, 'Общая информация о компании')
        logger.debug(data)
    elif category == 'product':
        data = get_sheet_all_data(sheet_url, 'Товары')
        # Попытка уменьшить контекст для иишки
        # Модель слишком маленкая для обработки полного списка товаров
        filtered = filter_products(data, msg)

        if not filtered:
            return {"answer": "Я не нашёл такой товар в каталоге."}

        data = build_products_context(filtered)

    else:
        return {'answer': 'Не удалось определить категорию'}


    logger.debug(data)
    answer = generate_answer_ollama(data, msg)

    return {"answer": answer}
