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
        self.pos = Tetris.background
        self.time = 0
        field = await self.channel.send(await self.draw_field())
        while True:
            self.pos = Tetris.background
            await self.timer()
            await self.mino()
            await field.edit(content=await self.draw_field())
            sleep(1)

    async def timer(self):
        self.time += 1

    async def mino(self):
        minopos = [[1,5],[2,5],[3,5],[4,5]]
        for i in range(4):
            self.pos[minopos[i][0]][minopos[i][1]] = '□'

    async def draw_field(self):
        field_msg = 'Time:{}\n'.format(str(self.time))
        for r in range(18):
            row = ''
            for c in range(12):
                row += self.pos[r][c]
            row += '\n'
            field_msg += row
        return field_msg

with open('key.json', 'r') as f:
    token = json.load(f)['token']
MyClient().run(token)