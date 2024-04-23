import pygame
import numpy as np
from kdtree import check_num_in_range,kdtree
import sys
from random import randint

pygame.init()


pygame.display.set_caption("Draggable Turtle")


class Pixel:
    def __init__(self, size, xy_coords, screen_obj,color):
        self.size = size
        self.x_range = (xy_coords[0],xy_coords[0]+10)
        self.y_range = (xy_coords[1],xy_coords[1]+10)
        self.pos = xy_coords
        self.filled = False
        self.screen = screen_obj
        self.color=color
    def check_collision(self,event_pos):
        if check_num_in_range(event_pos[0],self.x_range) and check_num_in_range(event_pos[1],self.y_range):
            return True
        return False

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.pos[0], self.pos[1], self.size, self.size))
        self.filled=True
    def change_pos(self,pos):
        self.pos=pos

class Lava(Pixel):
    def __init__(self,size, xy_coords, screen_obj,color):
        super().__init__(size, xy_coords, screen_obj,color)
        self.size = size
        self.x_range = (xy_coords[0], xy_coords[0] + 10)
        self.y_range = (xy_coords[1], xy_coords[1] + 10)
        self.pos = xy_coords
        self.filled = False
        self.grid_pos=None
        self.screen = screen_obj
        self.color=color

class Grid:
    def __init__(self,grid_size,pixel_size,pygame_obj,pixel_type):
        self.screen = None
        self.pixels = []
        self.grid_matrix=np.zeros(grid_size[::-1],dtype=object)
        self.grid_size=grid_size
        self.pixel_size=pixel_size
        self.x_mid = self.grid_size[0] // 2 * self.pixel_size
        self.y_mid = self.grid_size[1] // 2 * self.pixel_size
        self.quadrants = [[], [], [], []]
        self.height = self.grid_size[1] * self.pixel_size
        self.width = self.grid_size[0] * self.pixel_size
        self.screen = pygame_obj.display.set_mode((self.width, self.height))
        self.filled_pixels=[]
        self.pixel_type=pixel_type

    def set_grid(self):
        for index_x,x in enumerate(range(0, self.width, self.pixel_size)):
            for index_y,y in enumerate(range(0, self.height, self.pixel_size)):
                pixel=self.pixel_type(self.pixel_size, (x, y), self.screen,(12,0,123))
                self.pixels.append(pixel)
                pixel.grid_pos=index_y,index_x
                self.grid_matrix[index_y,index_x]=pixel
                # self.quadrants[int(x>=self.x_mid)+int(y>=self.y_mid)*2].append(pixel)

    def detect_pixel_click(self,event_pos,obj_list):
        for pixel in obj_list:
            if pixel.check_collision(event_pos):
                pixel.draw((23,44,123))
    def falling_pixel(self):
        for pixel in self.filled_pixels:
            if pixel.grid_pos[0]+1>=grid.grid_size[1]:
                continue
            below_pixel=self.grid_matrix[pixel.grid_pos[0]+1,pixel.grid_pos[1]]

            if not below_pixel.filled:
                self.filled_pixels.remove(pixel)
                below_pixel.draw()
                print(below_pixel.filled,pixel.filled)
                below_pixel.filled,pixel.filled=pixel.filled,below_pixel.filled
                print(below_pixel.filled, pixel.filled)
                self.filled_pixels.append(below_pixel)


grid=Grid((80,50),10,pygame,Lava)
grid.set_grid()
tree=kdtree((0,grid.width),(0,grid.height),grid.pixels,30)
tree.sort_objects()
mouse_pressed=False
tree.filter_quads()
mouse_class = type("Object", (), {"pos": None})
mouse_obj = mouse_class()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pressed=True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed=False
    grid.screen.fill((0, 0, 0))
    if mouse_pressed:
        mouse_obj.pos = pygame.mouse.get_pos()
        for pixel in tree.create_quadrant_search(10, mouse_obj):
            if pixel.check_collision(pygame.mouse.get_pos()):
                pixel.draw()
                grid.filled_pixels.append(pixel)
                break
    for pixel in grid.filled_pixels:
        pixel.draw()
    grid.falling_pixel()

    pygame.display.flip()
    # Control the frame rate
    pygame.time.Clock().tick(180)
