import sys
from math import sqrt
from random import randint
import numpy as np
import pygame
import kdtree

#TODO make molecular dynamics
# make pool game
# make slider and simulation gas, liquid, solid by temperature
pygame.init()
width, height = 880, 625
screen_size=(width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Draggable Turtle")


def create_float_array(iterable):
    """Had trouble with integer overflow, so all arrays used as vectors are created or translated as float type"""
    if isinstance(iterable, np.ndarray):
        float_array = iterable.astype('float64')
    else:
        float_array = np.array(iterable, dtype='float64')
    return float_array


class Ball:
    def __init__(self, color, radius, screen_size, collision_damp, gravity=None, pos=None):
        if pos is None:
            pos = [width // 2, height // 2]
        if gravity is None:
            gravity = (0, 0)
        self.color = color
        self.diameter = radius * 2
        self.radius = radius
        self.pos = create_float_array(pos)
        self.previous_pos = pos
        self.screen_size = screen_size
        self.velocity = create_float_array((0, 0))
        self.gravity = create_float_array(gravity)
        self.acceleration = create_float_array((0, 0))
        self.terminal_velocity = 80
        self.lower_boundaries = create_float_array((0 + self.radius, 0 + self.radius))
        self.upper_boundaries = create_float_array((screen_size[0] - self.radius, screen_size[1] - self.radius))
        self.energy = True
        self.dragging = False
        self.collision_damp = collision_damp

    def elastic_collision(self, other_ball):
        r1 = self.radius
        r2 = other_ball.radius
        v1 = (((r1 - r2) / (r1 + r2)) * self.velocity) + (((2 * r2) / (r1 + r2)) * other_ball.velocity)
        v2 = (((r2 - r1) / (r1 + r2)) * other_ball.velocity) + (((2 * r1) / (r1 + r2)) * self.velocity)
        self.velocity = create_float_array(v1)
        other_ball.velocity = create_float_array(v2)

    def correct_penetration(self, other_ball):
        """(Penetration depth of overlapping balls) Function creates for casual collisions where overlap occurs. A
        position vector anti-parallel to the distance variable between 2 overlapping balls is used to push each other
        away"""
        # distance vector between 2 overlapping balls
        dist = other_ball.pos - self.pos
        dist_magnitude = np.linalg.norm(dist)
        # calculating amount of overlap
        pen_depth = other_ball.radius + self.radius - dist_magnitude
        # calculating the vector that will resolve penetration
        pen_res = dist / dist_magnitude * pen_depth / 2
        self.pos += -pen_res
        other_ball.pos += pen_res

    def check_collision(self, list_of_balls):
        self.pos = np.clip(self.pos, self.lower_boundaries, self.upper_boundaries)
        if list_of_balls:
            for ball in list_of_balls:
                # checking for collision
                if sqrt((ball.pos[0] - self.pos[0]) ** 2 + (
                        ball.pos[1] - self.pos[1]) ** 2) <= self.radius + ball.radius and ball != self:
                    self.correct_penetration(ball)
                    self.elastic_collision(ball)

        if not self.dragging:
            # I created this attribute so that the ball would know when it should experience gravity. "Energy" is
            # taken away when the ball hits the floor and will have no more upward velocity. Since the only way for
            # the balls to gain upward velocity is to be dragged by the mouse. Otherwise the ball sporadically tries
            # to go past the boundaries of the screen.
            if self.energy:
                self.velocity += self.gravity
            self.pos += self.velocity
            # flipping velocity when hitting the top and bottom wall
            if self.pos[1] + self.radius >= self.screen_size[1] or self.pos[1] - self.radius <= 0:
                self.velocity[1] *= -1
            # flipping and potentially lowering velocity when hitting the side walls
            if self.pos[0] >= self.upper_boundaries[0] or self.pos[0] <= self.lower_boundaries[0]:
                self.velocity[0] *= -self.collision_damp
            # keeping ball from experiencing gravity when it has no velocity and is on the floor by turning the addition of a gravity vector off with energy attribute
            if self.pos[1] >= self.upper_boundaries[1] and abs(self.velocity[1]) <= self.gravity[1]:
                self.energy = False
                self.velocity[1] = 0
            else:
                self.energy = True

        if self.dragging:
            self.energy = True
            self.pos = create_float_array(pygame.mouse.get_pos())
            term_vel = self.terminal_velocity
            # assigning mouse velocity to the ball after release
            self.velocity = np.clip((self.pos - self.previous_pos), create_float_array((-term_vel, -term_vel)),
                                    create_float_array((term_vel, term_vel)))


def make_balls(num_of_balls, radius_range, collision_damp, screen_size,gravity=0):
    balls = []
    for x in range(num_of_balls):
        balls.append(Ball((randint(0, 255), randint(0, 255), randint(0, 255)), randint(radius_range[0],radius_range[1]), screen_size, collision_damp,
                          (0, gravity), (randint(0, screen_size[0]), randint(0, screen_size[1]))))
    return balls


balls = make_balls(10, (5,80), 1, (width, height))
ball_tree=kdtree.kdtree((0,width),(0,height),balls,10)
ball_tree.sort_objects()ad
# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for ball in balls:
                    # creates bounding box to detect mouse click on ball
                    turtle_rect = pygame.Rect(ball.pos[0] - ball.diameter / 2, ball.pos[1] - ball.diameter / 2,
                                              ball.diameter, ball.diameter)
                    if turtle_rect.collidepoint(event.pos):
                        # switches an attribute so that the ball will follow the mouse while held down
                        ball.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for ball in balls:
                    # ball is not subject to gravity again
                    ball.dragging = False

    screen.fill((255, 255, 255))
    # draws a space partition tree to be used every frame
    ball_tree = kdtree.kdtree((0, width), (0, height), balls, 10)
    ball_tree.sort_objects()

    for ball in balls:
        ball.check_collision(ball_tree.create_quadrant_search(ball.radius*4,ball))
        ball.previous_pos = ball.pos
        pygame.draw.circle(screen, ball.color, ball.pos, ball.radius)
    # for quadrant in ball_tree.master_list:
    #     quadrant.draw_boundaries(screen,pygame)
    # clears quadrant master list for memory
    ball_tree.master_list.clear()
    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)
