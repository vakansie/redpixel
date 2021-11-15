import tkinter
import numpy
from PIL import Image, ImageTk
import random
from time import time, sleep


def unify_vector(vector):
    if vector[0] == 0 and vector[1] == 0: return vector*0
    return vector / (vector**2).sum()**0.5

class Game:

    def __init__(self):
        self.main_window = tkinter.Tk()
        self.main_canvas =tkinter.Canvas(self.main_window, bg="black", height=500, width=500)
        self.main_canvas.pack(expand=1, fill='both')
        self.player_sprite = ImageTk.PhotoImage(Image.open('redpixel.png'))
        self.hom_sprite = ImageTk.PhotoImage(Image.open('hom1.png'))
        self.tasks = []
        self.player = None
        self.lost = False

    def game_over(self):
        if not self.lost:
        #     for task in self.tasks:
        #         self.main_canvas.after_cancel(task)
            self.lost = True
            print('homnomnom')
            sleep(3)
            exit()
            # top = tkinter.Toplevel()
            # # game.main_canvas.wait_window(top)

    def spawn_hom(self):
        distance = random.randrange(50, 250)
        spawn_point = game.player.pos - numpy.array(game.player.dir) * distance
        self.pos = spawn_point
        Hom(spawn_point[0], spawn_point[1])
        task = self.main_canvas.after(2000, self.spawn_hom)
        self.tasks.append(task)

class Player:
    def __init__(self):
        self.pos = numpy.array([20,20], dtype=numpy.float)
        self.speed = numpy.array([0,0], dtype=numpy.float)
        self.dir = numpy.array([0,1], dtype=numpy.float)
        self.cooldown = 5
        self.last_shot = 0
        self.image = game.main_canvas.create_image(20, 20, image=game.player_sprite)
        self.bind_keys()

    def shoot(self, mouse_pos):
        now = time()
        if now - self.last_shot > self.cooldown:
            x, y = mouse_pos.x, mouse_pos.y
            bullet = Bullet(x,y)
            game.tasks.append(game.main_canvas.after(30, bullet.move))
            game.tasks.append(game.main_canvas.after(30, bullet.hit))
            self.last_shot = now

    def up(self):
        self.dir = [0, -1]
        self.speed = unify_vector(self.speed + self.dir) * 5
        self.pos += self.speed
        game.main_canvas.move(self.image,self.speed[0], self.speed[1])

    def left(self):
        self.dir = [-1, 0]
        self.speed = unify_vector(self.speed + self.dir) * 5
        self.pos += self.speed
        game.main_canvas.move(self.image,self.speed[0], self.speed[1])

    def down(self):
        self.dir = [0, 1]
        self.speed = unify_vector(self.speed + self.dir) * 5
        self.pos += self.speed
        game.main_canvas.move(self.image,self.speed[0], self.speed[1])

    def right(self):
        self.dir = [1, 0]
        self.speed = unify_vector(self.speed + self.dir) * 5
        self.pos += self.speed
        game.main_canvas.move(self.image,self.speed[0], self.speed[1])

    def bind_keys(self):
        game.main_window.bind("w", lambda x: self.up())
        game.main_window.bind("a", lambda x: self.left())
        game.main_window.bind("s", lambda x: self.down())
        game.main_window.bind("d", lambda x: self.right())
        game.main_window.bind("<Button-1>", lambda mouse_pos: self.shoot(mouse_pos))

class Hom:
    def __init__(self, x, y) -> None:
        self.pos = numpy.array([x,y], dtype=numpy.float)
        self.image = game.main_canvas.create_image(self.pos[0], self.pos[1], image=game.hom_sprite)
        self.move_tasks = game.main_canvas.after(1000, self.move)
        game.tasks.append(self.move_tasks)

    def move(self):
        if 'hit' in game.main_canvas.itemcget(self.image, "tags"):
            game.main_canvas.delete(self.image)
            del self
            return
        dir_to_player = unify_vector(game.player.pos - self.pos) * 5
        self.pos += dir_to_player
        game.main_canvas.move(self.image, dir_to_player[0], dir_to_player[1])
        self.hit()
        task = game.main_canvas.after(200, self.move)
        game.tasks.append(task)

    def hit(self):
        colliders = game.main_canvas.find_overlapping(
            self.pos[0], self.pos[1], self.pos[0]+1, self.pos[1]+1)
        for collider in colliders:
            if collider == game.player.image:
                game.game_over()

class Bullet:
    def __init__(self, x, y) -> None:
        self.dir_from_player = unify_vector(numpy.array([x,y], dtype=numpy.float) - game.player.pos)
        bullet_pos = game.player.pos + (self.dir_from_player * 10)
        self.image = game.main_canvas.create_rectangle(
            bullet_pos[0],
            bullet_pos[1]+6,
            bullet_pos[0]+5,
            bullet_pos[1]+11,
            fill='red',
            tags='bullet')
        game.main_canvas.after(3000, self.delete)

    def move(self):
        game.main_canvas.move(self.image, self.dir_from_player[0]*10, self.dir_from_player[1]*10)
        task = game.main_canvas.after(30, self.move)
        game.tasks.append(task)

    def hit(self):
        if 'hit' in game.main_canvas.itemcget(self.image, "tags"):
            game.main_canvas.delete(self.image)
            del self
            return
        hitbox = game.main_canvas.coords(self.image)
        if hitbox and len(game.main_canvas.find_overlapping(
            hitbox[0], hitbox[1], hitbox[2], hitbox[3])) != 1:
            game.main_canvas.addtag_overlapping(
                'hit',
                hitbox[0], hitbox[1], hitbox[2], hitbox[3])
            game.player.last_shot = 0
        task =game.main_canvas.after(30, self.hit)
        game.tasks.append(task)

    def delete(self):
        game.main_canvas.delete(self.image)
        del self

game = Game()
game.player = Player()
hom1 = Hom(100, 100)
hom2 = Hom(200, 100)
game.spawn_hom()

game.main_window.mainloop()