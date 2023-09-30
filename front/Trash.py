#Autor: Ivan Olmos Pineda
#Curso: Multiagentes - Graficas Computacionales

import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from objloader import *
import random
import math

class Trash:
    
    def __init__(self, x, z):
        self.Position = [x, 5.0, z]
        
    def cargar(self):
        global obj
        obj = OBJ("Trash.obj", swapyz=True)
        obj.generate()

    def update(self, new_x, new_z):
        self.Position[0] = new_x
        self.Position[2] = new_z
        
    def draw(self):
        global obj
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        glScaled(5, 5, 5)
        glRotatef(90, -1, 0, 0)
        obj.render()
        glPopMatrix()