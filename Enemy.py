import utils
import random

DEFAULT_SIZE = 0.3 * utils.SCREEN_H
MAX_SIZE = 0.6 * utils.SCREEN_H
MAX_SPEED = 0.003 * utils.SCREEN_H
SHIFT_DURATION = 30
SHIFT_SUPPRESSION = 90
FLIP_INTERVAL = 15
class Enemy:
    def __init__(self, controller, sprite_h, sprite_t, sprite_l, x):
        self.controller = controller
        self.sprite_h = sprite_h
        self.sprite_t = sprite_t
        self.sprite_l = sprite_l
        self.pos = [x, 0]
        self.hp = 5
        self.size = DEFAULT_SIZE
        self.head_tilt = 0
        self.torso_tilt = 0
        self.hit_h = 0
        self.hit_t = 0
        self.hit_l = 0
        self.flip = False
        self.flip_timer = FLIP_INTERVAL

    def move(self, p_x, p_y):
        outputs = [random.gauss(0, 0.3), random.gauss(0, 0.3), random.random() * 2 - 1, random.random() * 2 - 1]
        #outputs = self.controller(p_x, p_y, self.pos[0], self.pos[1])
        self.pos[0] += int(MAX_SPEED * outputs[0] * 2)
        self.pos[1] += int(MAX_SPEED * (2 * outputs[1] + 1))
        self.size = (MAX_SIZE - DEFAULT_SIZE) * self.pos[1] / utils.SCREEN_H + DEFAULT_SIZE
        if self.flip_timer == 0:
            self.flip = not self.flip
            self.flip_timer = FLIP_INTERVAL
        else:
            self.flip_timer -= 1

        if self.hit_h > 0:
            self.hit_h -= 1
        if self.hit_t > 0:
            self.hit_t -= 1
        if self.hit_l > 0:
            self.hit_l -= 1
        if self.head_tilt > 0:
            self.head_tilt -= 1
        elif self.head_tilt < 0:
            self.head_tilt += 1
        else:
            if outputs[2] > 0.5:
                self.head_tilt += SHIFT_DURATION + SHIFT_SUPPRESSION
            if outputs[2] < -0.5:
                self.head_tilt -= SHIFT_DURATION + SHIFT_SUPPRESSION
        if self.torso_tilt > 0:
            self.torso_tilt -= 1
        elif self.torso_tilt < 0:
            self.torso_tilt += 1
        else:
            if outputs[3] > 0.5:
                self.torso_tilt += SHIFT_DURATION + SHIFT_SUPPRESSION
            if outputs[3] < -0.5:
                self.torso_tilt -= SHIFT_DURATION + SHIFT_SUPPRESSION

    def kill(self):
        return

#class EnemyPoll:
    #def __init__(self, pops, ):