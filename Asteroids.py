__author__ = 'Matthew'


import pygame
from Tkinter import *
import random
import math
import time
import sqlite3
import re
import webbrowser
import os

# pygame.init()
pygame.mixer.init()
fire_sound = pygame.mixer.Sound('fire.wav')
thrust_sound = pygame.mixer.Sound('thrust.wav')
explosion_sound = pygame.mixer.Sound('explosion.wav')
saucer_sound = pygame.mixer.Sound('saucer.wav')

CANVAS_WIDTH = 700
CANVAS_HEIGHT = 700
SCORE = {1:10, 2:50, 3:100}
FLYING_SAUCER_SCORE = 500
FALCON_SCORE = 750
SAUCER_LEVEL = 1

def get_tick_count():
    return int(round(time.time() * 1000))

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

class ScoreDatabase:

    def __init__(self):
        self.connection = sqlite3.connect('Asteroid.sqlite')
        self.cursor = self.connection.cursor()

    def create_database(self):
        self.cursor.executescript('''

        CREATE TABLE IF NOT EXISTS User (
            id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name   TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Score (
            id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            user_id INTEGER,
            score INTEGER,
            score_datetime TEXT
        );

        ''')

    def get_high_scores(self):
        highscores=[]
        position=0
        self.cursor.execute('''SELECT U.name,S.score
                            FROM User U JOIN Score S ON S.user_id =U.id
                            ORDER BY S.score DESC LIMIT  10''')

        rows = self.cursor.fetchall()

        for row in rows:
            position+=1
            highscores.append((position, row[0], row[1]))

        return highscores

    def save_score(self, name, score):
        self.cursor.execute('''INSERT OR IGNORE INTO User (name)
        VALUES ( ? )''', ( name, ) )
        self.cursor.execute('SELECT id FROM User WHERE name = ? ', (name, ))
        user_id = self.cursor.fetchone()[0]

        self.cursor.execute('''INSERT OR IGNORE INTO Score (user_id, score, score_datetime)
        VALUES ( ?, ?, datetime("now"))''', (user_id,score ) )

        self.connection.commit()


class GameWorldObject:
    def __init__(self):
        self.colour = "White"
        self.points = list()
        self.angle = 0
        self.shape = list()
        self.x = 0
        self.velocity_x = 0
        self.y = 0
        self.velocity_y = 0
        self.radius = 0

    def draw(self, canvas):
        canvas.create_polygon(self.points, fill='', outline=self.colour)

    def update(self):
        self._update_position()
        self._set_points()

    def _set_points(self):
        self.points = self._calc_points(self.shape, self.angle)

    def _calc_points(self, shape, angle):
        radians = angle * math.pi /180.0
        sine = math.sin(radians)
        cosine = math.cos(radians)

        # calculate point position
        points = list()
        for p in shape:
            new_x = p[0] * cosine - p[1] * sine
            new_y = p[0] * sine + p[1] * cosine
            points.append((self.x + new_x , self.y + new_y))

        return points

    def _update_position(self):
        # update position based on movement speed (velocity speed)
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Use Stoke's law to apply drag to the ship
        self.velocity_x -= self.velocity_x * self.drag_factor
        self.velocity_y -= self.velocity_y * self.drag_factor

        # keep object in game world  (wrap around borders )
        if self.x < 0:
            self.x += CANVAS_WIDTH
        elif self.x > CANVAS_WIDTH:
            self.x -= CANVAS_WIDTH

        if self.y < 0:
            self.y += CANVAS_HEIGHT
        elif self.y > CANVAS_HEIGHT:
            self.y -= CANVAS_HEIGHT

    def get_angle(self):
        return self.angle

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_velocity_x(self):
        return self.velocity_x

    def get_velocity_y(self):
        return self.velocity_y

    def is_collision(self, gameObject):
        collision = False

        x = gameObject.get_x() - self.get_x()
        y = gameObject.get_y() - self.get_y()
        distance = math.sqrt(x**2 + y**2)
        if gameObject.get_radius() + self.get_radius() >= distance:
            collision = True

        return collision

    def get_radius(self):
        return self.radius


class Ship(GameWorldObject):
    def __init__(self):
        GameWorldObject.__init__(self)
        self.acceleration_factor = 0.7
        self.drag_factor = 0.02
        self.rotation_factor = 20
        self.score = 0
        self.active = True
        self.reactivate_time = 0
        self.lives = 3
        self.radius= 15
        self.shield_duration = 4000
        self.shield_cool_down = 15000
        self.thrust_sound_playing = False
        self.thrust_sound_duration = 500
        self.thrust_sound_last_played = 0
        self.count = 0

        # calculate the co-ordinates of the ship
        xTop = 0
        xSize = 25
        ySize = 30
        yTop = -ySize/2
        yIndent = 10

        # shape centered at (0,0)
        self.shape = ( (xTop, yTop),
                        (xTop + xSize/2.0, yTop + ySize),
                        (xTop, yTop + ySize - yIndent),
                        (xTop - xSize/2.0, yTop + ySize) )

        self.thruster_shape = ( (xTop - xSize/8.0, yTop + ySize - 5),
                            (xTop, yTop +ySize + yIndent - 5),
                            (xTop + xSize/8.0 , yTop + ySize - 5))

        self.bullet_cool_down= 200 # Fire Cool Down (ms)
        self.max_bullets = 4 # Number of bullets allowed on screen

        self.reset()

    def reset(self):

        # position at center of canvas
        self.x = CANVAS_WIDTH/2
        self.y = CANVAS_HEIGHT / 2

        self.angle = 0 # orientation

        # speed
        self.velocity_x = 0
        self.velocity_y = 0

        self.bullets = set([])
        self.last_bullet_time = 0
        self.bullets_used = 0

        #Make invincible
        self.invincibility = True
        self.last_shield_time = get_tick_count()

    def set_active(self,active):
        self.active = active

    def rotate_left(self, event):
        self.angle -= self.rotation_factor

    def rotate_right(self, event):
        self.angle += self.rotation_factor

    def accelerate(self, event):
        """
        accelerate the ship in the current direction
        """
        radians = self.angle * math.pi /180.0
        x = math.sin(radians)
        y = math.cos(radians)

        #  add to velocity vector
        self.velocity_x += x * self.acceleration_factor
        self.velocity_y -= y * self.acceleration_factor

        # if not self.thrust_sound_playing:
        self.thrust_sound_last_played = get_tick_count()
        if not self.thrust_sound_playing:
            self.thrust_sound_playing = True
            thrust_sound.play(loops=-1)

    def update(self):
        # check if ship is action
        if self.active == False:
            if get_tick_count() < self.reactivate_time:
                return
            self.active = True
            self.reset()

        #Update shield flag
        self.invincibility = (get_tick_count() - self.last_shield_time) < self.shield_duration

        for bullet in set(self.bullets):
            if bullet.remove():
                self.bullets_used = max(self.bullets_used - 1, 0)
                self.bullets.remove(bullet)
            else:
                bullet.update()

        GameWorldObject.update(self)

    def draw(self,canvas):

        if self.thrust_sound_playing:
            if get_tick_count() - self.thrust_sound_last_played > self.thrust_sound_duration:
                self.thrust_sound_playing = False
                thrust_sound.stop()

        #Draw lives
        canvas.create_text(50,20, text='Lives:', fill='White' )

        for i in range(self.lives):
            canvas.create_circle((i * 15) + 35, 40, 5, fill="Green")

        canvas.create_text(CANVAS_WIDTH - 50,20, text='Score:', fill='White' )
        canvas.create_text(CANVAS_WIDTH - 50,40, text=str(self.score), fill='Blue' )

        if self.active:
            GameWorldObject.draw(self,canvas)
            if self.invincibility:
                canvas.create_circle(self.x, self.y,self.radius + 7, outline="White")
            self.draw_thruster(canvas)

            for bullet in self.bullets:
                bullet.draw(canvas)

        #Indicate if shield available
        canvas.create_text(50, CANVAS_HEIGHT - 20, text='Shield', fill="White")
        colour = 'Red'
        if (get_tick_count() - self.last_shield_time) > self.shield_cool_down:
            if not self.invincibility:
                colour='Green'
        canvas.create_rectangle(80, CANVAS_HEIGHT - 15, 90, CANVAS_HEIGHT - 25, fill=colour)


    def draw_thruster(self, canvas):
        self.count += 1
        self.count = self.count % 10
        if self.thrust_sound_playing:
            if self.count < 5:
                thruster_points = GameWorldObject._calc_points(self, self.thruster_shape, self.angle)
                canvas.create_line((thruster_points[0], thruster_points[1]), fill="White")
                canvas.create_line((thruster_points[1], thruster_points[2]), fill="White")

    def fire(self,event):
        if not self.active:
            return

        # Dont fire unless the cooldown period has expired
        if (get_tick_count() - self.last_bullet_time >= self.bullet_cool_down):

            #Dont fire if the maximum number of bullets are already on scren
            if self.bullets_used < self.max_bullets:

                #Make new bullet
                bullet = Bullet(self)
                self.bullets.add(bullet)

                #Last bullet fired now
                self.last_bullet_time = get_tick_count()
                self.bullets_used += 1

                #Play fire sound
                fire_sound.play()

    def add_points(self,points):
        self.score+=points

    def get_score(self):
        return self.score

    #Reset cooldown (used when fire key is released)
    def reset_bullet_cooldown(self,event):
        self.last_bullet_time = 0

    def get_bullets(self):
        return list(self.bullets)

    def remove_bullet(self, bullet):
        self.bullets.remove(bullet)
        self.bullets_used -= 1

    def make_inactive_for(self, milliseconds):
        self.active = False
        self.reactivate_time = get_tick_count() + milliseconds

    def get_lives(self):
        return self.lives

    def remove_live(self):
        self.lives -= 1

    def is_collision(self, gameObject):
        if not self.active:
            return False

        return GameWorldObject.is_collision(self, gameObject)

    def handle_activate_shield_event(self, event):
        if not self.invincibility:
            if get_tick_count() - self.last_shield_time > self.shield_cool_down:
                self.activate_shield()

    def is_invincible(self):
        return self.invincibility

    def activate_shield(self):
        self.invincibility = True
        self.last_shield_time = get_tick_count()

class EnemyShip(GameWorldObject):
    def __init__(self,ship):

        # Bullets:
        self.bullets_used = 0
        self.last_bullet_time = get_tick_count()
        self.bullet_interval = random.randint(500,2000)
        self.max_bullets = 1 # Number of bullets allowed on screen
        self.bullets = set()

        # Saucer
        self.ship = ship
        # saucer_sound.play(loops=-1)
        self.last_changed=get_tick_count()
        self.interval= random.randint(100,5000)
        self.drag_factor=0
        self.colour='White'


    def set_initial_position_and_velocity(self):
        pass

    def update(self):

        current_time = get_tick_count()

        if current_time > self.last_bullet_time + self.bullet_interval:
            self.fire()
            self.bullet_interval = random.randint(500,2000)

        for bullet in set(self.bullets):
            if bullet.remove():
                self.bullets_used = max(self.bullets_used - 1, 0)
                self.bullets.remove(bullet)
            else:
                bullet.update()


        GameWorldObject.update(self)

    def draw(self, canvas):

        GameWorldObject.draw(self,canvas)
        for bullet in self.bullets:
            bullet.draw(canvas)

    def fire(self):

        if self.bullets_used < self.max_bullets:

            #Make new bullet
            x = self.ship.get_x() - self.x
            y = self.ship.get_y() - self.y

            radians = math.atan2(x,y)
            speed = 1.2
            velocity_x = speed * math.sin(radians)
            velocity_y = speed * math.cos(radians)

            bullet = Bullet(self, velocity_x, velocity_y)
            self.bullets.add(bullet)

            #Last bullet fired now
            self.last_bullet_time = get_tick_count()
            self.bullets_used += 1

            #Play fire sound
            fire_sound.play()

    def remove_bullet(self, bullet):
        self.bullets.remove(bullet)
        self.bullets_used -= 1

    def destroy(self):
        saucer_sound.stop()

    def get_bullets(self):
        return list(self.bullets)

    def get_points(self):
        pass

class Saucer(EnemyShip):
    def __init__(self,ship):

        EnemyShip.__init__(self,ship)

        self.radius = 10
        self.angle=0
        self.shape = ((-10,2),(10,2),(6,6), (-6,6), (-10,2), (-4,-2),(4,-2),
                        (-4,-2),(-4,-4),
                        (4,-4), (4,-2), (10,2))
        self.set_initial_position_and_velocity()
        self.update()

    def get_points(self):
        return FLYING_SAUCER_SCORE

    def set_initial_position_and_velocity(self):
        self.velocity_x = random.randint(200,400) / 100
        if random.randint(0,1) == 0:
            self.x = 0
        else:
            self.x=CANVAS_WIDTH -1
            self.velocity_x *= -1

        self.y = random.randint(0,CANVAS_HEIGHT)
        self.velocity_y = random.randint(200,400) / 100.0 - 0.5

    def update(self):

        current_time = int(round(time.time() * 1000))

        if current_time > self.last_changed + self.interval:
            self.velocity_y *= -1
            self.last_changed=int(round(time.time() * 1000))
            self.interval = random.randint(100,5000)

        EnemyShip.update(self)

class Falcon(EnemyShip):
    def __init__(self,ship):

        EnemyShip.__init__(self,ship)
        self.speed = 5
        self.radius = 20

        self.shape = ((20,5), (20,10), (15,10), (5,20), (-10,20), (-20,10), (-20,-10), (-10,-20), (5,-20), (15,-10),
                      (20,-10), (20,-5), (10,-5), (10,5), (20,5))

        self.set_initial_position_and_velocity()
        self.interval= 1000
        self.update()

    def set_initial_position_and_velocity(self):
        self.velocity_x = random.randint(200,400) / 100
        self.velocity_y = random.randint(200,400) / 100.0 - 0.5
        choice = random.randint(0,3)

        if choice == 0:
            self.x = random.randint(0,CANVAS_WIDTH)
            self.y = 0
        elif choice == 1:
            self.x = CANVAS_WIDTH
            self.y = random.randint(0,CANVAS_HEIGHT)
            self.velocity_x *= -1
        elif choice == 2:
            self.x = random.randint(0,CANVAS_WIDTH)
            self.y = CANVAS_HEIGHT
            self.velocity_y *= -1
        else:
            self.x = 0
            self.y = random.randint(0,CANVAS_HEIGHT)

        radians = math.atan2(self.velocity_y,
                             self.velocity_x)
        self.angle = math.degrees(radians)

    def get_points(self):
        return FALCON_SCORE

    def update(self):

        current_time = get_tick_count()

        if current_time > self.last_changed + self.interval:
            x = self.ship.get_x() - self.x
            y = self.ship.get_y() - self.y
            radians = math.atan2(y,x)
            self.angle = math.degrees(radians)
            self.velocity_x = self.speed * math.cos(radians)
            self.velocity_y = self.speed * math.sin(radians)
            self.last_changed=int(round(time.time() * 1000))

        EnemyShip.update(self)


class Fighter(EnemyShip):
    def __init__(self):

        self.shape = ((25,0), (5,5), (5,20),(15,20),(-5,20), (0,20), (-5,5), (-10,0), (-5,-5), (0,-20), (-5,-20), (15,-20),
                      (15,-20), (5,-20), (5,-5), (25,0))


class Asteroid(GameWorldObject):
    def __init__(self, size, x = None, y = None, velocity_x = None, velocity_y = None):
        GameWorldObject.__init__(self)

        if size < 1:
            self.size = 1
        else:
            self.size = size

        self.colour="Yellow"
        self.drag_factor=0
        self.radius= 40 / size
        minRadius = self.radius - (10 / size)
        maxRadius = self.radius + (10 / size)
        granularity=20
        minVary=25
        maxVary=75

        self.shape=[]
        angle=0
        while angle < 2 * math.pi:
            angleVaryPc=random.randint(minVary, maxVary)
            angleVaryRadians= (2 * math.pi / granularity) * angleVaryPc / 100
            angleFinal = angle + angleVaryRadians - (math.pi / granularity)
            radius= random.randint(minRadius, maxRadius)
            point=[0,0]
            point[0]= math.sin(angleFinal) * radius
            point[1]= math.cos(angleFinal) * radius
            self.shape.append(point)
            angle += 2 * math.pi / granularity

        if x is None:
            self.x = random.randint(0,CANVAS_WIDTH)
        else:
            self.x = x

        if y is None:
            self.y = random.randint(0,CANVAS_HEIGHT)
        else:
            self.y = y

        self.angle= random.randint(0,360)
        self.rotation_factor= random.randint(0,100) / 100.0 - 0.5

        if velocity_x is None:
            self.velocity_x = random.randint(0,100) / 100.0 - 0.5
        else:
            self.velocity_x = velocity_x

        if velocity_y is None:
            self.velocity_y = random.randint(0,100) / 100.0 - 0.5
        else:
            self.velocity_y = velocity_y

        self.update() # create the points

    def remove(self):
        pass

    def get_radius(self):
        return self.radius

    def get_size(self):
        return self.size

class Bullet(GameWorldObject):
    def __init__(self,ship, velocity_x=None, velocity_y=None):
        GameWorldObject.__init__(self)
        self.shape = ((0,0),(0,5))
        self.radius = 2.5

        # Direction of Bullet should be the direction in which the ship is facing
        self.angle = ship.get_angle()

        if velocity_x is None:
            self.velocity_x = math.sin(2 * math.pi * (ship.get_angle()/360.0))
        else:
            self.velocity_x=velocity_x

        if velocity_y is None:
            self.velocity_y = -math.cos(2 * math.pi * (ship.get_angle()/360.0))
        else:
            self.velocity_y=velocity_y



        #Initial position of the bullet should be the ships center point
        self.x=ship.get_x()
        self.y=ship.get_y()

        # Move the Bullet artificially a bit so it doesn't render inside the ship
        self.x += self.velocity_x * 20
        self.y += self.velocity_y * 20

        # Bullet movement speed factor
        self.velocity_x *= 7
        self.velocity_y *= 7

        # No rotation or rotational speed
        self.rotation_factor = 0
        self.drag_factor = 0

        self.created_time = get_tick_count()
        self.time_to_live = 2000

    def remove(self):
    # Remove a bullet if its Time To Live has expired
        return get_tick_count() - self.created_time > self.time_to_live

    def get_radius(self):
        return self.radius


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

            self.asteroids.add(Asteroid(1,velocity_x=velocity_x,velocity_y=velocity_y))

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
        self.game_over = False

        ship = Ship()
        self.addShip(ship)
        self.enemy_ship = None
        self.asteroids = set([])
        self.level = 1
        self.create_new_wave()
        self.last_enemy_ship_time = get_tick_count()
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
        self.ship = ship

    def update_objects(self):

        if self.game_over == True:
            return

        # Update game objects

        self.ship.update()

        if self.enemy_ship != None:
            self.enemy_ship.update()

        for asteroid in set(self.asteroids):
            asteroid.update()

        #Check for collisions

        #Collision with Saucer and Ships Bullets
        if self.enemy_ship is not None:
            bullets = self.ship.get_bullets()
            for bullet in bullets:
                if bullet.is_collision(self.enemy_ship):
                    explosion_sound.play()
                    points = self.enemy_ship.get_points()
                    self.ship.add_points(points)
                    self.ship.remove_bullet(bullet)
                    self.enemy_ship.destroy()
                    self.enemy_ship = None
                    self.enemy_ship_interval = random.randint(2000,20000)
                    self.last_enemy_ship_time = get_tick_count()
                    break

        # Collision with Enemy Ship and Players Ship
        if self.enemy_ship is not None:
            if not self.ship.is_invincible():
                if self.enemy_ship.is_collision(self.ship):
                    explosion_sound.play()
                    self.ship_destroyed()
                    self.enemy_ship.destroy()
                    self.enemy_ship = None
                    self.enemy_ship_interval = random.randint(2000,20000)
                    self.last_enemy_ship_time = get_tick_count()

        # Collision with Players Ship and Enemy Ship Bullet
        if self.enemy_ship is not None:
            if not self.ship.is_invincible():
                bullets = self.enemy_ship.get_bullets()
                for bullet in bullets:
                    if bullet.is_collision(self.ship):
                        self.ship_destroyed()
                        self.enemy_ship.remove_bullet(bullet)
                        break

        for asteroid in set(self.asteroids):

            #Compare each bullet against Asteroid
            bullets = self.ship.get_bullets()
            for bullet in bullets:
                if bullet.is_collision(asteroid):
                    explosion_sound.play()
                    size = asteroid.get_size()
                    if size < 3:
                        a1 = Asteroid(size + 1, asteroid.get_x(), asteroid.get_y(),
                                      asteroid.get_velocity_y() * -2 * size, asteroid.get_velocity_x() * 2 * size)
                        self.asteroids.add(a1)

                        a2 = Asteroid(size + 1, asteroid.get_x(), asteroid.get_y(),
                                      asteroid.get_velocity_y() * 2 * size, asteroid.get_velocity_x() * -2 * size)

                        self.asteroids.add(a2)

                    #Update Score
                    points=SCORE[asteroid.get_size()]
                    self.ship.add_points(points)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)
                    self.ship.remove_bullet(bullet)


            #Compare ship against Asteroid
            if not self.ship.is_invincible():
                if self.ship.is_collision(asteroid):
                    self.ship_destroyed()

        if len(self.asteroids) == 0:
            self.level += 1
            self.create_new_wave()
            if self.level == SAUCER_LEVEL:
                self.enemy_ship_interval = random.randint(2000,20000)
                self.last_enemy_ship_time = get_tick_count()


    def ship_destroyed(self):
        explosion_sound.play()
        self.ship.remove_live()
        if self.ship.get_lives() <= 0:
            self.ship.set_active(False)
            self.game_over=True
        else:
            self.ship.make_inactive_for(350)

    def draw(self):

        if self.frame.screen != self:
            return

        self.update_objects()
        self.canvas.delete('all')
        self.canvas.create_image(10, 10, image = self.backgroundImage, anchor = NW)
        self.ship.draw(self.canvas)

        # Saucer Creation
        self.create_enemy_ship()

        if self.enemy_ship != None:
            self.enemy_ship.draw(self.canvas)

        for asteroid in self.asteroids:
            asteroid.draw(self.canvas)

        # Show current wave number
        self.canvas.create_text(CANVAS_WIDTH - 40, CANVAS_HEIGHT - 20, text='Wave  ' + str(self.level) , fill="White")

        # Print game over message if needed
        if self.game_over == True:
            fire_sound.stop()
            thrust_sound.stop()
            explosion_sound.stop()
            self.canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 - 100, text="GAME OVER", fill="White", font=("Purisa", 35) )
            self.capture_name()

        if self.game_over == False:
            self.frame.get_parent().after(self.draw_interval, self.draw) # set timer to refresh screen


    #New Wave
    def create_new_wave(self):
        self.ship.activate_shield()
        for i in range(0,self.level + 2):
            self.asteroids.add(Asteroid(1))


    def capture_name(self):

        self.name_frame = Frame(self.canvas, bd=0, bg="Black")
        self.name_frame.pack()
        l = Label(self.name_frame,  bg="Black", fg="White", text="ENTER YOUR NAME", bd=0, font=("Purisa", 20))
        l.pack(side=LEFT)

        self.name_entry = Entry(self.name_frame, width=20, bg="Black", fg="White", bd=0, insertbackground="White")
        self.name_entry.focus()
        self.name_entry.pack()
        self.name_entry.bind("<Return>",self.save_score)
        self.canvas.create_window(CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 50, window=self.name_frame)


    def save_score (self, event):
        name = self.name_entry.get()
        valid = re.match('^\w+$',name) is not None
        name = name.upper()

        if not valid:
            self.canvas.create_text(CANVAS_WIDTH/2 + 90, CANVAS_HEIGHT/2 + 25, fill='Yellow', text='INVALID NAME', font=("Purisa", 20))
            self.name_entry.delete(0,END)
            self.name_entry.focus()
        else:
            score = self.ship.get_score()
            scores.save_score(name,score)
            self.frame.show_high_scores(None)

    def create_enemy_ship(self):
        if self.enemy_ship is None:
            if self.level == SAUCER_LEVEL:
                current_time = get_tick_count()
                if current_time > self.last_enemy_ship_time + self.enemy_ship_interval:
                     # self.saucer = Saucer(self.ship)
                    self.enemy_ship = Falcon(self.ship)

class HighScoresScreen(Screen):

    def __init__(self, frame, canvas):
        Screen.__init__(self,frame, canvas)

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_image(10, 10, image = self.backgroundImage, anchor = NW)
        self.canvas.create_text(CANVAS_WIDTH/2,50, fill='White', text='HIGH SCORES', font=("Purisa", 65))
        heading='   NAME                    SCORE'
        self.canvas.create_text(100,150, fill='White', text=heading, font=("Courier", 25), anchor=W)

        score_format="{0} {1} {2}"
        y_position=150

        high_scores = self.frame.get_high_scores()
        for score in high_scores:
            y_position+=40
            rank = str(score[0]).rjust(2)
            name = score[1].upper().ljust(20)
            score = str(score[2]).rjust(8)
            score_string = score_format.format(rank,name, score )
            self.canvas.create_text(100,y_position, fill='White', text=score_string, font=("Courier", 25), anchor=W)

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
        self.show_main_screen(None)

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


scores=ScoreDatabase()
scores.create_database()

root = Tk()
Canvas.create_circle = _create_circle

root.title("Asteroids")
app = Application(root)

def on_closing():
        print "In on_closing"
        root.destroy()

root.protocol('WM_DELETE_WINDOW', on_closing)

root.mainloop()

