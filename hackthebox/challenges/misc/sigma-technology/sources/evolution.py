import time
import itertools
import random
import numpy as np

########################################################################## init

random.seed(time.time())

#################################################################### population

def random_population(size: int, pixels: int=5) -> np.array:
    return np.random.rand(size, pixels, 5)

###################################################################### breeding

def recombine(population: np.ndarray, cr: float=0.8, f: float=0.5) -> np.ndarray:
    __a = np.copy(population)
    __b = np.copy(population); np.random.shuffle(__b)
    __c = np.copy(population); np.random.shuffle(__c)
    __p = np.random.rand(*(population.shape)) < cr # array of probabilities to cross each gene
    return (__a + f * __p *(__b - __c)) % 1. # broadcast to all the pixel values at once

def select(population: np.ndarray, fitness: callable, keep: float=0.3) -> np.ndarray:
    __count = int(keep * population.shape[0])
    __indices = np.argsort(fitness(population))[-__count:]
    return population.take(indices=__indices, axis=0)

def evolve(population: np.ndarray, generations: int, fitness: callable) -> np.ndarray:
    __parents = np.copy(population)
    for g in range(generations):
        print(g, '...')
        __children = recombine(population=__parents, cr=0.8, f=0.5)
        __elite = np.concatenate((
            select(population=__parents, fitness=fitness, keep=0.3),
            select(population=__children, fitness=fitness, keep=0.3)), axis=0)
        __foreigners = random_population(size=(population.shape[0] - __elite.shape[0]), pixels=5)
        __parents = np.concatenate((__elite, __foreigners), axis=0)
    return __parents