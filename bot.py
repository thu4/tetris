import discord
import json
from time import sleep

class MyClient(discord.Client):

    async def on_message(self, message):
        if message.content.startswith('/ping'):
            await message.channel.send('pong!')

        if message.content.startswith('/tetris'):
            tetris = Tetris(self, message)
            await tetris.start()


class Tetris():
    def __init__(self, client, message):
        self.client = client
        self.player = message.author
        self.channel = message.channel

    async def start(self):
        w = '■'
        a = '　'
        b_top = w*12
        b_mid = '\n'.join([w+a*10+w]*16)
        board = '{0}\n{1}\n{0}'.format(b_top,b_mid)
        display = await self.channel.send(board)
        await display.edit(display)


with open('key.json', 'r') as f:
    token = json.load(f)['token']
MyClient().run(token)