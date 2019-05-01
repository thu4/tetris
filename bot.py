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
                        if reaction.emoji == '▶':
                            game.mino_move_distance += 1
                        if reaction.emoji == '⏬':
                            game.quickdrop = True
                        if reaction.emoji == '🔁':
                            game.mino_move_angle += 1

    async def on_reaction_remove(self, reaction, user):
        if user != self.user:
            for game in MyClient.games:
                if reaction.message.channel == game.channel:
                    if user == game.player:
                        if reaction.emoji == '◀':
                            game.mino_move_distance -= 1
                        if reaction.emoji == '▶':
                            game.mino_move_distance += 1
                        if reaction.emoji == '⏬':
                            game.quickdrop = True
                        if reaction.emoji == '🔁':
                            game.mino_move_angle += 1

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
        self.quickdrop = False
        self.mino_pos = []
        self.mino_type = ''
        self.mino_move_distance = 0
        self.mino_move_angle = 0
    
    async def gameloop(self):
        self.base_field()
        self.mino_set()
        field = await self.channel.send(self.draw_field())
        for e in ['◀','▶','⏬','🔁']:
            await field.add_reaction(e)
        while True:
            self.pos = [x[:] for x in Tetris.background]
            self.timer()
            self.base_field()
            self.mino_move()
            self.mino_rotate()
            self.mino_fall()
            if self.quickdrop == False:
                sleep(1)
                await field.edit(content=self.draw_field())
                self.status()
            if self.is_game_over() == True:
                break
        await self.game_end()
    
    def status(self):
        # print(self.pos)
        # print(self.fixed_pos)
        # print(self.mino_pos)
        # print(self.mino_move_distance)
        # print(self.mino_move_angle)
        # print(self.mino_type)
        pass

    def base_field(self):
        self.pos = [x[:] for x in Tetris.background]
        for b in self.fixed_pos:
            self.pos[b[0]][b[1]] = 3

    def timer(self):
        if self.quickdrop == False:
            self.time += 1

    def mino_set(self):
        tl = ['I','O','T','J','L','S','Z']
        t = choice(tl)
        self.mino_type = t
        if t == 'I':
            self.mino_pos = [[1,4],[1,5],[1,6],[1,7]]
        if t == 'O':
            self.mino_pos = [[1,5],[1,6],[2,5],[2,6]]
        if t == 'T':
            self.mino_pos = [[1,6],[2,5],[2,6],[2,7]]
        if t == 'J':
            self.mino_pos = [[1,5],[2,5],[2,6],[2,7]]
        if t == 'L':
            self.mino_pos = [[1,7],[2,5],[2,6],[2,7]]
        if t == 'S':
            self.mino_pos = [[1,6],[1,7],[2,5],[2,6]]
        if t == 'Z':
            self.mino_pos = [[1,5],[1,6],[2,6],[2,7]]
        self.quickdrop = False

    def row_clear(self):
        l = [x[:] for x in self.fixed_pos]
        l.sort(key=lambda x: (x[0],x[1]))
        for r in range(1,17):
            inl_f = lambda x: x in l
            rl = []
            for i in range(1,11):
                rl.append([r,i])
            if all(map(inl_f, rl)):
                for i in range(1,11):
                    l.remove([r,i])
                    self.pos[r][i] = 0
                fl = [x for x in l if x[0] < r]
                for b in fl:
                    l.remove([b[0],b[1]])
                    l.append([b[0]+1,b[1]])
                    self.pos[b[0]][b[1]] = 0
                self.fixed_pos = l
                for b in self.fixed_pos:
                    self.pos[b[0]][b[1]] = 3

    def mino_rotate(self):
        t = self.mino_type
        r = self.mino_move_angle
        minopos = self.mino_pos[:]
        if r > 0:
            if t == 'I':
                if r % 2 == 1:
                    minopos = [[minopos[0][0]-1,minopos[1][1]],[minopos[0][0],minopos[1][1]],[minopos[0][0]+1,minopos[1][1]],[minopos[0][0]+2,minopos[1][1]]]
            elif t == 'O':
                pass
            else:
                lc = min([x[1] for x in minopos])
                lr = min([x[0] for x in minopos if x[1] == lc])
                minopos3x3 = [[lr,lc],[lr,lc+1],[lr,lc+2],[lr+1,lc+2],[lr+2,lc+2],[lr+2,lc+1],[lr+2,lc],[lr+1,lc]]
                #print('minopos3x3:{}'.format(minopos3x3))
                rm = (r * 2) % 8
                for i in range(8):
                    if minopos3x3[i] in minopos:
                        if i >= (8 - rm):
                            ri = i - (8 - rm)
                        else:
                            ri = i + rm
                        minopos.remove(minopos3x3[i])
                        minopos.append(minopos3x3[ri])
                #print('-minopos:{}'.format(minopos))
            # try:
            #     is_in_field = all(map(lambda x: self.pos[x[0]][x[1]] == 0, minopos))
            #     if is_in_field:
        self.mino_pos = minopos
        self.mino_move_angle = 0
            # except IndexError:
                # pass

    def mino_fall(self):
        minopos = self.mino_pos
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
            for b in self.mino_pos:
                b[0] += 1
        if n == 3:
            self.mino_set()
            self.row_clear()

    def mino_move(self):
        if self.mino_move_distance > 0:
            for i in range(self.mino_move_distance):
                minopos = self.mino_pos
                rc = max([x[1] for x in minopos])
                rr = [x[0] for x in minopos if x[1] == rc][0]
                #print(rr, rc)
                if self.pos[rr][rc+1] == 0:
                    for b in self.mino_pos:
                        b[1] += 1
                break
        elif self.mino_move_distance < 0:
            for i in range(abs(self.mino_move_distance)):
                minopos = self.mino_pos
                lc = min([x[1] for x in minopos])
                lr = [x[0] for x in minopos if x[1] == lc][0]
                if self.pos[lr][lc-1] == 0:
                    for b in self.mino_pos:
                        b[1] -= 1
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
        await self.channel.send('【ゲームオーバー】')
        self.client.games.remove(self)

with open('key.json', 'r') as f:
    token = json.load(f)['token']
MyClient().run(token)