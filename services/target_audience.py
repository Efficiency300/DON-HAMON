from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import json

load_dotenv()

async def target_audience(conversation: tuple[str, str , str]) -> dict:
    client = ChatOpenAI(model_name="gpt-4o")
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """
             Твоя задача: Выступать в роли профессионального аналитика целевой аудитории. Ты обладаешь 10-летним опытом анализа сообщений и поведения клиентов, специализируясь на выявлении интересов и потребностей в категории мясных продуктов. Ты будешь анализировать поступающие сообщения, классифицируя их на основе их содержания.
             Инструкции по анализу:

            1. Определи и зафиксируй ключевую информацию по следующим параметрам:
                Целевой клиент: Определи, интересуется ли клиент продукцией, задает ли вопросы о товарах или демонстрирует интерес к покупке.
                Сотрудничество: Проверь, предлагает ли клиент услуги или варианты сотрудничества.
                Комментарии: Заметь, если в сообщении клиента присутствуют ссылки, замечания или комментарии.


            2. Присваивай уникальный идентификатор в зависимости от этапа разговора. Используй следующую структуру:
                Целевой клиент: ({{"funnel": "9084438", "id": "73108018"}})
                Сотрудничество: ({{"funnel": "9084646", "id": "73109370"}})
                Комментарий: ({{"funnel": "9084650", "id": "73109386"}})

            3. Структура вывода данных:
                {{"funnel": "9084438", "id": "73108018"}}
         """),
        ("user", f"{conversation}")
    ])

    chain = prompt_template | client
    response = await chain.ainvoke({"conversation": conversation})
    try:
        resp_info = json.loads(response.content)
    except json.JSONDecodeError:
        raise ValueError(f"Некорректный формат ответа: {response.content}")

    return resp_info
