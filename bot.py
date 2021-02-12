#!/usr/bin/env python3
'''
Bot to send messages to a chat whenever people join or leave a Minecraft server.
'''
import asyncio
from asyncio import subprocess
import re
import os
import sys
import time
from telethon import TelegramClient

JOINLEAVE = re.compile(r'.(........)...Server thread/INFO\]: (\w+) (joined|left) the game')
REPEAT_THRESHOLD_SEC = 5 * 60

async def main():
    token = os.environ['bot_token']
    tg_group = int(os.environ['chat_id'])
    server_name = os.environ['server_name']

    bot = TelegramClient('minecraftlogbot', 1, 'b6b154c3707471f5339bd661645ed3d6')
    await bot.start(bot_token=token)

    tg_group = await bot.get_input_entity(tg_group)
    user_state = {}
    print('bot starting', file=sys.stderr)

    logs = await asyncio.create_subprocess_exec('./log_watch.py', stdout=subprocess.PIPE)

    async for line in logs.stdout:
        line = line.decode()
        if match := re.match(JOINLEAVE, line):
            event_time, user, action = match.groups()
            print(event_time, user, action, file=sys.stderr)
            now = time.monotonic()

            is_repeat = False
            if state := user_state.get(user):
                (prev_time, prev_action, prev_msg) = state
                is_repeat = (now - prev_time) < REPEAT_THRESHOLD_SEC

            if is_repeat and ((prev_action, action) == ('left', 'joined')):
                await prev_msg.delete()
            else:
                msg = await bot.send_message(
                    tg_group,
                    f'{user} {action} {server_name}'
                )
                user_state[user] = (now, action, msg)


if __name__ == '__main__':
    asyncio.run(main())
