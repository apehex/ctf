import copy
import csv
import math
import random

################################################################# current guess

FLAG = "HTB{fake_flag_for_testing}"
CANDIDATES = ['']
GRID = []
FIELD = []
MEASURES = []

################################################################# load the grid

with open('grid.csv') as _f:
    for x in csv.reader(_f, delimiter=','):
        GRID.append(x)

############################################################# load the measures

with open('out.csv') as _f:
    __measures = []
    for x in csv.reader(_f, delimiter=','):
        __measures.append((x[0], round(float(x[1]), 4)))
        if len(__measures) == 6:
            MEASURES.append(copy.deepcopy(__measures))
            __measures = []

################################################################### coordinates

def cap(num):
    return max(0, min(99,num))

################################################ check the coherence of a guess

def check(guess: str, locations: list) -> bool:
    return (
        len(guess) == len(locations)
        and all([GRID[locations[i][0]][locations[i][1]] == guess[i] for i in range(len(guess))]))

####################################################### computing the neighbors

def d2(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

def neighbors(grid: list, x: int, y: int) -> dict:
    __distances = {}
    for i in range(cap(x - 7), cap(x + 8)):
        for j in range(cap(y - 7), cap(y + 8)):
            __d2 = round(d2(x, y, i, j), 4)
            if __d2 not in __distances:
                __distances[__d2] = {'nodes': [], 'locations': []}
            __distances[__d2]['nodes'].append(grid[i][j])
            __distances[__d2]['locations'].append((i, j))
    return __distances

def process(grid: list):
    __field = []
    for i in range(100):
        __line = []
        for j in range(100):
            __line.append(neighbors(grid, i, j))
        __field.append(__line)
    return __field

#################################################### identifying the candidates

def is_candidate(node: dict, measures: list) -> bool:
    __v1, __d1 = measures[0]
    __v2, __d2 = measures[1]
    __v3, __d3 = measures[2]
    __d1 = round(__d1, 4)
    __d2 = round(__d2, 4)
    __d3 = round(__d3, 4)
    __d12 = round(measures[3][1], 4)
    __d23 = round(measures[4][1], 4)
    __d13 = round(measures[5][1], 4)
    __is_candidate = (
        __d1 in node
        and __d2 in node
        and __d3 in node
        and __v1 in node[__d1]['nodes']
        and __v2 in node[__d2]['nodes']
        and __v3 in node[__d3]['nodes'])
    if __is_candidate:
        __i1 = [__i for __i, __v in enumerate(node[__d1]['nodes']) if __v == __v1]
        __i2 = [__i for __i, __v in enumerate(node[__d2]['nodes']) if __v == __v2]
        __i3 = [__i for __i, __v in enumerate(node[__d3]['nodes']) if __v == __v3]
        __p1s = [node[__d1]['locations'][__i] for __i in __i1]
        __p2s = [node[__d2]['locations'][__i] for __i in __i2]
        __p3s = [node[__d3]['locations'][__i] for __i in __i3]
        __d12s = [__d12 == round(d2(__p1[0], __p1[1], __p2[0], __p2[1]), 4) for __p1 in __p1s for __p2 in __p2s]
        __d23s = [__d23 == round(d2(__p2[0], __p2[1], __p3[0], __p3[1]), 4) for __p2 in __p2s for __p3 in __p3s]
        __d13s = [__d13 == round(d2(__p1[0], __p1[1], __p3[0], __p3[1]), 4) for __p1 in __p1s for __p3 in __p3s]
        __is_candidate = (
            any(__d12s)
            and any(__d23s)
            and any(__d13s))
    return __is_candidate

def candidates(field: list, measures: list):
    __candidates = []
    for __l in field:
        for __n in __l:
            if is_candidate(__n, measures):
                __candidates.append(__n[0.]['nodes'][0])    # the current node is its own neighbor, at a distance of 0
    return __candidates

######################################################### piece it all together

FIELD = process(GRID)

print(''.join([candidates(FIELD, __m)[0] for __m in MEASURES]))

################################################################ another method

def _deltas() -> dict:
    __distances = {}
    for i in range(-7, 8):
        for j in range(-7, 8):
            __d2 = round(d2(0., 0., i , j), 4)
            if __d2 not in __distances:
                __distances[__d2] = []
            __distances[__d2].append((i, j))
    return __distances

def neighbors(x: int, y: int, d: float, deltas: list) -> list:
    return [(cap(x + __i), cap(y + __j)) for __i, __j in deltas[round(d, 4)]]

def nodes(coordinates: list, grid: list) -> list:
    return [grid[__n[0]][__n[1]] for __n in coordinates]

def is_candidate(x: int, y: int, grid: list, measures: list, deltas: list) -> bool:
    __v1, __d1 = measures[0]
    __v2, __d2 = measures[1]
    __v3, __d3 = measures[2]
    __d1 = round(__d1, 4)
    __d2 = round(__d2, 4)
    __d3 = round(__d3, 4)
    __d12 = round(measures[3][1], 4)
    __d23 = round(measures[4][1], 4)
    __d13 = round(measures[5][1], 4)
    __is_candidate = (
        __d1 in deltas
        and __d2 in deltas
        and __d3 in deltas
        and __v1 in nodes(neighbors(x, y, __d1, deltas), grid)
        and __v2 in nodes(neighbors(x, y, __d2, deltas), grid)
        and __v3 in nodes(neighbors(x, y, __d3, deltas), grid))

DELTAS = _deltas()
