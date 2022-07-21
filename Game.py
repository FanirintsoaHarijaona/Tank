#dernière modification:12-08-2021

import pygame                     
from pygame.locals import *       # PYGAME constant & functions
from sys import exit              
from PIL import Image             # bilbiothèque pour traitement d'image
from Ground import *  
from Tank import *       # classe Tank()       
from Obus import *
from Explosion import *    

class Game():
    """
    classe principale du jeux
    """

    def __init__(self, size_spriteX=64, size_spriteY=64, nb_spritesX=18, nb_spritesY=12, fps=30):
        """
        constructeur de la classe
        """
        print('démarrage jeux Tank')
        self.terrain = Ground(map_filenames=['map/tank_background.map', # terrain de jeux avec maps
                                              'map/tank_vegetaux.map',
                                              'map/tank_fondations.map',
                                              'map/tank_fondations2.map',
                                              'map/tank_flags1.map',
                                              'map/tank_flags2.map',
                                              'map/tank_bords.map',
                                              ])  
        self.tanks = []  # liste des tanks
        

        #tank joué au clavier
        self.tanks.append(Tank(self.terrain, 'Tank_human',
                               l_img_name=['assets/Tank/Tank2/Markup_128x128.png',
                                'assets/Tank/Tank2/Hull_02_128x128.png',
                                'assets/Tank/Tank2/Gun_03_128x128.png'],
                               human=True,
                               pos=( (self.terrain.nb_spritesX-3.5) * self.terrain.size_spriteX,
                                     (self.terrain.nb_spritesY-3.5) * self.terrain.size_spriteY)
                            ))
        self.humanTank = self.tanks[0] #tank joué au clavier par un humain

        self.timer = pygame.time.Clock()  # timer pour contrôler le FPS
        self.fps = fps                    # fps = 30 images par seconde
        
    def loop(self):
        """
        boucle infinie  du jeux: lecture des événements et dessin
        """
        while True:
            #lecture des événements Pygame 
            for event in pygame.event.get():  
                if event.type == QUIT:  # evènement click sur fermeture de fenêtre
                    self.destroy()      # dans ce cas on appelle le destructeur de la classe
                elif event.type == KEYDOWN: 
                    if (event.key==K_SPACE):  # activation du bouclier
                        self.humanTank.changes_shield()
                    elif (event.key==K_f):    # tir d'un obus
                        self.humanTank.fire()
                        
            self.timer.tick(self.fps)   #limite le fps
            
            self.terrain.draw()      #dessin du terrain
            
            for tank in self.tanks:        # dessin des tanks et obus tirés
                tank.draw()             # dessine le tank
                if tank.shell.countdown>0: # dessine l'obus s'il a été tiré
                    tank.shell.draw()
                if tank.shell.explosion.booom: # dessine l'explosion de l'obus si activée
                    tank.shell.explosion.draw()
                tank.move()            # fait bouger le tank et l'obus s'il est tiré

            pygame.display.update()     # rafraîchi l'écran

    def destroy(self):
        """
        destructeur de la classe
        """
        print('Bye!')
        pygame.quit() # ferme la fenêtre principale
        exit()        # termine tous les process en cours

# Programme  principal
#----------------------------------------------------------------
if __name__ == '__main__':
    appl=Game() #instanciation d'un objet Game(): le constructeur lance immédiatement le jeux
    try:
        appl.loop()
    except KeyboardInterrupt:  # interruption clavier CTRL-C: appel à la méthode destroy() de appl.
        appl.destroy()