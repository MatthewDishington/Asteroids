from GameWorldObject import *
from Utils import *

class Bullet(GameWorldObject):
    def __init__(self, canvas_width, canvas_height, ship, config, x=None, y=None, velocity_x=None, velocity_y=None):
        GameWorldObject.__init__(self, canvas_width, canvas_height)
        self.shape = ((0,0),(0,5))
        self.radius = 2.5

        # Direction of Bullet should be the direction in which the ship is facing
        self.angle = ship.get_angle()

        if velocity_x is None:
            self.velocity_x = math.sin(2 * math.pi * (ship.get_angle()/360.0))
        else:
            self.velocity_x = velocity_x

        if velocity_y is None:
            self.velocity_y = -math.cos(2 * math.pi * (ship.get_angle()/360.0))
        else:
            self.velocity_y = velocity_y

        if x is None:
            #Initial position of the bullet should be the ships center point
            self.x = ship.get_x()
            # Move the Bullet artificially a bit so it doesn't render inside the ship
            self.x += self.velocity_x * 20
        else:
            self.x = x

        if y is None:
            #Initial position of the bullet should be the ships center point
            self.y = ship.get_y()
            # Move the Bullet artificially a bit so it doesn't render inside the ship
            self.y += self.velocity_y * 20
        else:
            self.y = y

        # Bullet movement speed factor
        speed_factor = config['bullet_speed_factor']
        self.velocity_x *= speed_factor
        self.velocity_y *= speed_factor

        # No rotation or rotational speed
        self.rotation_factor = 0
        self.drag_factor = 0

        self.created_time = get_current_time()
        self.time_to_live = 1400
        self.update()

    def set_time_to_live(self,time_to_live):
        self.time_to_live = time_to_live

    def remove(self):
    # Remove a bullet if its Time To Live has expired
        return get_current_time() - self.created_time > self.time_to_live

    def get_radius(self):
        return self.radius

