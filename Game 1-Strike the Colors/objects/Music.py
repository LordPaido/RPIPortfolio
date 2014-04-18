import pygame


class Music:
    """Wrapper for pygame sound to play music"""
    def __init__(self, file):
        self.music = pygame.mixer.Sound(file)
        self.music.set_volume(0.5)	
    def play(self, loops=0):
        self.music.play(loops)	
    def stop(self):
        self.music.stop()	
    def pause(self):
        pygame.mixer.pause()
    def unpause(self):
        pygame.mixer.unpause()
	
