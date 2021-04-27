import pygame as pg
from pygame.locals import *


class Entity:
	def __init__(self, x, y, sprite):
		self.x = x
		self.y = y
		self.sprite = sprite   #Surface type
		self.rect = pg.Surface.get_rect(sprite)

	def move(self):
		self.x -= 1

	def update(self):
		pass