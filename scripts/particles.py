import pygame as pg 
from pygame.locals import *
import random


def circle_surf(radius, color):
	surf = pg.Surface((radius*2, radius*2))
	pg.draw.circle(surf, color, (radius, radius), radius)
	surf.set_colorkey((0,0,0))
	return surf


class Particle:
	def __init__(self, locat, velocity, radius = 5):
		self.locat = locat
		self.velocity = velocity
		self.radius = radius

	def update(self):
		try:
			self.locat[0] += self.velocity[0]
			self.velocity[1] += 0.2
			self.locat[1] += self.velocity[1]
			self.radius -= 0.1
		except:
			print(type(self.locat))
			print(type(self.velocity))


def update_particles(particles, loc, rad, velx):
	particles.append(Particle(locat=loc, velocity=[velx, random.randint(-5,5)/10 -1], radius = rad))
	
	for particle in particles:
		if particle.radius <= 0:
			particles.remove(particle)
		
		particle.update()

	return particles