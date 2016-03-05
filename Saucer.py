from EnemyShip import *
FLYING_SAUCER_SCORE = 500

class Saucer(EnemyShip):
    def __init__(self, canvas_width, canvas_height, player_ship, config):

        EnemyShip.__init__(self, canvas_width, canvas_height, player_ship, config)

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
        min_speed = self.config["saucer_speed_min"]
        max_speed = self.config["saucer_speed_max"]
        self.velocity_x = random.randint(min_speed,max_speed) / 100
        if random.randint(0,1) == 0:
            self.x = 0
        else:
            self.x=self.canvas_width -1
            self.velocity_x *= -1

        self.y = random.randint(0,self.canvas_height)
        self.velocity_y = random.randint(min_speed,max_speed) / 100.0 - 0.5

    def update(self):

        current_time = get_current_time()

        if current_time > self.last_changed + self.interval:
            self.velocity_y *= -1
            self.last_changed=get_current_time()
            self.interval = random.randint(100,5000)

        EnemyShip.update(self)