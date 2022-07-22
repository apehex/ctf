import time
import itertools
import random
import numpy as np

########################################################################## init

random.seed(time.time())

######################################################################### pixel

def _clip_pixel(pixel: np.ndarray, width: int, height: int) -> list:
    return (
        int(pixel[0]) % width,
        int(pixel[1]) % height,
        int(pixel[2]) % 256,
        int(pixel[3]) % 256,
        int(pixel[4]) % 256)

def clip(candidate: np.ndarray, width: int, height: int) -> np.ndarray:
    return np.array([
        _clip_pixel(pixel=__p, width=width, height=height)
        for __p in candidate])

##################################################################### candidate

def _random_pixel(width: int, height: int) -> list:
    return [
        random.randint(0, width - 1),
        random.randint(0, height - 1),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)]

def random_candidate(width: int, height: int, pixels: int=5) -> np.ndarray:
    return np.array(
        [_random_pixel(width, height) for _ in range(pixels)])

#################################################################### population

def random_population(size: int, width: int, height: int, pixels: int=5) -> np.array:
    return np.array([
        random_candidate(width, height, pixels) for _ in range(size)])

###################################################################### breeding

def mutate():
    pass

def cross(c1: np.ndarray, c2: np.ndarray, c3: np.ndarray, clip: callable, chance: float=0.9, scale: float=0.8) -> np.ndarray:
    __p = np.random.rand(*c1.shape) < chance # array of probabilities to cross each gene
    return clip(c1 + scale * __p * (c2 - c3))

def recombine(population: np.ndarray, clip: callable) -> np.ndarray:
    __next_generation = []
    __current_generation = list(population)
    for __c in __current_generation:
        __c2, __c3 = random.sample(__current_generation, 2)
        __next_generation.append(cross(__c1, __c2, __c3, clip, 0.5))
    return __next_generation

def select(population: np.ndarray, fitness: callable, keep: float=0.3) -> np.ndarray:
    pass

def evolve(population: np.ndarray, generations: int, fitness: callable, clip: callable) -> np.ndarray:
    __current_generation = list(population)
    for __g in range(generations):
        __current_generation = recombine(__current_generation, clip)
    return np.array(__next_generation)
