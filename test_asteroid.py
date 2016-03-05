from unittest import TestCase
from Asteroid import *

class TestAsteroid(TestCase):
    def test_size_and_radius(self):
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
        asteroid = Asteroid(700, 700, 1, config)
        size = asteroid.get_size()
        self.assertEquals(size, 1)
        radius = asteroid.get_radius()
        self.assertEquals(radius, 40)

        asteroid2 = Asteroid(700, 700, 2, config)
        size = asteroid2.get_size()
        self.assertEquals(size, 2)
        radius = asteroid2.get_radius()
        self.assertEquals(radius, 20)

        asteroid3 = Asteroid(700, 700, 3, config)
        size = asteroid3.get_size()
        self.assertEquals(size, 3)
        radius = asteroid3.get_radius()
        self.assertEquals(radius, 40/3)