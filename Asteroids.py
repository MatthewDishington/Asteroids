__author__ = 'Matthew'


from Tkinter import *
import random
import math
import time


CANVAS_WIDTH = 800
CANVAS_HEIGHT = 800

def get_tick_count():
    return int(round(time.time() * 1000))

class GameWorldObject:
    def __init__(self):
        self.colour="White"
        print "Im in GameWorldObject"

    def draw(self, canvas):
        self._update_position()
        self._set_points()
        canvas.create_polygon(self.points, fill='', outline=self.colour)

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


class Ship(GameWorldObject):
    def __init__(self):
        self.colour="White"
        self.acceleration_factor = 0.35
        self.drag_factor = 0.02
        self.rotation_factor = 10

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
        self.max_bullets = 8 # Number of bullets allowed on screen

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

    def draw(self,canvas):
        for bullet in set(self.bullets):
            if bullet.remove():
                self.bullets_used = max(self.bullets_used - 1, 0)
                self.bullets.remove(bullet)

        GameWorldObject.draw(self,canvas)

        for bullet in self.bullets:
            bullet.draw(canvas)


    def fire(self,event):
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

    #Reset cooldown (used when fire key is released)
    def reset_bullet_cooldown(self,event):
        self.last_bullet_time = 0



class Asteroid(GameWorldObject):
    def __init__(self):
        self.colour="Yellow"
        self.drag_factor=0
        minRadius=30
        maxRadius=50
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

        self.x = random.randint(0,CANVAS_WIDTH)
        self.y = random.randint(0,CANVAS_HEIGHT)
        self.angle= random.randint(0,360)
        self.rotation_factor= random.randint(0,100) / 100.0 - 0.5
        self.velocity_x = random.randint(0,100) / 100.0 - 0.5
        self.velocity_y = random.randint(0,100) / 100.0 - 0.5

    def remove(self):
        pass

class Bullet(GameWorldObject):
    def __init__(self,ship):

        self.shape = ((0,0),(0,5))
        self.colour = "White"


        # Direction of Bullet should be the direction in which the ship is facing
        self.angle = ship.get_angle()
        self.velocity_x = math.sin(2 * math.pi * (ship.get_angle()/360.0))
        self.velocity_y = -math.cos(2 * math.pi * (ship.get_angle()/360.0))

        print "Bullet velocity x = ", self.velocity_x
        print "Bullet velocity y = ", self.velocity_y

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

class Application(Frame):
    draw_interval = int((1/60.0) * 1000) # refresh 60 times a second

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack(fill=BOTH, expand=True)
        self.canvas = Canvas(parent, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background='Black')
        self.canvas.pack()
        ship = Ship()
        self.addShip(ship)
        self.asteroids = list()
        for i in range(0,3):
            self.asteroids.append(Asteroid())

        parent.bind('<Left>',ship.rotate_left)
        parent.bind('<Right>',ship.rotate_right)
        parent.bind('<Up>', ship.accelerate)
        parent.bind('<space>', ship.fire)
        parent.bind('<KeyRelease-space>', ship.reset_bullet_cooldown)
        self.draw()

    def addShip(self, ship):
        self.ship = ship

    def draw(self):
        self.canvas.delete('all')
        self.ship.draw(self.canvas)
        for asteroid in self.asteroids:
            asteroid.draw(self.canvas)

        self.parent.after(self.draw_interval, self.draw) # set timer to refresh screen

root = Tk()
root.title( "Asteroids")

app = Application(root)


root.mainloop()
