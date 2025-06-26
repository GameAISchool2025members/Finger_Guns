import math
import random

import sdl2
import sdl2.ext

SCREEN_W = 1920
SCREEN_H = 1080
FRAMERATE = 60


def draw_rect(renderer, center, w, h, color):
    rect = sdl2.SDL_Rect(center[0] - int(w / 2), center[1] - int(h / 2), w, h)
    renderer.fill(rect, color=color)

def draw_circle(renderer, center, radius, color, thickness):
    renderer.color = color
    for tick in range(0, thickness):
        for angle in range(0, 360):
            rad = math.radians(angle)
            x = int(center[0] + (radius + tick) * math.cos(rad))
            y = int(center[1] + (radius + tick) * math.sin(rad))
            renderer.draw_point([x, y])

def draw_scope(renderer, center, radius, color, thickness):
    draw_rect(renderer, center, radius, thickness, color)
    draw_rect(renderer, center, thickness, radius, color)
    draw_circle(renderer, center, radius, color, thickness)

def trigger_value(index_knuckle, thumb_tip):
    return math.sqrt((index_knuckle.x - thumb_tip.x) ** 2 + (index_knuckle.y - thumb_tip.y) ** 2 + (index_knuckle.z - thumb_tip.z) ** 2)