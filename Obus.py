from Agent import *
from Explosion import *

#--- OBUS
class Shell(Agent):
    """
    classe décrivant un obus d'un tank: dérive de la classe Agent.
    """

    def __init__(self, terrain, tank, name):
        """
        constructeur de la classe
            terrain    : le terrain sur lequel évolue l'obus
            tank       : le tank qui a tiré cet obus
            name       : nom de l'agent
            l_img_name : liste des noms des images  devant être dessinées dans l'ordre de la liste
            pos:  position (x,y) du tank (coin haut gauche)
            nb_rotates: nombre de rotations à pré-générer  (rotations par pas de 2pi/nb_rotations)
        """
        self.tank = tank  
        Agent.__init__(self,terrain, name,
                        l_img_name=['assets/Tank/Explosion/Light_Shell_128x128.png',          # obus
                                    'assets/Tank/Explosion/Sprite_Fire_Shots_Shot_A_000.png'  # feux de tir
                                   ],
                        pos=tank.pos, nb_rotates=tank.nb_rotates,v=30, vmax=30, accel=0, friction_force=0)
        self.id_shell = 0   
        self.id_fire = 1    
        self.countdown = 0  # si compte à rebours obus à 0: le tank peut tirer son obus
        self.explosion = Explosion(terrain, self, self.name+' explosion') # agent explosion quand l'obus touche un obstacle
        self.desactivates_all() #sésactive toutes les images
        
    def move(self):
        """
        méthode pour faire bouger l'obus
        """
        self.l_actif[self.id_fire] = (self.timer==0) # boule de feux de tir activée uniquement au tout début, quand timer = 0
        self.l_actif[self.id_shell] = (self.timer>0)
        if self.countdown == 0: # fin du compte à rebours: arrêt et explosion de l'obus.
            self.v=0
        Agent.move(self)
        if self.v==0:        # l'obus a rencontré un obstacle : explosion activée
            self.desactivates_all() #sésactive toutes les images
            self.explosion.pos = (self.pos[0]-self.explosion.half_size+self.half_size,
                                  self.pos[1]-self.explosion.half_size+self.half_size ) # positionne l'explosion centrée sur l'obus
            self.explosion.booom = True   # active l'animation de l'explosion