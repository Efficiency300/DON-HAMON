from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from services.promt import promt

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка переменных окружения
load_dotenv()


# Определение инструментов
def get_current_time(*args, **kwargs):
    import datetime
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Инструмент 'Time' вызван. Возвращает: {current_time}")
    return {"tool_name": "Time", "value": current_time}  # Возвращаем словарь

def get_client_name(*args, **kwargs):
    client_name = kwargs.get('get_name', args[0] if args else "Неизвестный клиент")  # Берём из args или kwargs
    logging.info(f"Инструмент 'get_name' вызван. Возвращает: {client_name}")
    return {"tool_name": "get_name", "value": client_name}

def get_client_number(*args, **kwargs):
    client_name = kwargs.get('get_number', args[0] if args else "Неизвестный клиент")  # Берём из args или kwargs
    logging.info(f"Инструмент 'get_number' вызван. Возвращает: {client_name}")
    return {"tool_name": "get_number", "value": client_name}

def get_goods_list(*args, **kwargs):
    client_name = kwargs.get('get_goods', args[0] if args else "Неизвестный клиент")  # Берём из args или kwargs
    logging.info(f"Инструмент 'get_goods' вызван. Возвращает: {client_name}")
    return {"tool_name": "get_goods", "value": client_name}

def get_client_address(*args, **kwargs):
    client_name = kwargs.get('get_address', args[0] if args else "Неизвестный клиент")  # Берём из args или kwargs
    logging.info(f"Инструмент 'get_address' вызван. Возвращает: {client_name}")
    return {"tool_name": "get_address", "value": client_name}
def get_current_date(*args, **kwargs):
    client_name = kwargs.get('get_date', args[0] if args else "Неизвестный клиент")  # Берём из args или kwargs
    logging.info(f"Инструмент 'get_date' вызван. Возвращает: {client_name}")
    return {"tool_name": "get_date", "value": client_name}
def get_payment_check(*args, **kwargs):
    client_name = kwargs.get('get_check', args[0] if args else "Неизвестный клиент")  # Берём из args или kwargs
    logging.info(f"Инструмент 'get_check' вызван. Возвращает: {client_name}")
    return {"tool_name": "get_check", "value": client_name}

tools = [
    Tool(
        name="get_name",
        func=get_client_name,
        description="Используйте, чтобы получить имя клиента, когда он его называет."
    ),
    Tool(
        name="get_number",
        func=get_client_number,
        description="Используйте, чтобы получить номер телефона клиента, если он его предоставляет."
    ),
    Tool(
        name="get_goods",
        func=get_goods_list,
        description="Используйте, чтобы получить список товаров, если клиент их запрашивает или упоминает."
    ),
    Tool(
        name="get_address",
        func=get_client_address,
        description="Используйте, чтобы получить адрес клиента, если он предоставляет его."
    ),
    Tool(
        name="get_time",
        func=get_current_time,
        description="Используйте, чтобы получить текущее время в заданной временной зоне."
    ),
    Tool(
        name="get_date",
        func=get_current_date,
        description="Используйте, чтобы ответить на запросы, связанные с текущей датой."
    ),
    Tool(
        name="get_check",
        func=get_payment_check,
        description="Используйте, чтобы получить подтверждение оплаты или данные о чеке, если это запрашивается."
    ),
]



# Инициализация языковой модели
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Настройка памяти
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
print(f"memory={memory}")
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(
        content=promt),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)



agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True  # Включение подробного вывода
)



print("Чат-бот запущен. Введите 'выход' для завершения.")
while True:
    user_input = input("Пользователь: ")
    if user_input.lower() == "выход":
        print("Бот: До свидания!")
        break

    response = agent_executor.invoke({"input": user_input})
    print(f"memory={memory}")
