"""fichier définissant le terrain de jeu"""
import pygame                   
from pygame.locals import *    
from sys import exit            
from PIL import Image           
from PIL import ImageDraw       # dessin à partir de PIL 

class Ground():
    """
    classe du terrain de jeux défini par un nombre de tuiles (size_factor_X, size_factor_Y)
    """
    
    def __init__(self, map_filenames, size_spriteX=64, size_spriteY=64, nb_spritesX=18, nb_spritesY=12):
        """
        constructeur de la classe qui va initiliaser la fenêtre pygame
        """   
        self.size_spriteX, self.size_spriteY = size_spriteX, size_spriteY       
        self.nb_spritesX, self.nb_spritesY   = nb_spritesX,  nb_spritesY        
        self.nb_pixelsX = self.size_spriteX * self.nb_spritesX                
        self.nb_pixelsY = self.size_spriteY * self.nb_spritesY                 
        self.bloc_size =  self.size_spriteX                                     

        self.path_media = 'assets/Decors/'           # chemin relatif où sont stockées les images décors
        self.path_map = 'map/'                      # chemin relatif où sont stockées les map(les fichiers avec le décor du terrain)
        self.sprites_file_name = 'map_sprites.txt'  # dictionnaire des sprites (tuiles 64*64 pixels)

        # création du dictionnaire des sprites utilisées self.sprites = { 'CODE': 'fileName.png'}
        #     TRUE signifie que la sprite est un bloc infranchissable
        self.sprites, self.sprites_grid = self.read_sprites()
        
        # dictionnaire des images des sprites (format PIL) fabriqué à partir du dictionnaire self.sprites
        self.sprites_pil = { key: Image.open(self.path_media+self.sprites[key]).convert('RGBA')
                                  for key in self.sprites.keys()
                                  if key != '  '
                                }
        self.sprites_pil['  '] = None # ajout de la clé '  ' qui correspond à None (pas d'image)

        # lecture de la 1ère map pour initialiser les matrices d'images et de blocs avec le background
        #  matrix_pil_background[l][c] = image 64*64 pixels ligne l colonne c d'une zone franchissable
        #  matrix_pil_bloc[l][c] = image 64*64 pixels ligne l colonne c concernant un bloc infranchissable
        matrix_pil_background, matrix_pil_bloc, self.matrix_bloc = self.read_map(map_filenames[0])

        #parcours des map_filenames suivants pour fusionner les éléments dans les matrices
        for map_filename in map_filenames[1:] :
            matrix_pil_background_add, matrix_pil_bloc_add, matrix_bloc_add = self.read_map(map_filename)
            for l in range(self.nb_spritesY):
                for c in range(self.nb_spritesX):
                    if  matrix_pil_background_add[l][c] != None : # image non vide
                        matrix_pil_background[l][c] = Image.alpha_composite(matrix_pil_background[l][c], matrix_pil_background_add[l][c])
                        #fusion des blocs non franchissables: si un code d'une MAP est TRUE, alors le code final fusionné est TRUE.
                        if matrix_bloc_add[l][c]:
                           self.matrix_bloc[l][c] = True
                           if matrix_pil_bloc[l][c] == None :
                               matrix_pil_bloc[l][c] = matrix_pil_bloc_add[l][c]
                           else:
                               matrix_pil_bloc[l][c] = Image.alpha_composite(matrix_pil_bloc[l][c], matrix_pil_bloc_add[l][c])

        background_pil = Image.new('RGBA',(self.nb_pixelsX, self.nb_pixelsY), 0) #création d'une image noire de la taille de l'écran
        draw = ImageDraw.Draw(background_pil) 

        for l in range(self.nb_spritesY):
            for c in  range(self.nb_spritesX):
                #construction du background 
                background_pil.paste(matrix_pil_background[l][c], (c*self.size_spriteX, l*self.size_spriteY))
                #dessine un carré bord noir sur chaque tuile
                draw.rectangle( [c*self.size_spriteX, l*self.size_spriteY , (c+1)*self.size_spriteX, (l+1)*self.size_spriteY],
                                outline='black')

        #prépare les masques de zones infranchissables
        self.matrix_mask = [] # matrix_mask[l][c] = masque des tuiles en ligne l et colonne c, 'None' si zone franchissable
        for l in range(self.nb_spritesY):
            self.matrix_mask.append([]) # ligne de masque vierge
            for c in  range(self.nb_spritesX):
                if self.matrix_bloc[l][c]:
                    #encadre la zone avec un carré au bord jaune
                    draw.rectangle( [c*self.size_spriteX, l*self.size_spriteY , (c+1)*self.size_spriteX, (l+1)*self.size_spriteY],
                                    outline='yellow')
                    #calcule le masque correspondantx aux pixels non transparents
                    self.matrix_mask[l].append(pygame.mask.from_surface(
                        pygame.image.fromstring(matrix_pil_bloc[l][c].tobytes(), matrix_pil_bloc[l][c].size, 'RGBA')))
                else:
                    self.matrix_mask[l].append(None)

        #initialisation pygame
        pygame.init()                   
        self.screen = pygame.display.set_mode((self.nb_pixelsX, self.nb_pixelsY),0,32)
        pygame.display.set_caption("TANK")   # titre

        #conversion finale de l'image PIL en image Pygame
        self.background_img = pygame.image.fromstring(background_pil.tobytes(), background_pil.size, 'RGBA')
        
    def isFull(self,grid_pos):
        """ determine s'il y a un obstacle infranchissable sur la map en ligne l, colonne c 
        """
        l,c = grid_pos
        return self.matrix_bloc[l][c]
    
    def read_sprites(self):
        """ lecture des sprites, retourne le dictionnaire des sprites {'code_sprite': 'filename.png'}
            ainsi que le dictionnaires des occupations {'code_sprite':TRUE/FALSE}  TRUE signifie sprite infranchissable
        """
        dic_sprites = {}      
        dic_sprites_grid = {} 
        try:
            # ouverture du fichier Map/map_sprites.txt en lecture seule
            with open(self.path_map + self.sprites_file_name, 'r') as f: 
                for line in f:                  
                    if line[0] != '#':          
                        words = line.split('|') 
                        #on ajoute dans self.map la liste des codes trouvés sauf retour chariot '\n' et sauf entête 'M'
                        try:
                            code = words[1]              
                            file_name = words[2].strip()  # file name de la sprite, avec suppression des espaces
                            try:   #vérification de l'existance du fichier
                                with open(self.path_media + file_name, 'r') as fs:
                                    pass 
                            except:
                                print('Le fichier: "' + self.path_media + file_name+ '" est introuvable.')
                                exit()
                            code_occup = words[4].strip()
                        except: #ficher Map/map_sprites.txt ne respecte pas le bon format
                            print('Le ficher " ' + self.path_map+self.sprites_file_name+'" ne respecte pas le bon format:')
                            print('ligne lue: ', line)
                            exit()
                        dic_sprites[code] = file_name               # ajout de {code : filename} au dictionnaire dic_sprites
                        dic_sprites_grid[code] = (code_occup=='x')  # ajout de {code : True/False} au dictionnaire dic_sprites_grid
                        # ajout de {code: TRUE/FALSE} au dictionnaire correspondant au bloc sur la grille
        except:
            print('Problème avec le fichier: "' + self.path_map+self.sprites_file_name + '"')
            exit()

        #ajout du code '  ' aux dictionnaires, ce code signifiant l'absence d'image
        dic_sprites['  '] = None
        dic_sprites_grid['  '] = False
        return dic_sprites, dic_sprites_grid    
        
    def read_map(self, map_file_name):
        """
        lecture d'un fichier MAP (voir fichier modèle.map)
        """
        # préparation de la matrice des codes map, dimension nb_spirteY lignes * nb_spritesX colonnes
        # matrix_map[l][c] = code sprite
        matrix_map, matrix_pil_background, matrix_pil_bloc  = [] , [], []
        try:
            with open(map_file_name, 'r') as fichier: 
                for line in fichier:                  
                    if line[0] == 'M':          
                        codes = line.split('|')
                        #on ajoute dans self.map la liste des codes trouvés sauf retour chariot '\n' et sauf entête 'M'
                        try:
                            matrix_map.append([c for c in codes if c!='\n' and c[0]!='M']) #liste de codes ajoutés à la map
                        except:
                            print('fichier',map_file_name,'ne respecte pas le bon format')
                            exit()
        except:
            print('Problème de lecture du fichier: "' + map_file_name + '".')
            exit()

        # conversion des codes de matrix_map en matrices d'images grâce au dictionnaires d'images self.sprites_pil
        # matrix_map_pil[l][c] = image ligne l, colonne c
        for l in range(self.nb_spritesY):
            matrix_pil_background.append([]) # ajout d'une ligne vide
            matrix_pil_bloc.append([])       # ajout d'une ligne vide
            for c in range(self.nb_spritesX):
                #ajout de l'image récupérée dans le dictionnaire self.sprites_pil, à partir du code matrix_map[l][c]
                matrix_pil_background[l].append(self.sprites_pil[matrix_map[l][c]])
                if self.sprites_grid[matrix_map[l][c]]: # si le code est un bloc infranchissable (= True)
                    matrix_pil_bloc[l].append(self.sprites_pil[matrix_map[l][c]]) # on le rajoute à matrix_pil_bloc
                else:
                    matrix_pil_bloc[l].append(None) 

        # création matrice des codes True/False pour chaque bloc franchissable ou non
        matrix_bloc =[ [ matrix_pil_bloc[l][c] != None 
                                for c in range(self.nb_spritesX) ]
                                    for l in range(self.nb_spritesY)
                     ]
    
        print(' ... lecture map', map_file_name, len(matrix_pil_background), 'lignes *', len(matrix_pil_background[0]),'colonnes')
        return matrix_pil_background, matrix_pil_bloc, matrix_bloc

    def draw(self):
        """
        méthode de déssin des décors du terrain
        """
        self.screen.blit(self.background_img, (0,0))