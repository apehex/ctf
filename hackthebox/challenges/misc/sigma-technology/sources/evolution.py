import time
import itertools
import random
import numpy as np

########################################################################## init

random.seed(time.time())

######################################################################### pixel

def _clip(candidate: np.ndarray, widht: int, height: int) -> np.ndarray:
    __candidate = candidate
    for __i in range(0, len(__candidate), 5):
        __candidate[__i] = __candidate[__i] % width
        __candidate[__i + 1] = __candidate[__i + 1] % height
        __candidate[__i + 2] = __candidate[__i + 2] % 256
        __candidate[__i + 3] = __candidate[__i + 3] % 256
        __candidate[__i + 4] = __candidate[__i + 4] % 256
    return __candidate

##################################################################### candidate

def random_pixel(width: int, height: int) -> list:
    return [
        random.randint(0, width - 1),
        random.randint(0, height - 1),
        int(random.gauss(128, 127)) % 256,
        int(random.gauss(128, 127)) % 256,
        int(random.gauss(128, 127)) % 256]

def random_candidate(width: int, height: int, pixels: int=5) -> np.ndarray:
    return np.array(list(itertools.chain.from_iterable(
        [random_pixel(width, height) for _ in range(pixels)])))

#################################################################### population

def random_population(size: int, width: int, height: int, pixels: int=5) -> np.array:
    return np.array([list(random_candidate(width, height, pixels)) for _ in range(size)])

###################################################################### breeding

def mutate():
    pass

def cross(c1: np.ndarray, c2: np.ndarray, c3: np.ndarray, fitness: callable, clip: callable, scale: float=0.5, acceptance: float=0.1) -> np.ndarray: 
    __candidate = clip(c1 + scale * (c2 + c3))
    if fitness(__candidate) > fitness(c1) or random.random() <= acceptance:
        return __candidate
    return c1

def evolve(population: np.ndarray, fitness: callable, clip: callable) -> np.ndarray:
    __next_generation = []
    for __c1 in population:
        __c2, __c3 = random.sample(population, 2)
        __next_generation.append(cross(__c1, __c2, __c3, fitness, clip, 0.5, 0.1))
    return np.array(__next_generation)
