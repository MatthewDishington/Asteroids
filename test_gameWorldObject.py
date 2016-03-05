from unittest import TestCase
from GameWorldObject import *

class TestGameWorldObject(TestCase):
    def test__calc_points(self):
        game_object = GameWorldObject(700,700)

        shape = ((10,10),(10,2),(2,2))
        new_shape = game_object._calc_points(shape,90)

        first_point = new_shape[0]
        x = first_point[0]
        y = first_point[1]
        self.assertAlmostEquals(-10,x)
        self.assertAlmostEquals(10,y)

        second_point = new_shape[1]
        x = second_point[0]
        y = second_point[1]
        self.assertAlmostEquals(-2,x)
        self.assertAlmostEquals(10,y)

        third_point = new_shape[2]
        x = third_point[0]
        y = third_point[1]
        self.assertAlmostEquals(-2,x)
        self.assertAlmostEquals(2,y)


    def test__update_position(self):
        # Go off to the left
        game_object = GameWorldObject(700,700)
        game_object.set_velocity_x(-10)
        game_object._update_position()
        x = game_object.get_x()
        self.assertEquals(x,690)

        # Go off to the top
        game_object = GameWorldObject(700,700)
        game_object.set_velocity_y(-10)
        game_object._update_position()
        y = game_object.get_y()
        self.assertEquals(y,690)

        # Go off to the right
        game_object = GameWorldObject(700,700)
        game_object.set_x(690)
        game_object.set_velocity_x(20)
        game_object._update_position()
        x = game_object.get_x()
        self.assertEquals(x,10)

         # Go off to the bottom
        game_object = GameWorldObject(700,700)
        game_object.set_y(690)
        game_object.set_velocity_y(20)
        game_object._update_position()
        y = game_object.get_y()
        self.assertEquals(y,10)

    def test_is_collision(self):
        game_object1 = GameWorldObject(700,700)
        game_object2 = GameWorldObject(700,700)
        game_object3 = GameWorldObject(700,700)

        #Not in Collision
        game_object1.set_x(100)
        game_object1.set_y(100)
        game_object1.set_radius(15)

        game_object2.set_x(150)
        game_object2.set_y(150)
        game_object2.set_radius(20)

        is_collision = game_object1.is_collision(game_object2)
        self.assertFalse(is_collision)

        #In Collision
        game_object3.set_x(50)
        game_object3.set_y(50)
        game_object3.set_radius(50)
        is_collision = game_object1.is_collision(game_object1)
        self.assertTrue(is_collision)
