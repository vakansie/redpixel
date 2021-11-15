import tkinter
import numpy
from PIL import Image, ImageTk, ImageGrab
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
        self.imgnum = iter([str(x).zfill(4) for x in range(500)])
        #self.save_canvas()

    def game_over(self):
        def exit_game():
            exit()
        if not self.lost:
            self.lost = True
            self.main_canvas.create_text(250, 250, text="HOMNOMNOM\n     FATALITY", fill="red", font=('Impact 36 bold'))
            self.main_canvas.after(3000, exit_game)

    def spawn_hom(self):
        distance = random.randrange(50, 250)
        dir = unify_vector(numpy.random.uniform(-1, 1, 2))
        spawn_point = game.player.pos + dir * distance
        self.pos = spawn_point
        Hom(spawn_point[0], spawn_point[1])
        task = self.main_canvas.after(2000, self.spawn_hom)
        self.tasks.append(task)

    def save_canvas(self):
        imgnum = next(self.imgnum)
        x = self.main_window.winfo_rootx() + self.main_canvas.winfo_x()
        y = self.main_window.winfo_rooty() + self.main_canvas.winfo_y()
        xx = x + self.main_canvas.winfo_width()
        yy = y + self.main_canvas.winfo_height()
        ImageGrab.grab(bbox=(x, y, xx, yy)).save(f"images\\redpixel{imgnum}.png")
        self.tasks.append(self.main_window.after(100, self.save_canvas))

class Player:
    def __init__(self):
        self.pos = numpy.array([20,20], dtype=numpy.float)
        self.speed = numpy.array([0,0], dtype=numpy.float)
        self.dir = numpy.array([0,1], dtype=numpy.float)
        self.cooldown = 5
        self.last_shot = 0
        self.moving = []
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

    def move_player(self, new_direction):
        self.moving.append(new_direction)
        if len(self.moving) > 20: self.moving.pop(0)
        self.dir *= 0
        for direction in self.moving:
            self.dir += direction
        self.dir = unify_vector(self.dir) + numpy.array(new_direction)
        self.speed = self.dir * 5
        self.pos += self.speed
        game.main_canvas.move(self.image,self.speed[0], self.speed[1])

    def up(self):
        self.move_player([0, -1])

    def left(self):
        self.move_player([-1, 0])

    def down(self):
        self.move_player([0, 1])

    def right(self):
        self.move_player([1, 0])

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