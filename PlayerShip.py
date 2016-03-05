from Bullet import *
import Sounds

class PlayerShip(GameWorldObject):
    def __init__(self, canvas_width, canvas_height, config):
        GameWorldObject.__init__(self, canvas_width, canvas_height)
        acceleration = config["acceleration_factor"]
        self.acceleration_factor = acceleration
        self.drag_factor = 0.02
        rotation = config["rotation_factor"]
        self.rotation_factor = rotation
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
        self.count = 0
        self.config = config
        self.canvas_width = canvas_width

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

        self.thruster_shape = ( (xTop - xSize/8.0, yTop + ySize - 5),
                            (xTop, yTop +ySize + yIndent - 5),
                            (xTop + xSize/8.0 , yTop + ySize - 5))

        self.bullet_cool_down= 200 # Fire Cool Down (ms)
        self.max_bullets = 4 # Number of bullets allowed on screen

        self.reset()

    def reset(self):

        # position at center of canvas
        self.x = self.canvas_width/2
        self.y = self.canvas_height/ 2

        self.angle = 0 # orientation

        # speed
        self.velocity_x = 0
        self.velocity_y = 0

        self.bullets = set([])
        self.last_bullet_time = 0
        self.bullets_used = 0

        #Make invincible
        self.invincibility = True
        self.last_shield_time = get_current_time()

    def set_active(self,active):
        self.active = active

    def is_active(self):
        return self.active

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
        self.thrust_sound_last_played = get_current_time()
        if not self.thrust_sound_playing:
            self.thrust_sound_playing = True
            Sounds.thrust_sound.play(loops=-1)

    def update(self):
        # check if ship is action
        if self.active == False:
            if get_current_time() < self.reactivate_time:
                return
            self.active = True
            self.reset()

        #Update shield flag
        self.invincibility = (get_current_time() - self.last_shield_time) < self.shield_duration

        for bullet in set(self.bullets):
            if bullet.remove():
                self.bullets_used = max(self.bullets_used - 1, 0)
                self.bullets.remove(bullet)
            else:
                bullet.update()

        GameWorldObject.update(self)

    def draw(self,canvas):

        if self.thrust_sound_playing:
            if get_current_time() - self.thrust_sound_last_played > self.thrust_sound_duration:
                self.thrust_sound_playing = False
                Sounds.thrust_sound.stop()

        #Draw lives
        canvas.create_text(50,20, text='Lives:', fill='White', font=("Purisa", 15))

        for i in range(self.lives):
            canvas.create_circle((i * 15) + 35, 40, 5, fill="Green")

        canvas.create_text(self.canvas_width - 50,20, text='Score:', fill='White', font=("Purisa", 15) )
        canvas.create_text(self.canvas_height - 50,40, text=str(self.score), fill='Blue', font=("Purisa", 15) )

        if self.active:
            GameWorldObject.draw(self,canvas)
            if self.invincibility:
                canvas.create_circle(self.x, self.y,self.radius + 7, outline="White")
            self.draw_thruster(canvas)

            for bullet in self.bullets:
                bullet.draw(canvas)

        #Indicate if shield available
        canvas.create_text(50, self.canvas_height - 20, text='Shield', fill="White", font=("Purisa", 15))
        colour = 'Red'
        if (get_current_time() - self.last_shield_time) > self.shield_cool_down:
            if not self.invincibility:
                colour='Green'
        canvas.create_rectangle(80, self.canvas_height - 15, 90, self.canvas_height - 25, fill=colour)


    def draw_thruster(self, canvas):
        self.count += 1
        self.count = self.count % 10
        if self.thrust_sound_playing:
            if self.count < 5:
                thruster_points = GameWorldObject._calc_points(self, self.thruster_shape, self.angle)
                canvas.create_line((thruster_points[0], thruster_points[1]), fill="White")
                canvas.create_line((thruster_points[1], thruster_points[2]), fill="White")

    def fire(self,event):
        if not self.active:
            return

        # Dont fire unless the cooldown period has expired
        if (get_current_time() - self.last_bullet_time >= self.bullet_cool_down):

            #Dont fire if the maximum number of bullets are already on scren
            if self.bullets_used < self.max_bullets:

                #Make new bullet
                bullet = Bullet(self.canvas_width, self.canvas_height, self, self.config)
                self.bullets.add(bullet)

                #Last bullet fired now
                self.last_bullet_time = get_current_time()
                self.bullets_used += 1

                #Play fire sound
                Sounds.fire_sound.play()

    def add_points(self,points):
        self.score+=points

    def get_score(self):
        return self.score

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
        self.reactivate_time = get_current_time() + milliseconds

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
            if get_current_time() - self.last_shield_time > self.shield_cool_down:
                self.activate_shield()

    def is_invincible(self):
        return self.invincibility

    def activate_shield(self):
        self.invincibility = True
        self.last_shield_time = get_current_time()