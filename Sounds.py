import pygame

fire_sound = None
thrust_sound = None
explosion_sound = None
enemy_ship_sound = None
sounds_loaded = False

def load_sounds():

    global fire_sound, thrust_sound, explosion_sound, enemy_ship_sound, sounds_loaded

    if not sounds_loaded:
        # pygame.init()
        pygame.mixer.init()

        fire_sound = pygame.mixer.Sound('fire.wav')
        thrust_sound = pygame.mixer.Sound('thrust.wav')
        explosion_sound = pygame.mixer.Sound('explosion.wav')
        enemy_ship_sound = pygame.mixer.Sound('saucer.wav')

        sounds_loaded = True

def stop_sounds():

    if sounds_loaded:
        fire_sound.stop()
        thrust_sound.stop()
        explosion_sound.stop()
        enemy_ship_sound.stop()