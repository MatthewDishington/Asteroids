__author__ = 'Matthew'

from tkinter import *
root = Tk()

import re
import webbrowser
import os

from ScoreDatabase import *
from PlayerShip import *
from Asteroid import *
from Saucer import *
from Falcon import *
from Fighter import *

# root = Tk()

if os.name == "posix": # e.g. mac
    config={"bullet_speed_factor": 10,
            "asteroid_speed_min": 100,
            "asteroid_speed_max": 150,
            "high_scores_size": 65,
            "scores_size": 25,
            "rotation_factor": 20,
            "acceleration_factor": 0.7,
            "label_and_entry_box_size": 20,
            "enemy_ship_bullet_speed": 1.2,
            "saucer_speed_min": 200,
            "saucer_speed_max": 400,
            "falcon_speed": 3,
            "fighter_speed": 3

            }
else:
    config={"bullet_speed_factor": 7,
            "asteroid_speed_min": 75,
            "asteroid_speed_max": 125,
            "high_scores_size": 50,
            "scores_size": 20,
            "rotation_factor": 10,
            "acceleration_factor": 0.4,
            "wave_text_size": 15,
            "label_and_entry_box_size": 15,
            "enemy_ship_bullet_speed": 0.8,
            "saucer_speed_min": 150,
            "saucer_speed_max": 300,
            "falcon_speed": 3,
            "fighter_speed": 3
            }

CANVAS_WIDTH = 700
CANVAS_HEIGHT = 700
SCORE = {1:10, 2:50, 3:100}

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)


class Screen():

    def __init__(self, frame, canvas):
        self.frame=frame
        self.canvas = canvas
        self.backgroundImage = PhotoImage(file="nebula.gif")


    def draw(self):
        pass

class MainScreen(Screen):

    draw_interval = int((1/60.0) * 1000)

    def __init__(self, frame, canvas):
        Screen.__init__(self, frame, canvas)
        self.asteroids = set([])
        for i in range(0,4):
            velocity_x = random.randint(50,100) / 100.0 - 0.2
            velocity_y = random.randint(50,100) / 100.0 - 0.2

            self.asteroids.add(Asteroid(CANVAS_WIDTH, CANVAS_HEIGHT,1,config,velocity_x=velocity_x,velocity_y=velocity_y))

    def draw(self):
        if self.frame.screen != self:
            return

        self.canvas.delete("all")

        for asteroid in set(self.asteroids):
            asteroid.update()

        self.canvas.create_image(10, 10, image = self.backgroundImage, anchor = NW)
        self.canvas.create_text(CANVAS_WIDTH/2,150, fill='White', text='ASTEROIDS', font=("Purisa", 65))

        play_game_id=self.canvas.create_text(CANVAS_WIDTH/2, 350, fill='White', text='PLAY GAME', font=("Purisa", 25))
        self.canvas.tag_bind(play_game_id, "<Button-1>", self.frame.play_game)

        high_scores_id=self.canvas.create_text(CANVAS_WIDTH/2, 400, fill='White', text='HIGH SCORES', font=("Purisa", 25))
        self.canvas.tag_bind(high_scores_id, "<Button-1>", self.frame.show_high_scores)

        instructions_id=self.canvas.create_text(CANVAS_WIDTH/2, 450, fill='White', text='INSTRUCTIONS', font=("Purisa", 25))
        self.canvas.tag_bind(instructions_id, "<Button-1>", self.frame.show_instructions)

        exit_game_id=self.canvas.create_text(CANVAS_WIDTH/2, 500, fill='White', text='EXIT GAME', font=("Purisa", 25))
        self.canvas.tag_bind(exit_game_id, "<Button-1>", sys.exit)

        for asteroid in self.asteroids:
            asteroid.draw(self.canvas)

        if self.frame.screen == self:
            self.frame.get_parent().after(self.draw_interval, self.draw) # set timer to refresh screen

class PlayGameScreen(Screen):

    draw_interval = int((1/60.0) * 1000) # refresh 60 times a second

    def __init__(self, frame, canvas):
        Screen.__init__(self,frame, canvas)
        Sounds.load_sounds()
        self.game_over = False

        ship = PlayerShip(CANVAS_WIDTH, CANVAS_HEIGHT, config)
        self.addShip(ship)
        self.enemy_ships = set([])
        self.asteroids = set([])
        self.level = 1
        self.create_new_wave()
        self.last_enemy_ship_time = get_current_time()
        self.enemy_ship_interval = random.randint(2000,20000)

        parent = frame.get_parent()
        parent.bind('<Left>',ship.rotate_left)
        parent.bind('<Right>',ship.rotate_right)
        parent.bind('<Up>', ship.accelerate)
        parent.bind('<space>', ship.fire)
        parent.bind('<KeyRelease-space>', ship.reset_bullet_cooldown)
        parent.bind('<s>', ship.handle_activate_shield_event)

        self.draw()

    def addShip(self, ship):
        self.player_ship = ship

    def update_objects(self):

        if self.game_over == True:
            return

        # Update game objects

        self.player_ship.update()

        for enemy_ship in self.enemy_ships:
            enemy_ship.update()

        for asteroid in set(self.asteroids):
            asteroid.update()

        #Check for collisions

        #Collision with Enemy ship and Ships Bullets
        for enemy_ship in set(self.enemy_ships):
            bullets = self.player_ship.get_bullets()
            for bullet in bullets:
                if bullet.is_collision(enemy_ship):
                    Sounds.explosion_sound.play()
                    points = enemy_ship.get_points()
                    self.player_ship.add_points(points)
                    self.player_ship.remove_bullet(bullet)
                    enemy_ship.destroy()
                    self.enemy_ships.remove(enemy_ship)
                    self.enemy_ship_interval = random.randint(2000,20000)
                    self.last_enemy_ship_time = get_current_time()
                    break

        # Collision with Enemy Ship and Players Ship
        if self.player_ship.is_active() and not self.player_ship.is_invincible():
            for enemy_ship in set(self.enemy_ships):
                if enemy_ship.is_collision(self.player_ship):
                    # explosion_sound.play()
                    self.ship_destroyed()
                    enemy_ship.destroy()
                    self.enemy_ships.remove(enemy_ship)
                    self.enemy_ship_interval = random.randint(2000,20000)
                    self.last_enemy_ship_time = get_current_time()
                    break

        # Collision with Players Ship and Enemy Ship Bullet
        if self.player_ship.is_active() and  not self.player_ship.is_invincible():
            for enemy_ship in set(self.enemy_ships):
                bullets = enemy_ship.get_bullets()
                for bullet in bullets:
                    if bullet.is_collision(self.player_ship):
                        self.ship_destroyed()
                        enemy_ship.remove_bullet(bullet)
                        break

        for asteroid in set(self.asteroids):

            #Compare each bullet against Asteroid
            bullets = self.player_ship.get_bullets()
            for bullet in bullets:
                if bullet.is_collision(asteroid):
                    Sounds.explosion_sound.play()
                    size = asteroid.get_size()
                    if size < 3:
                        a1 = Asteroid(CANVAS_WIDTH, CANVAS_HEIGHT, size + 1, config, asteroid.get_x(), asteroid.get_y(),
                                      asteroid.get_velocity_y() * -1.25 * size, asteroid.get_velocity_x() * 1.25 * size)
                        self.asteroids.add(a1)

                        a2 = Asteroid(CANVAS_WIDTH, CANVAS_HEIGHT,size + 1, config, asteroid.get_x(), asteroid.get_y(),
                                      asteroid.get_velocity_y() * 1.25 * size, asteroid.get_velocity_x() * -1.25 * size)

                        self.asteroids.add(a2)

                    #Update Score
                    points=SCORE[asteroid.get_size()]
                    self.player_ship.add_points(points)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)
                    self.player_ship.remove_bullet(bullet)


            #Compare ship against Asteroid
            if self.player_ship.is_active() and not self.player_ship.is_invincible() :
                if self.player_ship.is_collision(asteroid):
                    self.ship_destroyed()

        if len(self.asteroids) == 0:
            self.level += 1
            self.create_new_wave()

    def ship_destroyed(self):
        Sounds.explosion_sound.play()
        self.player_ship.remove_live()
        if self.player_ship.get_lives() <= 0:
            self.player_ship.set_active(False)
            self.game_over=True
        else:
            self.player_ship.make_inactive_for(350)

    def draw(self):

        if self.frame.screen != self:
            return

        self.update_objects()
        self.canvas.delete('all')
        self.canvas.create_image(10, 10, image = self.backgroundImage, anchor = NW)
        self.player_ship.draw(self.canvas)

        # Saucer Creation
        self.create_enemy_ship()

        for enemy_ship in self.enemy_ships:
            enemy_ship.draw(self.canvas)

        for asteroid in self.asteroids:
            asteroid.draw(self.canvas)

        # Show current wave number
        self.canvas.create_text(CANVAS_WIDTH - 45, CANVAS_HEIGHT - 20, text='Wave  ' + str(self.level) , fill="White",
                                font=("Purisa", 15))

        # Print game over message if needed
        if self.game_over == True:
            Sounds.stop_sounds()

            self.canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - 100, text="GAME OVER", fill="White", font=("Purisa", 35) )
            score = self.player_ship.get_score()
            rank = scores_database.get_rank(score)
            rank_text = 'YOU RANKED: '+ str(rank)
            self.canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - 50, text=rank_text, fill="White", font=("Purisa", 20))
            self.capture_name()

        if self.game_over == False:
            self.frame.get_parent().after(self.draw_interval, self.draw) # set timer to refresh screen


    #New Wave
    def create_new_wave(self):
        self.player_ship.activate_shield()
        for i in range(0,self.level + 2):
            self.asteroids.add(Asteroid(CANVAS_WIDTH, CANVAS_HEIGHT,1, config))


    def capture_name(self):
        label_size = config["label_and_entry_box_size"]
        entry_box_size = config["label_and_entry_box_size"]
        self.name_frame = Frame(self.canvas, bd=0, bg="Black")
        self.name_frame.pack()
        l = Label(self.name_frame, bg="Black", fg="White", text="ENTER YOUR NAME:", bd=0, font=("Purisa", label_size))
        l.pack(side=LEFT)

        self.name_entry = Entry(self.name_frame, width=entry_box_size, bg="Black", fg="White", bd=0, insertbackground="White", font=("Purisa", entry_box_size))
        self.name_entry.focus()
        self.name_entry.pack()
        self.name_entry.bind("<Return>",self.save_score)
        self.canvas.create_window(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 70, window=self.name_frame)


    def save_score (self, event):
        name = self.name_entry.get()
        valid = re.match('^\w+$',name) is not None
        name = name.upper()

        if not valid:
            self.canvas.create_text(CANVAS_WIDTH/2 + 90, CANVAS_HEIGHT/2 + 45, fill='Yellow', text='INVALID NAME', font=("Purisa", 20))
            self.name_entry.delete(0, END)
            self.name_entry.focus()
        else:
            score = self.player_ship.get_score()
            scores_database.save_score(name, score)
            self.frame.show_high_scores(None)

    def create_enemy_ship(self):

        current_time = get_current_time()
        if current_time > self.last_enemy_ship_time + self.enemy_ship_interval:
            fighter_level = 1
            if self.level >= fighter_level:
                max_ships = self.level - fighter_level + 1
                while len(self.enemy_ships) < max_ships:
                    self.enemy_ships.add(Fighter(CANVAS_WIDTH, CANVAS_HEIGHT,self.player_ship, config))
                    self.last_enemy_ship_time = current_time
            elif self.level >= 4:
                  if len(self.enemy_ships) < 1:
                    self.enemy_ships.add(Falcon(CANVAS_WIDTH, CANVAS_HEIGHT,self.player_ship, config))
                    self.last_enemy_ship_time = current_time
            elif self.level >= 3:
                if len(self.enemy_ships) < 1:
                    self.enemy_ships.add(Saucer(CANVAS_WIDTH, CANVAS_HEIGHT,self.player_ship, config))
                    self.last_enemy_ship_time = current_time


class HighScoresScreen(Screen):

    def __init__(self, frame, canvas):
        Screen.__init__(self,frame, canvas)

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, image = self.backgroundImage, anchor = NW)
        high_screen_size = config['high_scores_size']
        self.canvas.create_text(CANVAS_WIDTH/2,50, fill='White', text='HIGH SCORES', font=("Purisa", high_screen_size))
        heading='   NAME                    SCORE'
        score_size = config['scores_size']
        self.canvas.create_text(100, 150, fill='White', text=heading, font=("Courier", score_size), anchor=W)

        score_format="{0} {1} {2}"
        y_position=150

        high_scores = self.frame.get_high_scores()
        for score in high_scores:
            y_position+=40
            rank = str(score[0]).rjust(2)
            name = score[1].upper().ljust(20)
            score = str(score[2]).rjust(8)
            score_string = score_format.format(rank,name, score )
            self.canvas.create_text(100, y_position, fill='White', text=score_string, font=("Courier", score_size), anchor=W)

        back_id=self.canvas.create_text(CANVAS_WIDTH/2, 650, fill='White', text='BACK TO MAIN MENU', font=("Purisa", 25))
        self.canvas.tag_bind(back_id, "<Button-1>", self.frame.show_main_screen)

class Application(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(parent, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background='Black')
        self.canvas.pack()
        self.hs = []
        self.screen = None
        # self.show_main_screen(None)

    def get_parent(self):
        return self.parent

    def load_high_scores(self):
        db=ScoreDatabase()
        self.hs=db.get_high_scores()

    def get_high_scores(self):
        return self.hs

    def show_main_screen(self, event):
        self.screen = MainScreen(self, self.canvas)
        self.screen.draw()

    def show_high_scores(self, event):
        self.screen = HighScoresScreen(self,self.canvas)
        self.screen.draw()
        self.load_high_scores()
        self.screen.draw()

    def show_instructions(self, event):
        webbrowser.open_new('file://' + os.path.realpath('help.html'))

    def play_game(self, event):
        self.screen = PlayGameScreen(self,self.canvas)
        self.screen.draw()

Canvas.create_circle = _create_circle
scores_database=ScoreDatabase()
scores_database.create_database()

root.title("Asteroids")
app = Application(root)
app.show_main_screen(None)

root.mainloop()


