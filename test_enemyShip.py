from unittest import TestCase
from EnemyShip import *
from PlayerShip import *


class TestEnemyShip(TestCase):
    def test_fire(self):
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
        enemy_ship = EnemyShip( 700, 700, ship, config)
        enemy_ship.fire()
        bullets = enemy_ship.get_bullets()

        self.assertEquals(len(bullets), 1)

