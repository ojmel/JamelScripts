import pygame
import sys
import numpy as np
from random import randint
from math import sqrt

pygame.init()

width, height = 880, 625
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Draggable Turtle")
def create_float_array(iterable):
    if isinstance(iterable,np.ndarray):
        float_array=iterable.astype('float64')
    else:
        float_array=np.array(iterable,dtype='float64')
    return float_array


class Ball:
    def __init__(self, color, radius, screen_size, collision_damp, gravity=None,pos=None):
        if pos is None:
            pos = [width // 2, height // 2]
        if gravity is None:
            gravity=(0, 6)
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
    def correct_penetration(self,other_ball):
        dist = other_ball.pos - self.pos
        dist_magnitude = np.linalg.norm(dist)
        pen_depth = other_ball.radius + self.radius - dist_magnitude
        pen_res = dist / dist_magnitude * pen_depth / 2
        self.pos += -pen_res
        other_ball.pos += pen_res
    def check_collision(self, list_of_balls):

        self.pos = np.clip(self.pos, self.lower_boundaries, self.upper_boundaries)
        for ball in list_of_balls:
            if sqrt((ball.pos[0]-self.pos[0]) ** 2 + (
                    ball.pos[1]-self.pos[1]) ** 2) <= self.radius + ball.radius and ball != self:
                self.correct_penetration(ball)
                self.elastic_collision(ball)

        if not self.dragging:
            if self.energy:
                self.velocity += self.gravity
            self.pos += self.velocity
            # flipping velocity when hitting the top and bottom wall
            if self.pos[1] + self.radius >= self.screen_size[1] or self.pos[1] - self.radius <= 0:
                self.velocity[1] *= -1
            #flipping and potentially lowering velocity when hitting the side walls
            if self.pos[0] >= self.upper_boundaries[0] or self.pos[0] <= self.lower_boundaries[0]:
                self.velocity[0] *= -self.collision_damp
            #keeping ball from experiencing gravity when it has no velocity and is on the floor
            if self.pos[1] >= self.upper_boundaries[1] and abs(self.velocity[1]) <= self.gravity[1]:
                self.energy = False
                self.velocity[1] = 0
            else:
                self.energy=True

        if self.dragging:
            self.energy = True
            self.pos = create_float_array(pygame.mouse.get_pos())
            term_vel=self.terminal_velocity
            self.velocity = np.clip((self.pos - self.previous_pos),create_float_array((-term_vel,-term_vel)),create_float_array((term_vel,term_vel)))


def make_balls(num_of_balls, radius, collision_damp, screen_size):
    balls = []
    for x in range(num_of_balls):
        balls.append(Ball((randint(0, 255), randint(0, 255), randint(0, 255)), radius * 2, screen_size, collision_damp,
                          (0,0),(randint(0, screen_size[0]), randint(0, screen_size[1]))))
    return balls


balls = make_balls(30, 5, 1, (width, height))
# Main game loop

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for ball in balls:
                    turtle_rect = pygame.Rect(ball.pos[0] - ball.diameter / 2, ball.pos[1] - ball.diameter / 2,
                                              ball.diameter, ball.diameter)
                    if turtle_rect.collidepoint(event.pos):
                        ball.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                for ball in balls:
                    ball.dragging = False

    screen.fill((255, 255, 255))
    for ball in balls:
        ball.check_collision(balls)
        ball.previous_pos = ball.pos
        pygame.draw.circle(screen, ball.color, ball.pos, ball.diameter // 2)
        pygame.draw.circle(screen, ball.color, ball.pos, ball.diameter // 2)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)
