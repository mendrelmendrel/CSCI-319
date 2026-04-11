"""
A Singleton Sound Manager class
Author: Liz Matthews, 3/18/2026

Provides on-demand loading of sounds and music for a pygame program.

"""

import pygame
import os

class SoundManager(object):
    """A singleton factory class to create and store sprites on demand.
    Do not directly instantiate this class! Use SpriteManager.getInstance()."""
    
    # The singleton instance variable
    _INSTANCE = None
        
    @classmethod
    def getInstance(cls):
        """Used to obtain the singleton instance"""
        if cls._INSTANCE == None:
            cls._INSTANCE = cls()
        
        return cls._INSTANCE
    
    # Construct absolute paths to music and sfx folders
    _BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _SFX_FOLDER = os.path.join(_BASE_PATH, "music")
    _MUSIC_FOLDER = os.path.join(_BASE_PATH, "music")
    
    def __init__(self):
        if type(self)._INSTANCE != None:
            raise RuntimeError("Cannot create more than one instance of the SpriteManager. Try SpriteManager.getInstance() instead.")
    
        pygame.mixer.init()
        self.BGMs = {}
        self.dict = {}
        self.currentlyPlaying = None
    
    def playBGM(self, name):
        if self.currentlyPlaying:
            pygame.mixer.music.stop()
        self.currentlyPlaying = name
        pygame.mixer.music.load(os.path.join(SoundManager._MUSIC_FOLDER,
                                                name))        
        pygame.mixer.music.play(-1)
    
    def fadeoutBGM(self, fadeoutAmount=1000):
        pygame.mixer.music.fadeout(fadeoutAmount)
        self.currentlyPlaying = None
    
    def playSFX(self, name, loops=0):
        try:
            if name not in self.dict:
                self._loadSFX(name)
            return self.dict[name].play(loops)
        except (FileNotFoundError, pygame.error):
            return None
        
    
    def _loadSFX(self, name):
        """Loads a sound from a file."""
        fullname = os.path.join(SoundManager._SFX_FOLDER, name)
        sound = pygame.mixer.Sound(fullname)
            
        self.dict[name] = sound
    
    def stopAllSFX(self):
        for song, player in self.dict.items():
            if song.endswith(".wav"):
                player.stop()