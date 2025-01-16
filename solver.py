import numpy as np
from collections import defaultdict
from fetch_data import processed_data
from z3 import *

class Tile:
    def __init__(self, tile, tile_id, rotate = True):
        self.tile_id = tile_id
        unique_orient = defaultdict(set)
        rots = 4 if rotate else 1
        for _ in range(rots):
            unique_orient[tile.shape].add(tile.tobytes())
            tile = np.rot90(tile)
        unique_orient = [np.frombuffer(v, dtype=int).reshape(*k) 
                         for k in unique_orient 
                         for v in unique_orient[k]
                        ]
        self.orientations = unique_orient
        f = lambda x: [(i, j) for (i, j), v in np.ndenumerate(x) if v]
        self.repre = [f(tile) for tile in unique_orient]


    def add_constraint(self, s, BRD):
        X, Y = BRD.shape
        tile_condition = []
        for tile, repre in zip(self.orientations, self.repre):
            for i in range(X):
                for j in range(Y):
                    if i + tile.shape[0] <= X and j + tile.shape[1] <= Y:
                        cells = set([(i + x, j + y) for x, y in repre])
                        tile_condition += [And([
                            e == self.tile_id if (tx, ty) in cells else 
                            e != self.tile_id
                            for (tx, ty), e in np.ndenumerate(BRD)
                        ])]
        s += Or(tile_condition)

def get_solver(grid_size, tiles, graph, rotate):
    sx, sy = grid_size
    n = len(tiles)

    s = SolverFor("QF_FD")
    BRD = np.array(IntVector('b', sx*sy), dtype=object).reshape(sx, sy)

    # board constraints
    s += [And(-1<=e, e<n) for e in BRD.flat]
    for tid, tile in tiles.items():
        t = Tile(tile, tid, rotate)
        t.add_constraint(s, BRD)
    
    # adjacency constraints
    for t1 in range(n):
        for t2 in range(t1 + 1, n):
            adj_cond = []
            for x in range(sx):
                for y in range(sy):
                    if x + 1 < sx:
                        adj_cond.append(And(BRD[x, y] == t1, BRD[x+1, y] == t2))
                        adj_cond.append(And(BRD[x, y] == t2, BRD[x+1, y] == t1))
                    if y + 1 < sy:
                        adj_cond.append(And(BRD[x, y] == t1, BRD[x, y+1] == t2))
                        adj_cond.append(And(BRD[x, y] == t2, BRD[x, y+1] == t1))
            s += [graph[t1, t2] == Or(adj_cond)]
    return s, BRD

def get_solns(s, brd, one = True):
    ans = []
    while s.check() == sat:
        m = s.model()
        evalu = np.vectorize(lambda x: m[x].as_long())
        ans.append(evalu(brd) + 1) # adding one back to tiles
        if one:
            break
        s += Or([e!=m[e] for e in brd.flat])
    return ans

def solve(level, one = True):
    grid_size, tiles, graph, rotate = processed_data(level)
    s, brd = get_solver(grid_size, tiles, graph, rotate)
    return get_solns(s, brd, one)