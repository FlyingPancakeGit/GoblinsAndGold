from settings import *

import noise


class Mine:
    def __init__(self):
        self.size = MINE_SIZE
        self.scale = 100.0
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0

        self.mine = []

    def generate_mine(self):
        self.mine = []

        for i in range(self.size):
            i_list = []
            for j in range(self.size):
                i_list.append(noise.pnoise2(i / self.scale,
                                                 j / self.scale,
                                                 octaves=self.octaves,
                                                 persistence=self.persistence,
                                                 lacunarity=self.lacunarity,
                                                 repeatx=1024,
                                                 repeaty=1024,
                                                 base=3))
            self.mine.append(i_list)

    def mine_loop(self):
        self.generate_mine()
        return self.mine