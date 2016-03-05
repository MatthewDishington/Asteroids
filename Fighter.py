from EnemyShip import *
FIGHTER_SCORE = 1000

class Fighter(EnemyShip):
    def __init__(self, canvas_width, canvas_height, player_ship, config):
        EnemyShip.__init__(self, canvas_width, canvas_height, player_ship, config)
        speed = config["fighter_speed"]
        self.speed = speed
        self.radius = 20
        self.shape = ((25,0), (5,5), (5,20),(15,20),(-5,20), (0,20), (-5,5), (-10,0), (-5,-5), (0,-20), (-5,-20), (15,-20),
                      (15,-20), (5,-20), (5,-5), (25,0))
        self.max_bullets = 2 # Number of bullets allowed on screen
        self.gun_radius = math.sqrt(15**2 + 20**2)
        self.gun_angle = math.atan2(20,15)
        self.set_initial_position_and_velocity()
        self.interval = 1000
        self.update()

    def fire(self):

        if self.bullets_used < self.max_bullets:

            #Make new bullet
            #Calculate bullet Velocity
            x = self.player_ship.get_x() - self.x
            y = self.player_ship.get_y() - self.y

            radians = math.atan2(x,y)
            bullet_speed = self.config["enemy_ship_bullet_speed"]
            speed = bullet_speed
            velocity_x = speed * math.sin(radians)
            velocity_y = speed * math.cos(radians)


            #Calculate left bullet initial position
            current_gun_angle = math.radians(self.angle) + self.gun_angle
            x = self.x + self.gun_radius * math.cos(current_gun_angle)
            y = self.y + self.gun_radius * math.sin(current_gun_angle)
            bullet = Bullet(self.canvas_width, self.canvas_height,self, self.config, x=x, y=y, velocity_x=velocity_x, velocity_y=velocity_y)
            self.bullets.add(bullet)

            #Calculate right bullet initial position
            current_gun_angle = math.radians(self.angle) - self.gun_angle
            x = self.x + self.gun_radius * math.cos(current_gun_angle)
            y = self.y + self.gun_radius * math.sin(current_gun_angle)
            bullet = Bullet(self.canvas_width, self.canvas_height,self, self.config, x=x, y=y, velocity_x=velocity_x, velocity_y=velocity_y)
            self.bullets.add(bullet)

            #Last bullet fired now
            self.last_bullet_time = get_current_time()
            self.bullets_used += 1

            #Play fire sound
            if Sounds.fire_sound is not None:
                Sounds.fire_sound.play()

    def get_points(self):
        return FIGHTER_SCORE

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