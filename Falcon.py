from EnemyShip import *
FALCON_SCORE = 750

class Falcon(EnemyShip):
    def __init__(self, canvas_width, canvas_height, player_ship, config):

        EnemyShip.__init__(self, canvas_width, canvas_height, player_ship, config)
        speed = config["falcon_speed"]
        self.speed = speed
        self.radius = 20

        self.shape = ((20,5), (20,10), (15,10), (5,20), (-10,20), (-20,10), (-20,-10), (-10,-20), (5,-20), (15,-10),
                      (20,-10), (20,-5), (10,-5), (10,5), (20,5))

        self.set_initial_position_and_velocity()
        self.interval = 1000
        self.update()

    def get_points(self):
        return FALCON_SCORE

    def update(self):
        current_time = get_current_time()

        if current_time > self.last_changed + self.interval:
            x = self.player_ship.get_x() - self.x
            y = self.player_ship.get_y() - self.y
            radians = math.atan2(y,x)
            self.angle = math.degrees(radians)
            self.velocity_x = self.speed * math.cos(radians)
            self.velocity_y = self.speed * math.sin(radians)
            self.last_changed=get_current_time()

        EnemyShip.update(self)
