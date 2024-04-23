import numpy as np
from itertools import product


def check_square_overlap(sq1_x_range, sq2_x_range, sq1_y_range, sq2_y_range):
    x_overlap = not (sq1_x_range[1] < sq2_x_range[0] or sq1_x_range[0] > sq2_x_range[1])
    y_overlap = not (sq1_y_range[1] < sq2_y_range[0] or sq1_y_range[0] > sq2_y_range[1])
    return x_overlap and y_overlap


def min_and_max_index(list_of_nums):
    mini = min(list_of_nums)
    maxi = max(list_of_nums)
    min_index = list_of_nums.index(mini)
    max_index = list_of_nums.index(maxi)
    return (min_index, max_index), (mini, maxi)


def check_num_in_range(num, rnge):
    return rnge[0] <= num <= rnge[1]


class kdtree:
    master_list = []
    def __init__(self, x_range, y_range, potential_objects, object_limit):
        self.quadrants_of_interest = None
        kdtree.master_list.append(self)
        self.x_range = x_range
        self.y_range = y_range
        self.potential_objects = potential_objects.copy()
        self.objects = []
        self.object_limit = object_limit
        self.children = []
        self.x_mid = (x_range[1] + x_range[0]) / 2
        self.y_mid = (y_range[1] + y_range[0]) / 2

    def add_child(self, child):
        self.children.append(child)

    def add_object(self, object):
        self.objects.append(object)
    def filter_quads(self):
        self.quadrants_of_interest=[quadrant for quadrant in self.master_list if not quadrant.children and quadrant.objects]

    def sort_objects(self):

        for object in self.potential_objects.copy():
            if self.check_object_inside_box(object):
                self.add_object(object)
                object.quadrant = self
                self.potential_objects.remove(object)
        if len(self.objects) > self.object_limit and len(self.children) == 0:
            self.create_children()
            for child in self.children:
                child.sort_objects()

    def create_children(self):
        quadrant_child_boundaries = product(((self.x_range[0], self.x_mid), (self.x_mid, self.x_range[1])),
                                            ((self.y_range[0], self.y_mid), (self.y_mid, self.y_range[1])))
        for combo in quadrant_child_boundaries:
            self.add_child(kdtree(combo[0], combo[1], self.objects, self.object_limit))

    def check_object_inside_box(self, object):
        return check_num_in_range(object.pos[0], self.x_range) and check_num_in_range(object.pos[1], self.y_range)
    def create_quadrant_search(self, query_range, obj):
        query_x_range = (obj.pos[0] - query_range, obj.pos[0] + query_range)
        query_y_range = (obj.pos[1] - query_range, obj.pos[1] + query_range)
        objs_in_range = []
        self.filter_quads()
        for quadrant in self.quadrants_of_interest:
            if check_square_overlap(query_x_range, quadrant.x_range, query_y_range, quadrant.y_range):
                objs_in_range.extend(quadrant.objects)
        return objs_in_range

    def draw_boundaries(self, screen, game_obj):
        boundaries = tuple(product(self.x_range, self.y_range))
        game_obj.draw.line(screen, (3, 65, 5), boundaries[0], boundaries[1], 2)
        game_obj.draw.line(screen, (3, 65, 5), boundaries[0], boundaries[2], 2)
        game_obj.draw.line(screen, (3, 65, 5), boundaries[-1], boundaries[1], 2)
        game_obj.draw.line(screen, (3, 65, 5), boundaries[-1], boundaries[2], 2)
