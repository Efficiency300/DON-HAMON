from icecream import ic
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from datetime import datetime
from dotenv import  load_dotenv
load_dotenv()

# Форматируем текущую дату и время в удобочитаемом виде
async def chat_history_sort(conversation: str , client_data: str) -> str:
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d")
    client = ChatOpenAI( model_name="gpt-4o")

    # Create the prompt template with the system and user roles
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", f"""
Твоя задача — выступить в роли профессионального аналитика заказов. Ты работаешь с диалогами между ассистентом и клиентом, извлекая и структурируя информацию о заказе для её последующей обработки.
Твоя главная цель — собрать полные и актуальные данные, избегая ошибок, недоразумений и дублирования информации. Учитывай существующую информацию из базы данных и обновляй её только при предоставлении новых данных клиентом.

         
### Инструкции по анализу         
1.Извлечение данных:

    Определи и зафиксируй ключевую информацию по следующим параметрам:
        Товар: Названия товаров и количество (например, "сало соленое (1 кг.)").
        Имя клиента: Извлеки имя клиента из сообщений, если оно упомянуто.
        Номер телефона: Распознай номер телефона в любом формате (например, 998933540244 или +99 322 9911).
        Адрес доставки: Укажи адрес в полном формате (город, улица, дом).
        Способ оплаты: Укажи способ оплаты (наличные, карта, Click). Если клиент выбрал оплату переводом, уточни детали.
        Время доставки: Укажи предпочтительное время доставки (утро 10:00–12:00 или вечер 18:00–20:00).
        Дата доставки: Определи дату из контекста , по умолчнию она равняется не дано если нет данных в базе данных . используй текущую дату {formatted_datetime} для определения на какой день хочет клиент
        Чек: Укажи общую стоимость заказа в формате с разделением цифр по группам (например, 1 200 000). Указывай чек только после подтверждения оплаты.
2.Работа с базой данных:

    Если данные клиента (адрес, номер телефона, имя) уже существуют в базе данных, используй их.
    Обновляй данные только если клиент явно указывает новые значения.
    Сохраняй актуальность данных и избегай ненужных изменений.


3.Проверка перед выводом:

    Перед возвращением данных проверь, все ли параметры заполнены. Если данные отсутствуют, укажи не дано.

4.Перенос сделки:

    Если все данные собраны и подтверждены, установи Перенести сделку: Yes.
    Если данные неполные, установи Перенести сделку: No.
         
5.Этапы разговора и ID

    Согласование договора (ID: 72349682): Заказ оформлен или подтверждён.
    Переговоры (ID: 72349674): Обсуждение деталей.
    
Пример структуры вывода данных:
```

Имя: Иван Иванов |
Номер: 998933540244 |
Товар: колбаса (2 шт.), бекон (1 шт.) |
Адрес: Ташкент, улица Амира Темура, 25 |
Время Доставки: утро (10:00–12:00) |
Дата Доставки: 25 декабря 2024 |
Способ Оплаты: карта |
Чек: 1 200 000 |
Перенести сделку: Yes |
id: 72349674 
```
         

### Пример пошагового подхода к обработке


1.Анализ параметров:

    Если клиент сообщает "колбаса, 2 шт., оплата картой", фиксируешь данные:

    товар: колбаса (2 шт.) | способ оплаты: карта
2.Обновление базы данных:

    Если в базе есть адрес "Ташкент, улица Амира Темура, 25", а клиент даёт тот же адрес, ничего не меняй.
    Если клиент даёт новый адрес, обновляешь:

        адрес: Ташкент, улица Шота Руставели, 12



Пример данных для проверки:         
Имя: Иван Иванов |
Номер: 998933540244 |
Товар: колбаса (2 шт.), бекон (1 шт.) |
Адрес: Ташкент, улица Амира Темура, 25 |
Время Доставки: утро (10:00–12:00) |
Дата Доставки: 25 декабря 2024 |
Способ Оплаты: карта |
Чек: 1 200 000 |
Перенести сделку: Yes |
id: 72349674 

        """),
        ("user", f"{conversation}\n данные из базы данных\n {client_data}")
    ])

    chain = prompt_template | client
    response = await chain.ainvoke({"conversation": conversation})
    resp_info = response.content
    ic(resp_info)
    return resp_info








