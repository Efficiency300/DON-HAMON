from langchain.memory import ConversationBufferWindowMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Сохранение истории для каждой сессии
store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Возвращает историю сообщений для заданного session_id."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

# Создание цепочки с историей сообщений
chain = RunnableWithMessageHistory(llm, get_session_history)

def chat(session_id: str, user_input: str) -> str:
    """
    Обработка сообщений пользователя в рамках определенной сессии.
:param session_id: Уникальный идентификатор сессии.
:param user_input: Сообщение пользователя.
:return: Ответ от модели.
    """
    # Отправляем сообщение в цепочку
    response = chain.invoke(
        user_input,
        config={"configurable": {"session_id": session_id}},
    )
    return response

# Пример работы бесконечного диалога
if __name__ == "__main__":
    session_id = "1"  # Уникальный ID сессии
    print("Начало чата. Напишите 'выход', чтобы завершить.")
    while True:
        print(store)
        user_input = input("Вы: ")
        if user_input.lower() == "выход":
            print("Чат завершен.")
            break
        bot_response = chat(session_id, user_input)
        print(f"Ассистент: {bot_response}")
