import discord
import json
from time import sleep
from random import choice

class MyClient(discord.Client):

    games = []

    async def on_message(self, message):
        if message.content.startswith('/tetris'):
            if message.channel in [i.channel for i in MyClient.games]:
                await message.channel.send('このチャンネルでは既にゲームが行われています。\n別のチャンネルで開始して下さい。')
            else:
                tetris = Tetris(self, message)
                MyClient.games.append(tetris)
                await tetris.gameloop()

    async def on_reaction_add(self, reaction, user):
        if user != self.user:
            for game in MyClient.games:
                if reaction.message.channel == game.channel:
                    if user == game.player:
                        if reaction.emoji == '◀':
                            game.mino_move_distance -= 1
                            await reaction.message.remove_reaction('◀', user)
                        if reaction.emoji == '▶':
                            game.mino_move_distance += 1
                            await reaction.message.remove_reaction('▶', user)

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
        self.time = 0
        self.pos = []
        self.fixed_pos = []
        self.mino_center = []
        self.mino_move_distance = 0
        self.mino_type = ''
    
    async def gameloop(self):
        await self.base_field()
        await self.mino_set()
        field = await self.channel.send(await self.draw_field())
        for e in ['◀','▶']:
            await field.add_reaction(e)
        while True:
            self.pos = [x[:] for x in Tetris.background]
            self.timer()
            self.base_field()
            self.mino_move()
            self.mino_fall()
            await field.edit(content=self.draw_field())
            if self.is_game_over() == True:
                break
            sleep(1)
        await self.game_end()

    def base_field(self):
        self.pos = [x[:] for x in Tetris.background]
        for b in self.fixed_pos:
            self.pos[b[0]][b[1]] = 3

    def timer(self):
        self.time += 1

    def mino_set(self):
        t = ['I','O','T','J','L','S','Z']
        self.mino_type = choice(t)
        self.mino_center = [1,5]

    def row_clear(self):
        l = [x[:] for x in self.fixed_pos]
        l.sort(key=lambda x: (x[0],x[1]))
        print('[debug] {}'.format(l))
        for r in range(1,17):
            inl_f = lambda x: x in l
            rl = []
            for i in range(1,11):
                rl.append([r,i])
            if all(map(inl_f, rl)):
                for i in range(1,11):
                    self.fixed_pos.remove([r,i])
                for b in l:
                    if b[0] < r:
                        self.fixed_pos.remove([b[0],b[1]])
                        self.fixed_pos.append([b[0]+1,b[1]])
                for b in self.fixed_pos:
                    self.pos[b[0]][b[1]] = 3

    def minopos(self):
        t = self.mino_type
        cr = self.mino_center[0]
        cc = self.mino_center[1]
        if t == 'I':
            return [[cr,cc-1],[cr,cc],[cr,cc+1],[cr,cc+2]]
        if t == 'O':
            return [[cr,cc],[cr,cc+1],[cr+1,cc],[cr+1,cc+1]]
        if t == 'T':
            return [[cr,cc+1],[cr+1,cc],[cr+1,cc+1],[cr+1,cc+2]]
        if t == 'J':
            return [[cr,cc],[cr+1,cc],[cr+1,cc+1],[cr+1,cc+2]]
        if t == 'L':
            return [[cr,cc+2],[cr+1,cc],[cr+1,cc+1],[cr+1,cc+2]]
        if t == 'S':
            return [[cr,cc+1],[cr,cc+2],[cr+1,cc],[cr+1,cc+1]]
        if t == 'Z':
            return [[cr,cc],[cr,cc+1],[cr+1,cc+1],[cr+1,cc+2]]
        return []

    def mino_fall(self):
        minopos = self.minopos()
        n = 0
        for b in range(4):
            br = minopos[b][0]
            bc = minopos[b][1]
            if self.pos[br+1][bc] == 0:
                n = 2
            else:
                n = 3
                for i in minopos:
                    self.fixed_pos.append(i)
                break
        for b in range(4):
            br = minopos[b][0]
            bc = minopos[b][1]
            self.pos[br][bc] = n
        if n == 2:
            self.mino_center[0] += 1
        if n == 3:
            self.mino_set()
            self.row_clear()

    def mino_move(self):
        if self.mino_move_distance > 0:
            for i in range(self.mino_move_distance):
                minopos = self.minopos()
                rc = max([x[1] for x in minopos])
                rr = [x[0] for x in minopos if x[1] == rc][0]
                if self.pos[rr][rc+1] == 0:
                    self.mino_center[1] += 1
                break
        elif self.mino_move_distance < 0:
            for i in range(abs(self.mino_move_distance)):
                minopos = self.minopos()
                lc = min([x[1] for x in minopos])
                lr = [x[0] for x in minopos if x[1] == lc][0]
                if self.pos[lr][lc-1] == 0:
                    self.mino_center[1] -= 1
                break
        self.mino_move_distance = 0

    def draw_field(self):
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
                    b = '□'
                row += b
            row += '\n'
            field_msg += row
        return field_msg

    def is_game_over(self):
        for i in self.pos[1]:
            if i == 3:
                return True
        return False
    
    async def game_end(self):
        await self.channel.send('【ゲームオーバー】\nTime:{}'.format(self.time))
        self.client.games.remove(self)

with open('key.json', 'r') as f:
    token = json.load(f)['token']
MyClient().run(token)