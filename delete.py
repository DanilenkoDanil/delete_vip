import configparser
import json
import asyncio

from telethon.sync import TelegramClient
from telethon import connection

# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")
message_path = 1
old_message = []


with open("setting.json", 'r', encoding='utf8') as out:
    setting = json.load(out)

    client = TelegramClient(
        setting['account']['session'],
        setting['account']['api_id'],
        setting['account']['api_hash']
    )

    client.start()
    dialogs = client.get_dialogs()

    for index, dialog in enumerate(dialogs):
        if index < 250:
            if str(dialog.id) == setting['channels']['first_channel']:
                channel = dialog


async def change_user_links_text(message: str, username: str) -> str:
    for item in message.split():
        if '@' in item:
            if not item[1].isdigit():
                message = message.replace(item, username)

    return message


async def dump_all_messages(channel):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    global message_path
    history = await client(GetHistoryRequest(
        peer=channel,
        offset_id=0,
        offset_date=None, add_offset=0,
        limit=10, max_id=0, min_id=0,
        hash=0))
    messages = list(history.messages)
    messages.reverse()
    for message in messages:
        try:
            if int(message.id) not in old_message:
                old_message.append(int(message.id))
                if "Take-Profit target" in message.message or "All take-profit" in message.message:
                    if 'Months' in message.message:
                        await client.delete_messages(channel, message_ids=[message.id])
                    time = str(message.message).split('Period: ')[1].split(' ⏰')[0]
                    days = float(time.split('Days')[0])
                    if days > 3:
                        await client.delete_messages(channel, message_ids=[message.id])
        except Exception as e:
            print(e)


async def main():
    while True:
        try:
            await dump_all_messages(channel)
            await asyncio.sleep(30)
        except Exception as e:
            print(e)
            await asyncio.sleep(300)

with client:
    client.loop.run_until_complete(main())
