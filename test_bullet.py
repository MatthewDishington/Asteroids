from unittest import TestCase
from PlayerShip import *
from Bullet import *

class TestBullet(TestCase):
    def test_remove(self):
        config={"bullet_speed_factor": 10,
            "asteroid_speed_min": 100,
            "asteroid_speed_max": 150,
            "high_scores_size": 65,
            "scores_size": 25,
            "rotation_factor": 20,
            "acceleration_factor": 0.7,
            "label_and_entry_box_size": 20,
            "enemy_ship_bullet_speed": 1.2,
            "saucer_speed_min": 200,
            "saucer_speed_max": 400,
            "falcon_speed": 3,
            "fighter_speed": 3
                 }

        ship = PlayerShip(700, 700, config)
        bullet = Bullet(700, 700, ship, config)

        time_to_live = -1

        bullet.set_time_to_live(time_to_live)

        self.assertTrue(bullet.remove())
