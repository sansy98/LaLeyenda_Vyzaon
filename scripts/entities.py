import pygame as pg
from pygame.locals import *


class Entity:
	def __init__(self, x, y, sprite):
		self.x = x
		self.y = y
		self.sprite = sprite   #Surface type
		self.rect = pg.Surface.get_rect(sprite)
		self.movement = [0, 0]
		self.direction = 0		#0: left, 1: right
		self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
		self.rect.x = self.x
		self.rect.y = self.y

	def move(self):
		if self.direction == 0:
			self.movement[0] = -1
		elif self.direction == 1:
			self.movement[0] = 1
		if not self.collisions['bottom']:
			self.movement[1] = 2
		else:
			self.movement[1] = 0

	def update(self):
		if self.collisions['left'] and self.direction == 0:
			self.direction = 1
		elif self.collisions['right'] and self.direction == 1:
			self.direction = 0
		self.move()