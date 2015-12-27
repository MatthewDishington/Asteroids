__author__ = 'Matthew'


from Tkinter import *
import random
import math

CANVAS_WIDTH = 400
CANVAS_HEIGHT = 400

class Ship:

    def __init__(self):

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
        self.reset()

    def reset(self):

        # position at center of canvas
        self.x = CANVAS_WIDTH/2
        self.y = CANVAS_HEIGHT / 2

        self.angle = 0 # orientation

        # speed
        self.velocity_x = 0
        self.velocity_y = 0

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

    def rotate_left(self, event):
        self.angle -= self.rotation_factor

    def rotate_right(self, event):
        self.angle += self.rotation_factor

    def draw(self, canvas):
        self._update_position()
        self._set_points()

        canvas.create_polygon(self.points, fill='', outline='White')

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

    def _update_position(self):

        # update position based on movement speed (velocity speed)

        self.x += self.velocity_x
        self.y += self.velocity_y

        # Use Stoke's law to apply drag to the ship
        self.velocity_x -= self.velocity_x * self.drag_factor
        self.velocity_y -= self.velocity_y * self.drag_factor

        # keep ship in game world  (wrap around borders )
        if self.x < 0:
            self.x += CANVAS_WIDTH
        elif self.x > CANVAS_WIDTH:
            self.x -= CANVAS_WIDTH

        if self.y < 0:
            self.y += CANVAS_HEIGHT
        elif self.y > CANVAS_HEIGHT:
            self.y -= CANVAS_HEIGHT

class Asteroid:
    def __init__(self):
        self.minRadius=30
        self.maxRadius=50
        self.granularity=20
        self.minVary=25
        self.maxVary=75

        self.shape=[]
        angle=0
        while angle < 2 * math.pi:
            angleVaryPc=random.randint(self.minVary, self.maxVary)
            angleVaryRadians= (2 * math.pi / self.granularity) * angleVaryPc / 100
            angleFinal = angle + angleVaryRadians - (math.pi / self.granularity)
            radius= random.randint(self.minRadius, self.maxRadius)
            point=[0,0]
            point[0]= math.sin(angleFinal) * radius
            point[1]= math.cos(angleFinal) * radius
            self.shape.append(point)
            angle += 2 * math.pi / self.granularity



        self.x = random.randint(0,CANVAS_WIDTH)
        self.y = random.randint(0,CANVAS_HEIGHT)
        self.angle= random.randint(0,360)
        self.rotation_factor= random.randint(0,100) / 100.0 - 0.5
        self.velocity_x = random.randint(0,100) / 100.0 - 0.5
        self.velocity_y = random.randint(0,100) / 100.0 - 0.5



    def draw(self, canvas):
        self._update_position()
        self._set_points()
        canvas.create_polygon(self.points, fill='', outline='White')


    def _update_position(self):
        self.points = list()

        # update position based on movement speed (velocity speed)
        self.x += self.velocity_x
        self.y += self.velocity_y

        #Keep Asteroid in game world
        if self.x < 0:
            self.x += CANVAS_WIDTH
        elif self.x > CANVAS_WIDTH:
            self.x -= CANVAS_WIDTH

        if self.y < 0:
            self.y += CANVAS_HEIGHT
        elif self.y > CANVAS_HEIGHT:
            self.y -= CANVAS_HEIGHT

        #Update rotation
        self.angle += self.rotation_factor


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


    def remove(self):
        pass

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
