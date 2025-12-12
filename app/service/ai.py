from app.utils.ai.engine import ask_questioin

async def answer_user_message(text: str) -> str:
    return await ask_questioin(text)