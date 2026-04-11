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

    _FILE_ALIASES = {
        "soldierT.png": "soldiersprite.png",
        "Soldier.png": "soldiersprite.png",
        "SoldierSprite.png": "soldiersprite.png",
    }
    
    
    
    ### PROPERTIES TO CHANGE TO ADD NEW IMAGES ###
    
    # Static information about the sprite sizes of particular image sheets.
    _SPRITE_SIZES = {
        "kirby.png" : vec(16,16),
        "waddledee.png" : vec(16,16),
        "Soldier.png" : vec(100,100),
        "soldierT.png" : vec(100,100),
        "soldiersprite.png" : vec(100,100),
        "Knight.png" : vec(100,100),
        "Orc.png" : vec(100,100),
        "Monster_Slime-Sheet.png" : vec(96,96),
        "Human_Soldier_Sword_Shield-Sheet.png" : vec(96,96),
        "sickle_sheet.png" : vec(112,64),
        "Tilemap_color2.png" : vec(192,192),
        "Tree1.png" : vec(121,190),
        "Boulder.png" : vec(17,14),
        "boulder2.png" : vec(100,100),
        "bush_1.png" : vec(225,225),
        "bush2.png" : vec(16,16),
        "Bush3.png" : vec(16,16),
        "Bush4.png" : vec(16,16),
        "heart.rotate.png" : vec(32,32)

    }
    
    # A default sprite size
    _DEFAULT_SPRITE = vec(32,32)
    

    _SCALES = {
        "kirby.png" : 2,
        "waddledee.png" : 2,
        "Soldier.png" : 2,
        "soldierT.png" : 2,
        "soldiersprite.png" : 2,
        "Knight.png" : 2,
        "Orc.png" : 2,
        "Monster_Slime-Sheet.png" : 2,
        "Human_Soldier_Sword_Shield-Sheet.png" : 2,
        "sickle_sheet.png" : 2,
        "Tilemap_color2.png" : 1,
        "Tree1.png" : 1,
        "Boulder.png" : 1,
        "boulder2.png" : 1,
        "bush_1.png" : 0.16,
        "bush2.png" : 1,
        "Bush3.png" : 1,
        "Bush4.png" : 1,
        "heart.rotate.png" : 1
      
    }
    
    _DEFAULT_SCALE = 1
    
    # A list of images that require to be loaded with transparency
    _TRANSPARENCY = ["Soldier.png", "soldierT.png", "soldiersprite.png", "Knight.png", "Orc.png", "Arrow01(32x32).png", "Monster_Slime-Sheet.png", "Human_Soldier_Sword_Shield-Sheet.png", "sickle_sheet.png", 'Tilemap_color2.png', "heart.rotate.png", "Boulder.png", "boulder2.png", "bush_1.png", "bush2.png", "Bush3.png", "Bush4.png"]
    
    # A list of images that require to be loaded with a color key
    _COLOR_KEY = ["kirby.png", "waddledee.png", "Tree1.png", "boulder2.png", "bush_1.png"]
    
    # Crop regions within each sprite cell (x, y, width, height) AFTER scaling
    # Use this to trim padding and extract only the character
    _SPRITE_CROPS = {
        "Soldier.png" : Rect(72, 66, 68, 54),
        "soldierT.png" : Rect(60, 52, 92, 76),
        "soldiersprite.png" : Rect(60, 52, 92, 76),
        "Knight.png" : Rect(22, 48, 180, 80),
        "Orc.png" : Rect(84, 79, 48, 36),
        "Monster_Slime-Sheet.png" : Rect(70, 82, 44, 44),
        "Human_Soldier_Sword_Shield-Sheet.png" : Rect(66, 78, 48, 44),
        "sickle_sheet.png" : Rect(0, 8, 224, 88),
        "heart.rotate.png" : Rect(3, 3, 27, 27)
    }

    TILEMAP_COLOR2_RECTS = {
        "PLAIN_GRASS_BLOCK" : (0, 0, 192, 192),
        "PLAIN_GRASS_STRIP_RIGHT" : (112, 0, 48, 160),
        "HORIZONTAL_GRASS_PLATFORM" : (0, 160, 112, 80),
        "SMALL_GRASS_SQUARE" : (112, 160, 48, 80),
        "LEFT_SLOPE" : (0, 240, 80, 160),
        "RIGHT_SLOPE" : (112, 240, 48, 160),
        "TOP_CLIFF_GRASS_LARGE" : (256, 0, 112, 160),
        "TOP_CLIFF_GRASS_SIDE" : (368, 0, 48, 160),
        "STONE_WALL_MIDDLE_LARGE" : (256, 160, 112, 160),
        "STONE_WALL_MIDDLE_SIDE" : (368, 160, 48, 160),
        "STONE_WALL_BOTTOM_LARGE" : (256, 320, 112, 80),
        "STONE_WALL_BOTTOM_SIDE" : (368, 320, 48, 80)
    }

    TREE1_RECTS = {
        "TREE_1" : (36, 51, 121, 190)
    }

    TREE1_ANIMATION_RECTS = [
        (36, 51, 121, 190),
        (228, 51, 121, 190),
        (420, 51, 121, 190),
        (612, 51, 121, 190),
        (804, 51, 121, 190),
        (996, 51, 121, 190),
        (1188, 51, 121, 190),
        (1380, 51, 121, 190)
    ]

    def getTilemapColor2Rect(self, tileName):
        if tileName not in self.TILEMAP_COLOR2_RECTS:
            raise KeyError(f"Unknown Tilemap_color2 tile name: {tileName}")

        return self.TILEMAP_COLOR2_RECTS[tileName]

    def getTilemapColor2Sprite(self, tileName):
        rect = self.getTilemapColor2Rect(tileName)
        return self.getSprite("Tilemap_color2.png", rect)

    def getTree1Rect(self, treeName):
        if treeName not in self.TREE1_RECTS:
            raise KeyError(f"Unknown Tree1 sprite name: {treeName}")

        return self.TREE1_RECTS[treeName]

    def getTree1Sprite(self, treeName="TREE_1"):
        rect = self.getTree1Rect(treeName)
        return self.getSprite("Tree1.png", rect)

    def getTree1AnimationSprites(self):
        return [self.getSprite("Tree1.png", rect)
                for rect in self.TREE1_ANIMATION_RECTS]

    def getHeartRotateSprites(self):
        fileName = "heart.rotate.png"
        fullSheet = self.getSprite(fileName)
        spriteSize = self._SPRITE_SIZES.get(fileName,
                                            self._DEFAULT_SPRITE) * \
                     self._SCALES.get(fileName,
                                      self._DEFAULT_SCALE)

        columns = int(fullSheet.get_width() // spriteSize[0])
        return [self.getSprite(fileName, (frame, 0))
                for frame in range(columns)]
    
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
        fileName = self._resolveFileName(fileName)
        # If this sprite has a crop region, return the cropped size
        if fileName in self._SPRITE_CROPS:
            cropRect = self._SPRITE_CROPS[fileName]
            return vec(cropRect.width, cropRect.height)
        
        spriteSize = self._SPRITE_SIZES.get(fileName,
                                            self._DEFAULT_SPRITE)
        return spriteSize * self._SCALES.get(fileName,
                                             self._DEFAULT_SCALE)
    
    def getSprite(self, fileName, offset=None):
        fileName = self._resolveFileName(fileName)
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

    def _resolveFileName(self, fileName):
        return self._FILE_ALIASES.get(fileName, fileName)

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
         
               
            
         