from app.utils.ai.llm import classify_question_ollama, generate_answer_ollama
from app.config.settings import settings
from app.utils.ai.sheets import get_sheet

sheet_url = settings.SHEET_DOC_ID

async def ask_questioin(msg: str):

    category = classify_question_ollama(msg)
    if category == 'general':
        data = get_sheet(sheet_url, "Общая информация о компании")
    elif category == 'product':
        data = get_sheet(sheet_url, 'Товары')
    else:
        return {'answer': 'Не удалось определить категорию'}

    context = "\n".join([f"{row}" for row in data])
    answer = generate_answer_ollama(context, msg)

    return {"answer": answer}
