from settings import *


class Node:
    def __init__(self, pos, parent):
        self.pos = pos
        self.parent = parent

        self.f = 0
        self.g = 0
        self.h = 0

    def __eq__(self, other):
        return self.pos == other.pos

class Pathfinder:
    def __init__(self, mine_size, mine, start, end):
        self.mine_size = mine_size
        self.mine = mine

        self.start_node = Node(start, None)
        self.end_node = Node(end, None)
        self.current_node = None

        self.open_list = []
        self.closed_list = []

    def calc_node_dist(self, start_node, end_node):
        dx = abs(start_node.pos[0] - end_node.pos[0])
        dy = abs(start_node.pos[1] - end_node.pos[1])

        return dy + dx

    def get_neighbours(self, node):
        children = []

        for neighbour_pos in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x = node.pos[0] + neighbour_pos[0]
            y = node.pos[1] + neighbour_pos[1]

            if x < 0 or x > self.mine_size - 1 or 0 > y or y > self.mine_size - 1:
                continue
            if self.mine[x][y] == 'X':
                continue

            new_node = Node((x, y), self.current_node)

            new_node.g = node.g + self.mine[x][y]
            new_node.h = self.calc_node_dist(new_node, self.end_node)
            new_node.f = new_node.g + new_node.h

            if new_node.pos in [node.pos for node in self.closed_list]:
                continue
            if new_node.pos in [node.pos for node in self.open_list]:
                continue

            children.append(new_node)

        return children

    def get_path(self, current_node):
        path = []
        while current_node is not None:
            path.append(current_node.pos)
            current_node = current_node.parent
        return path[::-1]

    def find_path(self):
        self.open_list.append(self.start_node)

        while self.open_list:
            self.current_node = min(self.open_list, key=lambda node: node.f)

            if self.current_node == self.end_node:
                path = self.get_path(self.current_node)
                return path

            self.closed_list.append(self.current_node)
            self.open_list.remove(self.current_node)

            children = self.get_neighbours(self.current_node)

            for child in children:
                self.open_list.append(child)

        return None
