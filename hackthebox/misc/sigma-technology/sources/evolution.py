import itertools
import random
import numpy as np

##################################################################### candidate

def random_pixel(width: int, height: int) -> list:
    return [
        random.randint(0, width - 1),
        random.randint(0, height - 1),
        int(random.gauss(128, 127)) % 256,
        int(random.gauss(128, 127)) % 256,
        int(random.gauss(128, 127)) % 256]

def random_candidate(width: int, height: int, pixels: int=5) -> list:
    return itertools.chain.from_iterable([random_pixel(width, height) for _ in range(pixels)])

#################################################################### population

def random_population(size: int) -> np.array:
    return np.array([[]])

def init_population(config):
    initial_population = list()
    for c in range(config["population_size"]):
        perturbations = list()
        for p in range(config["num_perturbations"]):
            perturbations.append(initialize_random_candidate(config))
        initial_population.append(perturbations)
    return np.array(initial_population)

###################################################################### breeding

def 

def gen_children(fathers, config):
    """
    Args:
        fathers (numpy.ndarray): A tuple is of size 5 containing x, y, r, g, b
    Returns:
        numpy.ndarray: new generation population
    """
    children = list()
    for candidate in fathers:
        r1 = random.randint(0, fathers.shape[0] - 1)
        r2 = random.randint(0, fathers.shape[0] - 1)
        while r2 == r1:
            r2 = random.randint(0, fathers.shape[0] - 1)
        r3 = random.randint(0, fathers.shape[0] - 1)
        while r3 == r2 or r3 == r1:
            r3 = random.randint(0, fathers.shape[0] - 1)
        new_candidate = fathers[r1] + config["scale_factor"] * (fathers[r2] + fathers[r3])
        for i in range(new_candidate.shape[0]):
            new_candidate[i][0] %= config["img_x"]
            new_candidate[i][1] %= config["img_y"]
            new_candidate[i][2] %= 256
            new_candidate[i][3] %= 256
            new_candidate[i][4] %= 256
        children.append(new_candidate)

    return np.array(children)