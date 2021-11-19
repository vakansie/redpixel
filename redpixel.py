import tkinter
import numpy
from PIL import Image, ImageTk #, ImageGrab
import random
from time import time

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
        self.start_time = time()
        self.enemy_spawn_rate = 1
        self.hom_speed_factor = 1
        self.tasks = []
        self.enemy_tasks = []
        self.player = None
        self.lost = False
        self.imgnum = iter([str(x).zfill(4) for x in range(500)])
        self.score_display = self.main_canvas.create_text(450, 20, text=f'KILLS:  {0} /25', fill="red", font=('Impact 12 bold'))
        #self.save_canvas()

    def game_over(self):
        if not self.lost:
            self.lost = True
            self.main_canvas.create_text(250, 250, text="HOMNOMNOM\n     FATALITY", fill="red", font=('Impact 36 bold'))
            for task in self.tasks: self.main_canvas.after_cancel(task)
            self.main_canvas.after(3000, self.exit_game)

    def victory(self):
        self.main_canvas.create_text(250, 250, text="VICTORY", fill="green", font=('Impact 36 bold'))
        for task in self.enemy_tasks: self.main_canvas.after_cancel(task)
        self.main_canvas.after(3000, self.exit_game)

    def exit_game(self):
        exit()

    def spawn_hom(self):
        distance = random.randrange(50, 250)
        direction = unify_vector(numpy.random.uniform(-1, 1, 2))
        spawn_point = game.player.pos + direction * distance
        self.pos = spawn_point
        Hom(spawn_point[0], spawn_point[1])
        spawn_rate = int(max(1500 / game.enemy_spawn_rate*game.enemy_spawn_rate,0.01))
        task = self.main_canvas.after(spawn_rate, self.spawn_hom)
        self.enemy_tasks.append(task)
        self.tasks.append(task)

    def save_canvas(self):
        imgnum = next(self.imgnum)
        x = self.main_window.winfo_rootx() + self.main_canvas.winfo_x()
        y = self.main_window.winfo_rooty() + self.main_canvas.winfo_y()
        xx = x + self.main_canvas.winfo_width()
        yy = y + self.main_canvas.winfo_height()
        ImageGrab.grab(bbox=(x, y, xx, yy)).save(f"images\\redpixel{imgnum}.png")
        self.main_window.after(100, self.save_canvas)

    def update_score(self):
        self.main_canvas.itemconfig(self.score_display, text=f'KILLS:  {self.player.kill_count:>3} /25')

class Player:

    def __init__(self):
        self.pos = numpy.array([20,20], dtype=float)
        self.dist_to_move = numpy.array([0,0], dtype=float)
        self.dir = numpy.array([0,0], dtype=float)
        self.cooldown = 5
        self.last_shot = 0
        self.moving = None
        self.image = game.main_canvas.create_image(20, 20, image=game.player_sprite)
        self.kill_count = 0
        self.spread = 1
        self.bind_keys()

    def shoot(self, mouse_pos):
        if game.lost: return
        now = time()
        if now - self.last_shot > self.cooldown:
            for bullet_num in range(game.player.spread):
                x, y = mouse_pos.x, mouse_pos.y
                bullet = Bullet(x,y)
                game.tasks.append(game.main_canvas.after(30, bullet.move))
                game.tasks.append(game.main_canvas.after(30, bullet.hit))
            self.last_shot = now

    def move_player(self, new_direction):
        if game.lost: return
        # self.moving.append(new_direction)
        # if len(self.moving) > 1: self.moving.pop(0)
        #self.dir *= 0
        # for direction in self.moving:
        #     self.dir += direction
        self.dir = unify_vector(self.dir + unify_vector(new_direction))
        self.dist_to_move = self.dir * 5
        self.pos += self.dist_to_move
        game.main_canvas.move(self.image, self.dist_to_move[0], self.dist_to_move[1])
        self.moving = game.main_canvas.after(30, self.move_player, self.dir)


    def up(self):
        if self.moving: game.main_canvas.after_cancel(self.moving)
        self.move_player(numpy.array([0, -1]))

    def left(self):
        if self.moving: game.main_canvas.after_cancel(self.moving)
        self.move_player(numpy.array([-1, 0]))

    def down(self):
        if self.moving: game.main_canvas.after_cancel(self.moving)
        self.move_player(numpy.array([0, 1]))

    def right(self):
        if self.moving: game.main_canvas.after_cancel(self.moving)
        self.move_player(numpy.array([1, 0]))

    def bind_keys(self):
        game.main_window.bind("w", lambda x: self.up())
        game.main_window.bind("a", lambda x: self.left())
        game.main_window.bind("s", lambda x: self.down())
        game.main_window.bind("d", lambda x: self.right())
        game.main_window.bind("<Button-1>", lambda mouse_pos: self.shoot(mouse_pos))

class Hom:
    def __init__(self, x, y) -> None:
        self.pos = numpy.array([x,y], dtype=float)
        self.image = game.main_canvas.create_image(self.pos[0], self.pos[1], image=game.hom_sprite)
        self.move_task = game.main_canvas.after(int(1000 / game.hom_speed_factor), self.move)
        game.enemy_tasks.append(self.move_task)

    def move(self):
        if 'hit' in game.main_canvas.itemcget(self.image, "tags"):
            self.death()
            return
        dir_to_player = unify_vector(game.player.pos - self.pos) * 5 * game.hom_speed_factor
        self.pos += dir_to_player
        game.main_canvas.move(self.image, dir_to_player[0], dir_to_player[1])
        self.hit()
        task = game.main_canvas.after(int(200/game.hom_speed_factor), self.move)
        game.enemy_tasks.append(task)

    def hit(self):
        colliders = game.main_canvas.find_overlapping(
            self.pos[0], self.pos[1], self.pos[0]+1, self.pos[1]+1)
        for collider in colliders:
            if collider == game.player.image:
                game.game_over()

    def death(self):
        game.main_canvas.delete(self.image)
        del self
        game.player.kill_count += 1
        game.update_score()
        if game.player.kill_count >= 25:
            game.victory()
            return
        game.enemy_spawn_rate += 0.1
        game.hom_speed_factor += 0.07
        return

class Bullet:
    def __init__(self, x, y) -> None:
        self.dir_from_player = unify_vector(numpy.array([x,y], dtype=float) - game.player.pos)
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

def main():
    global game
    game = Game()
    game.player = Player()
    hom1 = Hom(100, 100)
    hom2 = Hom(200, 100)
    game.spawn_hom()
    game.main_window.mainloop()

if __name__ == '__main__':
    main()