import discord
import json
from time import sleep

class MyClient(discord.Client):
    async def on_message(self, message):
        if message.content.startswith('/tetris'):
            tetris = Tetris(self, message)
            await tetris.gameloop()

class Tetris():

    background = []
    for r in range(18):
        background.append([])
        if r == 0 or r == 17:
            background[r] = [1]*12
        else:
            background[r] = [0]*12
            background[r][0] = 1
            background[r][11] = 1

    def __init__(self, client, message):
        self.client = client
        self.player = message.author
        self.channel = message.channel
    
    async def gameloop(self):
        self.fixed_pos = []
        self.time = 0
        await self.base_field()
        await self.mino_set()
        field = await self.channel.send(await self.draw_field())
        for e in ['◀','▶']:
            await field.add_reaction(e)
        while True:
            self.pos = [x[:] for x in Tetris.background]
            await self.timer()
            await self.base_field()
            await self.mino_fall()
            await field.edit(content=await self.draw_field())
            sleep(1)

    async def base_field(self):
        self.pos = [x[:] for x in Tetris.background]
        for b in self.fixed_pos:
            self.pos[b[0]][b[1]] = 3

    async def timer(self):
        self.time += 1

    async def mino_set(self):
        self.mino_type = 'I'
        self.mino_center = [1,5]

    async def mino_fall(self):
        cr = self.mino_center[0]
        cc = self.mino_center[1]
        if self.mino_type == 'I':
            minopos = [[cr,cc-1],[cr,cc],[cr,cc+1],[cr,cc+2]]
        n = 0
        for b in range(4):
            br = minopos[b][0]
            bc = minopos[b][1]
            if self.pos[br+1][bc] == 1 or self.pos[br+1][bc] == 3:
                n = 3
                for i in minopos:
                    self.fixed_pos.append(i)
                await self.mino_set()
                break
            else:
                n = 2
        for b in range(4):
            br = minopos[b][0]
            bc = minopos[b][1]
            self.pos[br][bc] = n
        if n == 2:
            self.mino_center[0] += 1

    async def draw_field(self):
        field_msg = 'Time:{}\n'.format(str(self.time))
        for r in range(18):
            row = ''
            for c in range(12):
                if self.pos[r][c] == 0:
                    b = '　'
                elif self.pos[r][c] == 1:
                    b = '■'
                elif self.pos[r][c] == 2:
                    b = '□'
                elif self.pos[r][c] == 3:
                    b = '〇'
                row += b
            row += '\n'
            field_msg += row
        return field_msg

with open('key.json', 'r') as f:
    token = json.load(f)['token']
MyClient().run(token)