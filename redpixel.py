import tkinter
import numpy
from PIL import Image, ImageTk #, ImageGrab
import random
from time import time
from math import sin, cos, pi


class Game:

    def __init__(self):
        self.main_window = tkinter.Tk()
        self.main_canvas =tkinter.Canvas(self.main_window, bg="black", height=500, width=500)
        self.main_canvas.pack(expand=1, fill='both')
        self.player_sprite = ImageTk.PhotoImage(Image.open('redpixel.png'))
        self.hom_sprite = ImageTk.PhotoImage(Image.open('hom1.png'))
        self.final_hom_sprite = ImageTk.PhotoImage(Image.open('finalhom.png'))        
        self.adjuster_sprite = ImageTk.PhotoImage(Image.open('taco.png'))
        self.enemy_spawn_rate = 1
        self.hom_speed_factor = 1
        self.spawn_task = None
        self.hit_homs = []
        self.player = None
        self.final_hom = None
        self.lost = False
        self.golden_r = (1 + 5 ** 0.5) / 2
        self.score_display = self.main_canvas.create_text(450, 20, text=f'KILLS:  {0}', fill="red", font=('Impact 12 bold'))
        # self.imgnum = iter([str(x).zfill(4) for x in range(500)])
        # self.save_canvas()

    def game_over(self):
        if not self.lost:
            self.lost = True
            self.player.cooldown = 10
            self.main_canvas.create_text(250, 250, text="HOMNOMNOM\n     FATALITY", fill="red", font=('Impact 36 bold'))
            self.main_canvas.after(3000, self.exit_game)

    def victory(self):
        for hom in game.main_canvas.find_withtag('hom'):
            game.hit_homs.append(hom)
        self.main_canvas.after_cancel(self.spawn_task)
        self.main_canvas.create_text(250, 250, text="VICTORY", fill="green", font=('Impact 36 bold'))
        self.main_canvas.after(5000, self.exit_game)

    def exit_game(self):
        # from test import display_top
        # snapshot = tracemalloc.take_snapshot()
        # display_top(snapshot)
        exit()

    def spawn_hom(self):
        distance = random.randrange(50, 250)
        direction = unify_vector(numpy.random.uniform(-1, 1, 2))
        spawn_point = game.player.pos + direction * distance
        self.pos = spawn_point
        Hom(x=spawn_point[0], y=spawn_point[1], sprite=game.hom_sprite)
        spawn_rate = int(max(1500 / game.enemy_spawn_rate*game.enemy_spawn_rate,0.01))
        self.spawn_task = self.main_canvas.after(spawn_rate, self.spawn_hom)

    def spawn_final_hom(self):
        self.final_hom = Final_Hom()

    def save_canvas(self):
        imgnum = next(self.imgnum)
        x = self.main_window.winfo_rootx() + self.main_canvas.winfo_x()
        y = self.main_window.winfo_rooty() + self.main_canvas.winfo_y()
        xx = x + self.main_canvas.winfo_width()
        yy = y + self.main_canvas.winfo_height()
        #ImageGrab.grab(bbox=(x, y, xx, yy)).save(f"images\\redpixel{imgnum}.png")
        self.main_window.after(100, self.save_canvas)

    def update_score(self):
        self.main_canvas.itemconfig(self.score_display, text=f'KILLS:  {self.player.kill_count:>3}')

class Player:

    def __init__(self):
        self.pos = numpy.array([20,20], dtype=float)
        self.dist_to_move = numpy.array([0,0], dtype=float)
        self.dir = numpy.array([0,0], dtype=float)
        self.up_vector = numpy.array([0, -1])
        self.left_vector = numpy.array([-1, 0])
        self.down_vector = numpy.array([0, 1])
        self.right_vector = numpy.array([1, 0])
        self.cooldown = 0.3
        self.last_shot = 0
        self.moving = None
        self.image = game.main_canvas.create_image(20, 20, image=game.player_sprite)
        self.kill_count = 0
        self.spread = 1
        self.bind_keys()

    def shoot(self, mouse_pos):
        if game.lost: return
        now = time()
        difference_vector = game.player.pos - numpy.array([mouse_pos.x, mouse_pos.y])
        scale = magnitude(difference_vector)/300
        if now - self.last_shot < self.cooldown: return
        for bullet_num in range(game.player.spread):
            if not bullet_num % 2 and bullet_num:
                bullet_num = bullet_num - 1
                angle = 2 * pi - (bullet_num * game.golden_r/pi * scale)
            else: angle = (bullet_num * game.golden_r/pi * scale)
            x = cos((angle)) * (mouse_pos.x - game.player.pos[0]) - sin((angle)) * (mouse_pos.y - game.player.pos[1]) + game.player.pos[0]
            y = sin((angle)) * (mouse_pos.x - game.player.pos[0]) + cos((angle)) * (mouse_pos.y - game.player.pos[1]) + game.player.pos[1]
            Bullet(x, y)
        self.last_shot = now

    def move_player(self, direction_vector):
        if game.lost: return
        self.dir = unify_vector(self.dir + unify_vector(direction_vector))
        self.dist_to_move = self.dir * 5
        self.pos += self.dist_to_move
        game.main_canvas.move(self.image, self.dist_to_move[0], self.dist_to_move[1])
        if self.moving: game.main_canvas.after_cancel(self.moving)
        self.moving = game.main_canvas.after(30, self.move_player, self.dir)

    def up(self):
        self.move_player(self.up_vector)

    def left(self):
        self.move_player(self.left_vector)

    def down(self):
        self.move_player(self.down_vector)

    def right(self):
        self.move_player(self.right_vector)

    def bind_keys(self):
        game.main_window.bind("w", lambda x: self.up())
        game.main_window.bind("a", lambda x: self.left())
        game.main_window.bind("s", lambda x: self.down())
        game.main_window.bind("d", lambda x: self.right())
        game.main_window.bind("<Button-1>", lambda mouse_pos: self.shoot(mouse_pos))

class Hom:

    __slots__ = ('pos', 'image', 'move_task')

    def __init__(self, x, y, sprite):
        self.pos = numpy.array([x,y], dtype=float)
        self.image = game.main_canvas.create_image(self.pos[0], self.pos[1], image=sprite, tags='hom')
        self.move_task = game.main_canvas.after(int(1000 / game.hom_speed_factor), self.move_hom)

    def move_hom(self):
        if self.image in game.hit_homs:
            game.hit_homs.remove(self.image)
            self.death()
            return
        distance = magnitude(game.player.pos - self.pos)
        if 6 < distance < 50:
            leap = unify_vector(game.player.pos - self.pos) * distance * (1 + random.choice((0.3, -0.3)))
            game.main_canvas.move(self.image, leap[0], leap[1])
            self.pos += leap
        self.homnomnom()
        dir_to_player = unify_vector(game.player.pos - self.pos) * 5 * game.hom_speed_factor
        self.pos += dir_to_player
        game.main_canvas.move(self.image, dir_to_player[0], dir_to_player[1])
        self.move_task = game.main_canvas.after(max(int(200/game.hom_speed_factor), 30), self.move_hom)

    def homnomnom(self):
        if game.player.image in game.main_canvas.find_overlapping(
            self.pos[0], self.pos[1], self.pos[0]+1, self.pos[1]+1):
            game.game_over()

    def death(self):
        game.main_canvas.after_cancel(self.move_task)
        game.main_canvas.delete(self.image)
        del self
        game.player.kill_count += 1
        game.update_score()
        game.player.spread = game.player.kill_count // 5 + 1
        if game.player.kill_count == 25: game.spawn_final_hom()
        if not game.final_hom:
            game.enemy_spawn_rate += 0.15
            game.hom_speed_factor += 0.05
        return

class Final_Hom:
    
    def __init__(self):
        distance = random.randrange(40, 75)
        self.pos = numpy.array([250, 250], dtype=float)
        dir_from_player = unify_vector(self.pos - game.player.pos)
        spawn_point = self.pos + dir_from_player * distance
        self.pos = spawn_point
        self.image = game.main_canvas.create_image(self.pos[0], self.pos[1], image=game.final_hom_sprite, tags='hom')
        self.health_bar = game.main_canvas.create_rectangle(175, 470, 325, 500, fill='red')
        self.hitpoints = 250
        self.task = self.act()
        game.enemy_spawn_rate *= 2
        game.hom_speed_factor += 0.1

    def act(self):
        self.resolve_hits()
        self.wield_taco(self.pos[0] - 35, self.pos[1] + 15)
        self.move_final_hom()
        self.wield_taco(self.pos[0] - 35, self.pos[1] + 15)
        self.task = game.main_canvas.after(700, self.act)

    def wield_taco(self, x, y):
        taco = Hom(x, y, sprite=game.adjuster_sprite)
        dx, dy = random.choice((-1, 0, 1)), random.choice((-1, 1))
        step = numpy.array([dx, dy]) * random.choice((70, 70, 0))
        game.main_canvas.move(taco.image, step[0], step[1])
        taco.pos += step

    def resolve_hits(self):
        hits = [hom for hom in game.hit_homs if hom == self.image]
        for hit in hits:
            game.hit_homs.remove(hit)
            self.hitpoints -= 1
        self.update_health_bar()
        if self.hitpoints <= 0:
            self.death()

    def death(self):
        game.main_canvas.delete(self.health_bar)
        game.main_canvas.after_cancel(self.task)
        game.main_canvas.delete(self.image)
        del self
        game.victory()

    def update_health_bar(self):
        game.main_canvas.delete(self.health_bar)
        self.health_bar = game.main_canvas.create_rectangle(self.pos[0] - 75, 470, self.pos[0] + 75-(150-self.hitpoints), 500, fill='red')

    def move_final_hom(self):
        step = unify_vector(game.player.pos - self.pos) * 5 * game.hom_speed_factor
        self.pos += step
        game.main_canvas.move(self.image, step[0], step[1])

class Bullet:

    #__slots__ = ('dir_from_player', 'task', 'image')

    def __init__(self, x, y):
        self.dir_from_player = unify_vector(numpy.array([x,y]) - game.player.pos) * 10
        bullet_pos = game.player.pos + self.dir_from_player * 1.5
        self.task = game.main_canvas.after(30, self.move_bullet)
        self.image = game.main_canvas.create_rectangle(
            bullet_pos[0],
            bullet_pos[1]+6,
            bullet_pos[0]+5,
            bullet_pos[1]+11,
            fill='red',
            tags='bullet')
        game.main_canvas.after(1200, self.delete)

    def move_bullet(self):
        game.main_canvas.move(self.image, self.dir_from_player[0], self.dir_from_player[1])
        self.hit()
        self.task = game.main_canvas.after(30, self.move_bullet)

    def hit(self):
        hitbox = game.main_canvas.coords(self.image)
        if not hitbox: return
        overlap = game.main_canvas.find_overlapping( hitbox[0], hitbox[1], hitbox[2], hitbox[3])
        hit_homs = [hom for hom in game.main_canvas.find_withtag('hom') if hom in overlap]
        if not hit_homs: return
        for hom in hit_homs:
            game.hit_homs.append(hom)
        self.delete()
        game.player.last_shot = 0.2

    def delete(self):
        game.main_canvas.after_cancel(self.task)
        game.main_canvas.delete(self.image)
        del self

def unify_vector(vector):
    if not numpy.any(vector): return vector
    return vector / (vector**2).sum()**0.5

def magnitude(vector):
    return(vector[0] * vector[0] + vector[1] * vector[1])**0.5

def main():
    global game
    game = Game()
    game.player = Player()
    Hom(100, 100, game.hom_sprite)
    Hom(200, 100, game.hom_sprite)
    game.spawn_hom()
    game.main_window.mainloop()

if __name__ == '__main__':
    # import tracemalloc
    # tracemalloc.start()
    main()