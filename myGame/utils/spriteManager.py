"""
A Singleton Sprite Manager class
Author: Liz Matthews, 7/21/2023

Provides on-demand loading of images for a pygame program.
Will load entire sprite sheets if given an offset.

"""

from pygame import image, Surface, Rect, SRCALPHA, transform
from . import vec
from os.path import join

class SpriteManager(object):
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
    
    # Folder in which images are stored
    _IMAGE_FOLDER = "images"
    
    
    
    ### PROPERTIES TO CHANGE TO ADD NEW IMAGES ###
    
    # Static information about the sprite sizes of particular image sheets.
    _SPRITE_SIZES = {
        "kirby.png" : vec(16,16),
        "waddledee.png" : vec(16,16),
        "Soldier.png" : vec(100,100),
        "Orc.png" : vec(100,100),
        "Monster_Slime-Sheet.png" : vec(96,96),
        "Human_Soldier_Sword_Shield-Sheet.png" : vec(96,96),
        "sickle_sheet.png" : vec(112,64)

    }
    
    # A default sprite size
    _DEFAULT_SPRITE = vec(32,32)
    

    _SCALES = {
        "kirby.png" : 2,
        "waddledee.png" : 2,
        "Soldier.png" : 2,
        "Orc.png" : 2,
        "Monster_Slime-Sheet.png" : 2,
        "Human_Soldier_Sword_Shield-Sheet.png" : 2,
        "sickle_sheet.png" : 2
      
    }
    
    _DEFAULT_SCALE = 1
    
    # A list of images that require to be loaded with transparency
    _TRANSPARENCY = ["Soldier.png", "Orc.png", "Arrow01(32x32).png", "Monster_Slime-Sheet.png", "Human_Soldier_Sword_Shield-Sheet.png", "sickle_sheet.png"]
    
    # A list of images that require to be loaded with a color key
    _COLOR_KEY = ["kirby.png", "waddledee.png"]
    
    # Crop regions within each sprite cell (x, y, width, height) AFTER scaling
    # Use this to trim padding and extract only the character
    _SPRITE_CROPS = {
        "Soldier.png" : Rect(80, 80, 36, 44),
        "Orc.png" : Rect(88, 84, 44, 30),
        "Monster_Slime-Sheet.png" : Rect(78, 84, 30, 30),
        "Human_Soldier_Sword_Shield-Sheet.png" : Rect(66, 78, 45, 40),
        "sickle_sheet.png" : Rect(0, 8, 224, 88)
    }
    
    def __init__(self):
        """Creation of the SpriteManager, sets up storage for surface.
        Can only be called once."""
        if type(self)._INSTANCE != None:
            raise RuntimeError("Cannot create more than one instance of the SpriteManager. Try SpriteManager.getInstance() instead.")
        
        # Stores the surfaces indexed based on file name
        self._full = {}
        self._sprites = {}
        self._rects = {}
    
    
    def getSize(self, fileName):
        # If this sprite has a crop region, return the cropped size
        if fileName in self._SPRITE_CROPS:
            cropRect = self._SPRITE_CROPS[fileName]
            return vec(cropRect.width, cropRect.height)
        
        spriteSize = self._SPRITE_SIZES.get(fileName,
                                            self._DEFAULT_SPRITE)
        return spriteSize * self._SCALES.get(fileName,
                                             self._DEFAULT_SCALE)
    
    def getSprite(self, fileName, offset=None):
        # If this sprite has not already been loaded, load the image from memory
        if fileName not in self._full.keys():
            self._loadImage(fileName, offset)
          
        
        # If the offset is arbitrary, flyweight load the rect offset
        if type(offset) == Rect or (type(offset) in [list, tuple] \
                                    and len(offset) == 4):
            if type(offset) != Rect:
                offset = Rect(offset)
                
            if fileName not in self._rects:
                self._rects[fileName] = {}
                
            if tuple(offset) not in self._rects[fileName]:
                self._rects[fileName][tuple(offset)] = self._loadRect(fileName,
                                                                      offset)
            return self._rects[fileName][tuple(offset)]
        
        # If this is an image sheet, return the correctly offset sub surface
        elif type(offset) in [list, tuple] and len(offset) == 2:
            if fileName not in self._sprites:
                self._loadSpriteSheet(fileName)
                
            return self._sprites[fileName][offset[1]][offset[0]]   
        
        # Otherwise, return the full image
        return self._full[fileName]

    def _applyColorKey(self, fileName, surface):
        if fileName in self._COLOR_KEY:
            surface.set_colorkey(surface.get_at((0,0)))
    
    def _applyTransparency(self, fileName, image=None, rect=None):
        if type(image) == Surface:
            if fileName in self._TRANSPARENCY:
                returnImage = image.convert_alpha()
            else:
                returnImage = image.convert()
        elif type(rect) == Rect:
            if fileName in self._TRANSPARENCY:
                returnImage = Surface(rect.size, SRCALPHA, 32)
            else:
                returnImage = Surface(rect.size)
        else:
            raise TypeError("Cannot apply transparency to types provided.")
            
        
        return returnImage
                
 
    def _loadImage(self, fileName, offset=None):
        # Load the full image      
        fullImage = image.load(join(self._IMAGE_FOLDER, fileName))
       
        fullImage = self._applyTransparency(fileName, image=fullImage)
        
        fullImage = transform.scale_by(fullImage,
                                       self._SCALES.get(fileName,
                                       self._DEFAULT_SCALE))
        
        self._full[fileName] = fullImage
        
        self._applyColorKey(fileName, self._full[fileName])
 
    def _loadRect(self, fileName, rect):
        sprite = self._applyTransparency(fileName, rect=rect)
           
        sprite.blit(self._full[fileName], (0,0), rect)
        
        self._applyColorKey(fileName, sprite)
        
        # Apply crop if specified for file
        if fileName in self._SPRITE_CROPS:
            cropRect = self._SPRITE_CROPS[fileName]
            # Create a new surface of the cropped size
            croppedSprite = self._applyTransparency(fileName,
                                                    rect=Rect(0, 0,
                                                              cropRect.width,
                                                              cropRect.height))
            # Blit the cropped region from sprite onto the new surface
            croppedSprite.blit(sprite, (0, 0), cropRect)
            self._applyColorKey(fileName, croppedSprite)
            return croppedSprite
        
        return sprite
    
    def _loadSpriteSheet(self, fileName):
        self._sprites[fileName] = []
        
        # Use raw frame/cell size for slicing the sheet.
        # (Do not use cropped size here, or grid stepping becomes wrong.)
        spriteSize = self._SPRITE_SIZES.get(fileName,
                                            self._DEFAULT_SPRITE) * \
                     self._SCALES.get(fileName,
                                      self._DEFAULT_SCALE)
        
        # See how big the sprite sheet is
        sheetDimensions = self._full[fileName].get_size()
        
        # Iterate over the entire sheet, increment by the sprite size
        for y in range(0, sheetDimensions[1], int(spriteSize[1])):
            self._sprites[fileName].append([])
            for x in range(0, sheetDimensions[0], int(spriteSize[0])):
                # Add the sprite to the end of the current row
                self._sprites[fileName][-1].append(self._loadRect(fileName,
                                                                  rect=Rect((x,y),
                                                                             spriteSize)))
         
               
            
         