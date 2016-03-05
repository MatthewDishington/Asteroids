
import Sounds
from Bullet import *
import random

class EnemyShip(GameWorldObject):
    def __init__(self, canvas_width, canvas_height, player_ship, config):
        GameWorldObject.__init__(self,canvas_width,canvas_height)
        # Bullets:
        self.bullets_used = 0
        self.last_bullet_time = get_current_time()
        self.bullet_interval = random.randint(500,2000)
        self.max_bullets = 1 # Number of bullets allowed on screen
        self.bullets = set()

        self.player_ship = player_ship
        if Sounds.enemy_ship_sound is not None:
            Sounds.enemy_ship_sound.play(loops=-1)

        self.last_changed=get_current_time()
        self.interval = random.randint(100,5000)
        self.drag_factor = 0
        self.colour = 'White'
        self.config = config

    def set_initial_position_and_velocity(self):
        self.velocity_x = random.randint(200,400) / 100
        self.velocity_y = random.randint(200,400) / 100.0 - 0.5
        choice = random.randint(0,3)

        if choice == 0:
            self.x = random.randint(0,self.canvas_width)
            self.y = 0
        elif choice == 1:
            self.x = self.canvas_width
            self.y = random.randint(0,self.canvas_height)
            self.velocity_x *= -1
        elif choice == 2:
            self.x = random.randint(0,self.canvas_width)
            self.y = self.canvas_height
            self.velocity_y *= -1
        else:
            self.x = 0
            self.y = random.randint(0, self.canvas_height)

        radians = math.atan2(self.velocity_y,
                             self.velocity_x)
        self.angle = math.degrees(radians)


    def update(self):

        current_time = get_current_time()

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
            x = self.player_ship.get_x() - self.x
            y = self.player_ship.get_y() - self.y

            radians = math.atan2(x,y)
            bullet_speed = self.config["enemy_ship_bullet_speed"]
            speed = bullet_speed
            velocity_x = speed * math.sin(radians)
            velocity_y = speed * math.cos(radians)

            bullet = Bullet(self.canvas_width, self.canvas_height, self, self.config, velocity_x=velocity_x, velocity_y=velocity_y)
            self.bullets.add(bullet)

            #Last bullet fired now
            self.last_bullet_time = get_current_time()
            self.bullets_used += 1

            #Play fire sound
            if Sounds.fire_sound is not None:
                Sounds.fire_sound.play()

    def remove_bullet(self, bullet):
        self.bullets.remove(bullet)
        self.bullets_used -= 1

    def destroy(self):
        Sounds.enemy_ship_sound.stop()

    def get_bullets(self):
        return list(self.bullets)

    def get_points(self):
        pass