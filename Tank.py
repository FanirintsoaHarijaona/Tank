"""fichier définissant les traits du Tank"""
import pygame                     
from pygame.locals import *       
from Ground import * 
from Agent import *    
from Obus import *

#--- TANK
class Tank(Agent):
    """
    classe décrivant un tank: dérive de la classe Agent.
    """

    def __init__(self, terrain, name, l_img_name, human=False, pos=(0,0), nb_rotates=16):
        
        Agent.__init__(self,terrain, name, l_img_name, pos, nb_rotates=64,
                       v=0, vmax=10, accel=0, friction_force=-1, id_img_mask=1)
        self.human = human        # True: joué par un humain
        self.id_shield, self.id_hull, self.id_weapon = 0,1,2 #id image du bouclier, coprs , canon et tir du tank
        self.new_accel = 1 #accélération du tank quand la commande Acceleration est activée
        self.shell = Shell(self.terrain, self, self.name+' shell') # agent "Obus" qui sera activé si tir.
        self.shell_countdown_init = 20    # compte à rebours pour retirer un obus: -1 chaque mouvement
         
    def move(self):
        """
        méthode pour faire bouger le tank
        """
        if self.human:
            key_pressed = pygame.key.get_pressed()   # capture touche pressée
            if (key_pressed[K_LEFT] or key_pressed[K_RIGHT]):
                self.rotates(key_pressed[K_LEFT] - key_pressed[K_RIGHT])
            if (key_pressed[K_s] or key_pressed[K_d]):
                #rotation du canon uniquement si touches pressée  'S'(rotation +1) ou 'D' (rotation-1)
                index_angle_wp =  ((key_pressed[K_s] - key_pressed[K_d]) + self.l_rotation[self.id_weapon]) % self.nb_rotates #nouvel indice d'angle du canon
                angle_wp_rel = ((index_angle_wp-self.l_rotation[self.id_hull])% self.nb_rotates) * 360 / self.nb_rotates
                if (angle_wp_rel<=90 or angle_wp_rel>=270): #le canon ne peut être orienté qu'à 90° par rapport au corps du tank, vers la droite ou vers la gauche
                    self.rotates(key_pressed[K_s] - key_pressed[K_d], self.id_weapon)
            #accélération du tank selon commande d'accélération UP ou DOWN
            self.accel = self.new_accel*( key_pressed[K_UP] - key_pressed[K_DOWN] )

        Agent.move(self)              # nouvelle position et orientation du tank

        if self.shell.countdown > 0:   # l'obus a été tiré
            self.shell.countdown -= 1  # décompte le compte à rebours de l'obus
            self.shell.move()         # anime l'obus

        if self.shell.explosion.booom:   # l'obus tiré a rencontré un obstacle
            self.shell.explosion.move() # anime l'explosion
            

    def changes_shield(self):
        """
        inverse le status actif/inactif du bouclier
        """
        self.l_actif[self.id_shield] = not(self.l_actif[self.id_shield])

    def fire(self):
        """
        tir d'obus si le timing le permet
        """
        if self.shell.countdown == 0 :
            self.shell.timer = 0                                 # remet le timer interne de l'obus à zéro
            self.shell.v = self.shell.vMax                       # vitesse de l'obus = vMax dès le début
            self.shell.pos = self.pos                            # position de l'obus = celle du tank
            self.shell.orient(self.l_rotation[self.id_weapon])   # orientation de l'obus = orientation du canon
            self.shell.countdown = self.shell_countdown_init     # début du compte à rebours
 