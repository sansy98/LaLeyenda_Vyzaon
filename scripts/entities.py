import pygame as pg
from pygame.locals import *


class Slider:
	def __init__(self, locat):
		self.locat = locat
		self.rect = Rect(locat, (100, 5))
		self.slRect = Rect(locat[0]+40, locat[1]-3, 10, 10)

	def update(self):
		pass


def update_sliders(sliders):
	sliderSurface = pg.Surface((455, 270))
	for slider in sliders:
		pg.draw.rect(sliderSurface, (128,128,128), slider.rect)
		pg.draw.rect(sliderSurface, (255,255,255), slider.slRect)
	return sliderSurface