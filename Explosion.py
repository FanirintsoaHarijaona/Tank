"""fichier décrivant les traits provoqués par le canon d'un tank"""

import pygame                     
from pygame.locals import *       
from Ground import * 
from Agent import *  

class Explosion(Agent):
    """
    classe décrivant une explosion (d'un obus sur un obstacle)
    """

    def __init__(self, terrain, obus, name):
        """
        constructeur de la classe
        """
        
        Agent.__init__(self,terrain, name,
                       l_img_name= ['assets/Tank/Explosion/Sprite_Effects_Explosion_000_64x64.png', # motif explosion 1
                           'assets/Tank/Explosion/Sprite_Effects_Explosion_001_64x64.png', # motif explosion 2
                           'assets/Tank/Explosion/Sprite_Effects_Explosion_002_64x64.png', # motif explosion 3
                           'assets/Tank/Explosion/Sprite_Effects_Explosion_003_64x64.png', # motif explosion 4
                           'assets/Tank/Explosion/Sprite_Effects_Explosion_004_64x64.png', # motif explosion 5
                           'assets/Tank/Explosion/Sprite_Effects_Explosion_005_64x64.png', # motif explosion 6
                           'assets/Tank/Explosion/Sprite_Effects_Explosion_006_64x64.png', # motif explosion 7
                           'assets/Tank/Explosion/Sprite_Effects_Explosion_007_64x64.png', # motif explosion 8
                           'assets/Tank/Explosion/Sprite_Effects_Explosion_008_64x64.png'  # motif explosion 9
                           ]
                       )
        self.desactivates_all()     # désactive toutes les images
        self.booom = False          # True: l'explosion est visible
        
    def move(self):
        """
        méthode pour animer l'explosion
        """
        if self.booom:
            if self.timer>0:
                self.l_actif[self.timer-1] = False     # désactive l'imge précédente
            self.l_actif[self.timer] = True            # active image suivante selon timer interne
            if self.timer == len(self.l_img_name) -1 : # fin de l'explosion
                self.booom = False
                self.desactivates_all()
                self.timer = 0
            Agent.move(self)