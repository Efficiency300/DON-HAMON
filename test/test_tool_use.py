import aiohttp
from config.config import Config
from status_crm.change_stage import change_stage


async def update_field_number(lead_id: str, response_text: str) -> None:
    url = f"{Config.URL}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        data = {
            'custom_fields_values': [
                {'field_id': 1000059, 'values': [{'value': number}]}

            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

    except Exception as e:
        print(f"Error in change_status: {e}")


async def update_field_goods(lead_id: str, response_text: str) -> None:
    url = f"{Config.URL}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        data = {
            'custom_fields_values': [
                {'field_id': 1000061, 'values': [{'value': goods}]}

            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

    except Exception as e:
        print(f"Error in change_status: {e}")

async def update_field_address(lead_id: str, response_text: str) -> None:
    url = f"{Config.URL}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        data = {
            'custom_fields_values': [
                {'field_id': 1000063, 'values': [{'value': address}]}

            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

    except Exception as e:
        print(f"Error in change_status: {e}")

async def update_field_delivery_time(lead_id: str, response_text: str) -> None:
    url = f"{Config.URL}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        data = {
            'custom_fields_values': [
                {'field_id': 1000065, 'values': [{'value': delivery_time}]}

            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

    except Exception as e:
        print(f"Error in change_status: {e}")


async def update_field_delivery_date(lead_id: str, response_text: str) -> None:
    url = f"{Config.URL}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        data = {
            'custom_fields_values': [
                {'field_id': 1000067, 'values': [{'value': delivery_date}]}

            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

    except Exception as e:
        print(f"Error in change_status: {e}")


async def update_field_pay_type(lead_id: str, response_text: str) -> None:
    url = f"{Config.URL}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        data = {
            'custom_fields_values': [
                {'field_id': 1000069, 'values': [{'value': pay_type}]}

            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

    except Exception as e:
        print(f"Error in change_status: {e}")


async def update_field_price(lead_id: str, response_text: str) -> None:
    url = f"{Config.URL}/{lead_id}"
    headers = {
        'Authorization': Config.SEND_ID,
        'Content-Type': 'application/json'
    }

    try:
        data = {
            'custom_fields_values': [
                {'field_id': 1000071, 'values': [{'value': price}]}

            ]
        }


        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    print("Custom fields successfully updated.")
                else:
                    print(f"Error updating custom fields: {response.status}")
                    print(await response.json())

    except Exception as e:
        print(f"Error in change_status: {e}")