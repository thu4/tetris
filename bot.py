import discord
import json
from time import sleep

class MyClient(discord.Client):
    async def on_message(self, message):
        if message.content.startswith('/tetris'):
            tetris = Tetris(self, message)
            await tetris.gameloop()

class Tetris():

    background = {}
    for r in range(18):
        background[r] = {}
        if r == 0 or r == 17:
            for c in range(12):
                background[r][c] = '■'
        else:
            background[r][0] = '■'
            background[r][11] = '■'
            for c in range(1,11):
                background[r][c] = '　'

    def __init__(self, client, message):
        self.client = client
        self.player = message.author
        self.channel = message.channel
    
    async def gameloop(self):
        
        while True:
            await self.tetromino()
            await self.draw_field()
            sleep(0.1)

    async def tetromino(self):
        pass

    async def draw_field(self):
        field_msg = ''
        for r in range(18):
            row = ''
            for c in range(12):
                row += Tetris.background[r][c]
            row += '\n'
            field_msg += row
        self.field = await self.channel.send(field_msg)
        self.field.edit(field_msg)

with open('key.json', 'r') as f:
    token = json.load(f)['token']
MyClient().run(token)