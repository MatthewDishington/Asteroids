from GameWorldObject import *
import random


class Asteroid(GameWorldObject):
    def __init__(self, canvas_width, canvas_height, size, config, x = None, y = None, velocity_x = None, velocity_y = None):
        GameWorldObject.__init__(self,canvas_width,canvas_height)
        if size < 1:
            self.size = 1
        else:
            self.size = size

        self.colour="Yellow"
        self.drag_factor=0
        self.radius= 40 / size
        minRadius = int(self.radius - (10 / size))
        maxRadius = int(self.radius + (10 / size))
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
            self.x = random.randint(0,self.canvas_width)
        else:
            self.x = x

        if y is None:
            self.y = random.randint(0,self.canvas_height)
        else:
            self.y = y

        self.angle= random.randint(0,360)
        self.rotation_factor= random.randint(0,100) / 100.0 - 0.5

        min_speed = config['asteroid_speed_min']
        max_speed = config['asteroid_speed_max']
        if velocity_x is None:
            self.velocity_x = random.randint(min_speed,max_speed) / 100.0 - 0.5
        else:
            self.velocity_x = velocity_x

        if velocity_y is None:
            self.velocity_y = random.randint(min_speed,max_speed) / 100.0 - 0.5
        else:
            self.velocity_y = velocity_y

        self.update() # create the points

    def get_radius(self):
        return self.radius

    def get_size(self):
        return self.size