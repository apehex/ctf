> Three vertices.Two csv files.One solution.

> Author: **[UbiquitousT][author-profile]**

## The challenge

We're given a 100 x 100 bidimensional grid with a single character at each "pixel":

```shell
wc sources/grid.csv 
  # 100   100 20344 sources/grid.csv
```

The flag is a serie of points on this grid:

```python
flagLocation.append([1,2]) # H
flagLocation.append([2,2]) # T
flagLocation.append([3,2]) # B
flagLocation.append([4,2]) # {
flagLocation.append([55,2]) # f
flagLocation.append([65,2]) # a
flagLocation.append([75,2]) # k
flagLocation.append([85,2]) # e
```

The coordinates are not directly given, they're fuzzed:

```python
x1 = random.randint(-7,7)
y1 = random.randint(-7,7)
x2 = random.randint(-7,7)
y2 = random.randint(-7,7)
x3 = random.randint(-7,7)
y3 = random.randint(-7,7)

p1 = [cap(x1 + x), cap(y1 + y)]
p2 = [cap(x2 + x), cap(y2 + y)]
p3 = [cap(x3 + x), cap(y3 + y)]
```

Instead, we know the distances from the target nodes to three neighbors:

```python 
distances = [(val1,getDistance(x,y,p1[0], p1[1])),(val2,getDistance(x,y,p2[0], p2[1])),(val3,getDistance(x,y,p3[0], p3[1])),(f"{val1}{val2}",getDistance(p1[0], p1[1],p2[0], p2[1])),(f"{val2}{val3}",getDistance(p2[0], p2[1],p3[0], p3[1])),(f"{val1}{val3}",getDistance(p1[0], p1[1],p3[0], p3[1]))]
```

Also the characters at the nodes are not unique:

```shell
grep -aic '(' sources/grid.csv 
# 67
```

Here, there are 67 candidates for the node "(".

The lines have irregular length (instead of the strict 199), because the delimiter `,` is sometimes encoded with quotes `","`.

## Parsing the data

The data is formated as comma separated csv, very straightforward:

```python
with open('grid.csv') as _f:
    for x in csv.reader(_f, delimiter=','):
        GRID.append(x)
```

The hints:

```python
with open('out.csv') as _f:
    __measures = []
    for x in csv.reader(_f, delimiter=','):
        __measures.append((x[0], round(float(x[1]), 4)))
        if len(__measures) == 6:
            MEASURES.append(copy.deepcopy(__measures))
            __measures = []
```

## Computing the neighbors

The fuzzed points are always localized in a 15 by 15 square centered on the flag nodes.

To determine whether a given node is part of the flag, we compute this neighborhood for every node on the grid.

The process for a single node looke like this:

```python
def neighbors(grid: list, x: int, y: int) -> list:
    __distances = {}
    for i in range(cap(x - 7), cap(x + 8)):
        for j in range(cap(y - 7), cap(y + 8)):
            __d2 = round(d2(x, y, i , j), 4)
            if __d2 not in __distances:
                __distances[__d2] = {'nodes': [], 'locations': []}
            __distances[__d2]['nodes'].append(grid[i][j])
            __distances[__d2]['locations'].append((i, j))
    return __distances
```

It is at most 225 calculations per node, versus 10000 if we computed all the distances for all the 10000<sup>2</sup> couples of points. 

## Computing the candidates

Then this "field" data can be used to determine if a given point on the grid satisfies all the distances to be part of the flag:

```python
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
    # 1) all 3 target characters are surrounding the current node, at the right distances
    __is_candidate = (
        __d1 in node
        and __d2 in node
        and __d3 in node
        and __v1 in node[__d1]['nodes']
        and __v2 in node[__d2]['nodes']
        and __v3 in node[__d3]['nodes'])
    # 2) those 3 points have the right distances between themselves
    if __is_candidate:
        # note: there may be more than one matching point for each value; all of these have to be tested
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
```

In short, the point has to:

1) be surrounded by all 3 characters specified in the "out" file
2) have those 3 points spread around as measured in that same file

Since those criteria are very restrictive, we expect only one point to match each flag character: 

```python
print(''.join([candidates(FIELD, __m)[0] for __m in MEASURES]))
```

> `HTB{sQU@r3s_R_4_N3rD$}`

And it worked!

## Further improvements

Actually there is no need to compute the neighborhood for every point, once is enough.

Indeed, the coordinate deltas are always related to the distance in the same way. For any point on the grid, it is possible to infer the position of candidates directly from the distance:

```python
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
```

And then update the `is_candidate` function accordingly.

[author-profile]: https://app.hackthebox.com/users/147141
