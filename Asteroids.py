__author__ = 'Matthew'


import pygame
from Tkinter import *
import random
import math
import time


# pygame.init()
pygame.mixer.init()
fire_sound = pygame.mixer.Sound('fire.wav')
thrust_sound = pygame.mixer.Sound('thrust.wav')
explosion_sound = pygame.mixer.Sound('bangLarge.wav')

CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500
SCORE = {1:10, 2:50, 3:100}

def get_tick_count():
    return int(round(time.time() * 1000))

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

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
        radians = self.angle * math.pi /180.0
        sine = math.sin(radians)
        cosine = math.cos(radians)

        # calculate point position
        self.points = list()
        for p in self.shape:
            new_x =  p[0] * cosine - p[1] * sine
            new_y = p[0] * sine + p[1] * cosine
            self.points.append((self.x + new_x , self.y + new_y))

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
        self.acceleration_factor = 0.5
        self.drag_factor = 0.02
        self.rotation_factor = 15
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

            for bullet in self.bullets:
                bullet.draw(canvas)

        #Indicate if shield available
        canvas.create_text(50, CANVAS_HEIGHT - 20, text='Shield', fill="White")
        colour = 'Red'
        if (get_tick_count() - self.last_shield_time) > self.shield_cool_down:
            if not self.invincibility:
                colour='Green'
        canvas.create_rectangle(80, CANVAS_HEIGHT - 15, 90, CANVAS_HEIGHT - 25, fill=colour)


    def fire(self,event):
        if not self.active:
            return

        # Dont fire unless the cooldown period has expired
        if (get_tick_count() - self.last_bullet_time >= self.bullet_cool_down):

            #Dont fire if the maxium number of bullets are already on scren
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
        maxRadius = self.radius + (10/ size)
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
    def __init__(self,ship):
        GameWorldObject.__init__(self)
        self.shape = ((0,0),(0,5))
        self.radius = 2.5

        # Direction of Bullet should be the direction in which the ship is facing
        self.angle = ship.get_angle()
        self.velocity_x = math.sin(2 * math.pi * (ship.get_angle()/360.0))
        self.velocity_y = -math.cos(2 * math.pi * (ship.get_angle()/360.0))

        #Initial position of the bullet should be the ships center point
        self.x=ship.get_x()
        self.y=ship.get_y()

        # Move the Bullet artificially a bit so it doesn't render inside the ship
        self.x += self.velocity_x * 20
        self.y += self.velocity_y * 20

        # Bullet movement speed factor
        self.velocity_x *= 5
        self.velocity_y *= 5

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

class Application(Frame):
    draw_interval = int((1/60.0) * 1000) # refresh 60 times a second

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(parent, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background='Black')
        self.canvas.pack()
        self.backgroundImage = PhotoImage(file="nebula.gif")
        self.game_over = False

        ship = Ship()
        self.addShip(ship)
        self.asteroids = set([])
        self.level = 1
        self.create_new_wave()

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

        for asteroid in set(self.asteroids):
            asteroid.update()

        #Check for collisions

        for asteroid in set(self.asteroids):
            #Compare each bullet against Asteroid
            bullets = self.ship.get_bullets()
            for bullet in bullets:
                if bullet.is_collision(asteroid):
                    explosion_sound.play()
                    size = asteroid.get_size()
                    if size < 3:
                        a1 = Asteroid(size + 1, asteroid.get_x(), asteroid.get_y(),
                                      asteroid.get_velocity_y() * -2, asteroid.get_velocity_x() * 2)
                        self.asteroids.add(a1)

                        a2 = Asteroid(size + 1, asteroid.get_x(), asteroid.get_y(),
                                      asteroid.get_velocity_y() * 2, asteroid.get_velocity_x() * -2)
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
                    explosion_sound.play()
                    self.ship.remove_live()
                    if self.ship.get_lives() <= 0:
                        self.ship.set_active(False)
                        self.game_over=True
                    else:
                         self.ship.make_inactive_for(350)

        if len(self.asteroids) == 0:
            self.level += 1
            self.create_new_wave()



    def draw(self):
        self.update_objects()
        self.canvas.delete('all')
        self.canvas.create_image(10, 10, image = self.backgroundImage, anchor = NW)
        self.ship.draw(self.canvas)
        for asteroid in self.asteroids:
            asteroid.draw(self.canvas)

        # Show current wave number
        self.canvas.create_text(CANVAS_WIDTH - 40, CANVAS_HEIGHT - 20, text='Wave  ' + str(self.level) , fill="White")

        # Print game over message if needed
        if self.game_over == True:
            self.canvas.create_text(CANVAS_WIDTH/2, CANVAS_HEIGHT/2, text="GAME OVER", fill="White", font=("Purisa", 20) )

        self.parent.after(self.draw_interval, self.draw) # set timer to refresh screen

    #New Wave
    def create_new_wave(self):
        self.ship.activate_shield()
        for i in range(0,self.level + 2):
            self.asteroids.add(Asteroid(1))


root = Tk()
Canvas.create_circle = _create_circle

root.title( "Asteroids")

app = Application(root)


root.mainloop()
