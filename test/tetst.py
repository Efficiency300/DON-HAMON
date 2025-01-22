from amocrm.v2 import tokens, Lead
from amocrm.v2.exceptions import AmoApiException

# Настройка параметров клиента для получения токенов
tokens.default_token_manager(
    client_id="935d48d1-c878-437c-bac1-fe5864252f02",  # Замените на ваш client_id
    client_secret="AnG9PFlqyPnpaaSYHYyT8tQIGyi4tsFYhgvSpfHw4SthkFfrs0tL4KU8ndp0lrcR",
    # Замените на ваш client_secret
    subdomain="infowelloiluz",  # Замените на ваш subdomain
    redirect_url="https://donhamon.ru",  # Замените на ваш redirect_url
    storage=tokens.FileTokensStorage()  # Хранение токенов в файле
)

# Инициализация токенов с кодом авторизации (выполните это один раз)
tokens.default_token_manager.init(
    code="def50200f19063f1e0e627a569dff8155dd1e7ebf0f11e2f93f4e8818a95f519bb1b0477e484d4e6987876b81af06ccaf3a2c4a1d2ef3a41c0dfd674dd8bb426a0e7c2e2cd5aad750a81fb6eac145c220576990aaa2f36ec124fd20c183f610a96c7e4363f26102c2e4136f60e209dab224103a2eceb4ff864b855495a2597a06164b150ae80561a90876c320bb0ac4febe1fbfba713ceff7e108cccc63a1d2d67178cbd2f5ad37affe5391e9f4bd4abe31afb34adce939087879d99af328d3315079906d6967fa9227a2278f4fef942e14a65a5070147e28ec6e25c429a09669d11381469e4abe7dc78a35325f9b664c08f48725eee19f2a13a8f9108f5ab2d0e8ac91d6cef915e68fec8845482db5f2e79655c61ea2bc96aacc9e0833e51c56448b2930dbeaecb67e9c935c63dd01ac779814fbf613ecf9bc47db90ab711a9373c8b50df4410dcc5fbcde154fa7a33e89df3c436bb2b2d27d63e31b9e83776f389010a9d78c58ee066ffe424b169d0e44fc8cf3cecae66d45097665d83d12242aed8ce151593ac78bd3d64985c998f06b20215b4143eedf25745b85a3a07c98a82febfb062dac33b7b300e12ef8ea6a66ccef89c564e15859f53e5affb2ed5c22d2b2f7df286eb727779d06a0aa919fa2adc10644ff85f28d1a53e9a3f14eee66c226b",
    skip_error=True
)




from amocrm.v2 import tokens, Pipeline

# Получение всех воронок (pipelines) и их статусов (statuses)
pipelines = Pipeline.objects.all()  # получение всех воронок

for pipeline in pipelines:
    print(f"Воронка: {pipeline.name} (ID: {pipeline.id})")

    # Получаем статусы, связанные с данной воронкой
    statuses = pipeline.statuses  # это уже список
    for status in statuses:
        print(f" - Статус: {status.name} (ID: {status.id})")
        