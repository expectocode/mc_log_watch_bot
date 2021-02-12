#!/usr/bin/env python3
import asyncio
from asyncio import subprocess
import re
import os
import sys

from telethon import TelegramClient, events

JOINLEAVE = re.compile(r'.(........)...Server thread/INFO\]: (\w+) (joined|left) the game')

async def main():
    token = os.environ["bot_token"]
    tg_group = int(os.environ["chat_id"])
    server_name = os.environ["server_name"]

    bot = TelegramClient('minecraftlogbot', 1, "b6b154c3707471f5339bd661645ed3d6")
    await bot.start(bot_token=token)

    tg_group = await bot.get_input_entity(tg_group)
    print("bot starting", file=sys.stderr)
    await bot.send_message(tg_group, "bot starting")

    logs = await asyncio.create_subprocess_exec("./log_watch.py", stdout=subprocess.PIPE)

    async for line in logs.stdout:
        line = line.decode()
        if match := re.match(JOINLEAVE, line):
            time, user, action = match.groups()
            print(time, user, action)
            await bot.send_message(
                tg_group,
                f'{user} {action} {server_name} ({time})'
            )


if __name__ == '__main__':
    asyncio.run(main())
