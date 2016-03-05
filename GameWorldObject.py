__author__ = 'Matthew'
import math

class GameWorldObject:

    def __init__(self, canvas_width, canvas_height):
        self.colour = "White"
        self.points = list()
        self.angle = 0
        self.shape = list()
        self.x = 0
        self.velocity_x = 0
        self.y = 0
        self.velocity_y = 0
        self.radius = 0
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.drag_factor = 0

    def draw(self, canvas):
        canvas.create_polygon(self.points, fill='', outline=self.colour)

    def update(self):
        self._update_position()
        self._set_points()

    def _set_points(self):
        self.points = self._calc_points(self.shape, self.angle)

    def _calc_points(self, shape, angle):
        radians = angle * math.pi / 180.0
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
            self.x += self.canvas_width
        elif self.x > self.canvas_width:
            self.x -= self.canvas_width

        if self.y < 0:
            self.y += self.canvas_height
        elif self.y > self.canvas_height:
            self.y -= self.canvas_height

    def get_angle(self):
        return self.angle

    def get_x(self):
        return self.x

    def set_x(self,x):
        self.x = x

    def get_y(self):
        return self.y

    def set_y(self,y):
        self.y = y

    def get_velocity_x(self):
        return self.velocity_x

    def set_velocity_x(self,velocity_x):
        self.velocity_x = velocity_x

    def get_velocity_y(self):
        return self.velocity_y

    def set_velocity_y(self,velocity_y):
        self.velocity_y = velocity_y

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

    def set_radius(self,radius):
        self.radius = radius