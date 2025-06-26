import math
import random

import cv2
import mediapipe as mp
import sdl2.ext
import sdl2.sdlimage
import time

import utils
import Enemy

MAX_ENEMIES = 30
MAX_HP = 3

hand_finder = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
#pose_finder = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
sdl2.ext.init()
mode = sdl2.SDL_DisplayMode()
sdl2.SDL_GetCurrentDisplayMode(0, mode)
utils.SCREEN_W = mode.w
utils.SCREEN_H = mode.h
utils.DEFAULT_SIZE = 0.3 * utils.SCREEN_H
utils.MAX_SIZE = 0.6 * utils.SCREEN_H
window = sdl2.ext.Window("HELLO!", size=(utils.SCREEN_W, utils.SCREEN_H), flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
renderer = sdl2.ext.Renderer(window)
factory = sdl2.ext.SpriteFactory(renderer=renderer)
spriterenderer = factory.create_sprite_render_system(window)
sprite_head = factory.from_image("pictures/Guy_head.png")
sdl2.SDL_SetTextureBlendMode(sprite_head.texture, sdl2.SDL_BLENDMODE_BLEND)
sprite_torso = factory.from_image("pictures/Guy_torso.png")
sdl2.SDL_SetTextureBlendMode(sprite_torso.texture, sdl2.SDL_BLENDMODE_BLEND)
sprite_legs = factory.from_image("pictures/Guy_legs.png")
sdl2.SDL_SetTextureBlendMode(sprite_legs.texture, sdl2.SDL_BLENDMODE_BLEND)
sprite_laser = factory.from_image("pictures/Guy_head_laser.png")
sdl2.SDL_SetTextureBlendMode(sprite_laser.texture, sdl2.SDL_BLENDMODE_BLEND)
sprite_trophy = factory.from_image("pictures/Trophy.png")
sdl2.SDL_SetTextureBlendMode(sprite_trophy.texture, sdl2.SDL_BLENDMODE_BLEND)
window.show()
red = sdl2.ext.Color(255, 0, 0)
green = sdl2.ext.Color(0, 255, 0)
blue = sdl2.ext.Color(0, 0, 255)
black = sdl2.ext.Color(0, 0, 0)
webcam = cv2.VideoCapture(0)

#initialize
running = True
# base_coords = {}
# trigger_tick = 0.1
# INIT_DELAY = 3
# INIT_SHOOT = 2
# for coord in [(0, 0), (utils.SCREEN_W, 0), (0, utils.SCREEN_H)]:
#     prev_tick = time.time_ns() / 1e6
#     if not running:
#         break
#     for i in range(utils.FRAMERATE * INIT_DELAY):
#         renderer.color = black
#         renderer.clear()
#         utils.draw_rect(renderer, coord, 20, 20, red)
#         utils.draw_circle(renderer, coord, utils.FRAMERATE * INIT_DELAY + 30 - i, red, 10)
#         current_tick = time.time_ns() / 1e6
#         if (current_tick - prev_tick) * utils.FRAMERATE < 1:
#             time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
#         prev_tick = time.time_ns() / 1e6
#         renderer.present()
#     hands = None
#     shoulder = None
#     renderer.color = black
#     renderer.clear()
#     utils.draw_rect(renderer, coord, 20, 20, green)
#     utils.draw_circle(renderer, coord, 30, green, 10)
#     renderer.present()
#     stop_time = time.time_ns() + 1e9
#     while running and (time.time_ns() < stop_time or hands is None):
#         success, image = webcam.read()
#         image = cv2.flip(image, 1)
#         image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#         hand_result = hand_finder.process(image_rgb)
#         #shoulder_result = pose_finder.process(image_rgb)
#         renderer.color = black
#         renderer.clear()
#         events = sdl2.ext.get_events()
#         for event in events:
#             if event.type == sdl2.SDL_QUIT:
#                 running = False
#                 break
#             if event.type == sdl2.SDL_KEYUP:
#                 if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
#                     running = False
#                     break
#                 if event.key.keysym.sym == sdl2.SDLK_w:
#                     enemies = []
#                     tot_enemies = MAX_ENEMIES
#                     break
#                 if event.key.keysym.sym == sdl2.SDLK_l:
#                     curr_hp = 0
#                     break
#         utils.draw_rect(renderer, coord, 20, 20, green)
#         utils.draw_circle(renderer, coord, 30, green, 10)
#         if hand_result.multi_hand_landmarks:
#             hands = hand_result.multi_hand_landmarks[0].landmark
#         #if shoulder_result.pose_landmarks:
#         #    shoulder = shoulder_result.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
#         current_tick = time.time_ns() / 1e6
#         if (current_tick - prev_tick) * utils.FRAMERATE < 1:
#             time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
#         prev_tick = time.time_ns() / 1e6
#         renderer.present()
#
#     thumb_tip = hands[4]
#     index_knuckle = hands[6]
#     trigger_tick += utils.trigger_value(index_knuckle, thumb_tip) / 3.0
#    base_coords[coord] = (hands[8].x - shoulder.x, hands[8].y - shoulder.y)
#x_m = base_coords[(utils.SCREEN_W, 0)][0] - base_coords[(0, 0)][0]
#x_q = base_coords[(0, 0)][0]
#y_m = base_coords[(0, utils.SCREEN_H)][1] - base_coords[(0, 0)][0]
#y_q = base_coords[(0, 0)][0]

p_x = 0
p_y = 0
enemies = []
head_x = 50.0 / 400.0
head_y = 65.0 / 400.0
torso_x = 140.0 / 400.0
torso_y = 142.0 / 400.0
legs_x = 160.0 / 400.0
legs_y = 193.0 / 400.0

prev_shoot = False
shoot = False
prev_tick = time.time_ns() / 1e6
laser = 0
curr_hp = MAX_HP
tot_enemies = 0
while running and curr_hp > 0 and (tot_enemies < MAX_ENEMIES or len(enemies) > 0):
    renderer.color = black
    renderer.clear()
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
        if event.type == sdl2.SDL_KEYUP:
            if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                running = False
                break
            if event.key.keysym.sym == sdl2.SDLK_w:
                enemies = []
                tot_enemies = MAX_ENEMIES
                break
            if event.key.keysym.sym == sdl2.SDLK_l:
                curr_hp = 0
                break

    if laser > 0:
        sdl2.SDL_SetTextureAlphaMod(sprite_laser.texture, 255 - int(255 * abs(laser - 30) / 30))
        sdl2.SDL_RenderCopy(renderer.renderer, sprite_laser.texture, None,
                            sdl2.SDL_Rect(
                                max(0, int((utils.SCREEN_W - utils.SCREEN_H) / 2)), max(0, int((utils.SCREEN_H - utils.SCREEN_W) / 2)),
                                min(utils.SCREEN_W, utils.SCREEN_H), min(utils.SCREEN_W, utils.SCREEN_H)
                            )
                            )
        laser -= 1
        current_tick = time.time_ns() / 1e6
        if (current_tick - prev_tick) * utils.FRAMERATE < 1:
            time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
        prev_tick = time.time_ns() / 1e6
        renderer.present()
        continue
    for i in range(curr_hp):
        utils.draw_rect(renderer, (60 + 50 * i, 60), 40, 40, green)

    while (len(enemies) < 1 or random.randint(1,  int(utils.FRAMERATE * (1.5 - tot_enemies / MAX_ENEMIES))) == 1) and len(enemies) < 4 and tot_enemies < MAX_ENEMIES:
        tot_enemies += 1
        enemies.append(Enemy.Enemy(None, sprite_head, sprite_torso, sprite_legs,
                                   int(random.random() * (utils.SCREEN_W - Enemy.DEFAULT_SIZE) + Enemy.DEFAULT_SIZE / 2)
                       )
                       )
    success, image = webcam.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hand_result = hand_finder.process(image_rgb)
    #pose_result = pose_finder.process(image_rgb)
    if hand_result.multi_hand_landmarks:# and pose_result.pose_landmarks:
        if (len(hand_result.multi_hand_landmarks) > 1):
            hand_landmarks = max(hand_result.multi_hand_landmarks, key=lambda h: hand_landmarks[4].y - hand_landmarks[3].y).landmark
        else:
            hand_landmarks = hand_result.multi_hand_landmarks[0].landmark
        thumb = (int(hand_landmarks[4].x * utils.SCREEN_W), int(hand_landmarks[4].y * utils.SCREEN_H))
        index_tip = (int(hand_landmarks[8].x * utils.SCREEN_W), int(hand_landmarks[8].y * utils.SCREEN_H))
        index_base = (int(hand_landmarks[6].x * utils.SCREEN_W), int(hand_landmarks[6].y * utils.SCREEN_H))
        #right_shoulder = pose_result.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
        #shoulder_pos = (int(right_shoulder.x * utils.SCREEN_W), int(right_shoulder.y * utils.SCREEN_H))
        #shoot = utils.trigger_value(hand_landmarks[6], hand_landmarks[4]) <= trigger_tick
        shoot = hand_landmarks[3].y < hand_landmarks[4].y + 0.01
        if not shoot:
            #p_x = int((hand_landmarks[8].x - right_shoulder.x - x_q) / x_m * utils.SCREEN_W)
            #p_y = int((hand_landmarks[8].y - right_shoulder.y - y_q) / y_m * utils.SCREEN_H)
            p_x = int(hand_landmarks[8].x * utils.SCREEN_W)
            p_y = int(hand_landmarks[8].y * utils.SCREEN_H)
    else:
        shoot = False
    if shoot and not prev_shoot:
        for enemy in enemies:
            if abs(enemy.pos[1] - p_y) <= enemy.size / 2:
                d_x = p_x - enemy.pos[0]
                d_y = p_y - enemy.pos[1]
                if d_y >= (head_y + torso_y - 0.5) * enemy.size:
                    if abs(d_x) <= legs_x * enemy.size / 2:
                        if enemy.hp == 1:
                            enemies.remove(enemy)
                        else:
                            enemy.hp -= 1
                            enemy.hit_l = 60
                        break
                elif d_y >= (head_y - 0.5) * enemy.size:
                    if ((abs(enemy.torso_tilt) <= Enemy.SHIFT_SUPPRESSION and abs(d_x) <= torso_x * enemy.size / 2) or
                            (enemy.torso_tilt > Enemy.SHIFT_SUPPRESSION and abs(d_x - enemy.size / 5) <= torso_x * enemy.size / 2) or
                            (enemy.torso_tilt < -Enemy.SHIFT_SUPPRESSION and abs(d_x + enemy.size / 5) <= torso_x * enemy.size / 2)
                    ):
                        if enemy.hp <= 2:
                            enemies.remove(enemy)
                        else:
                            enemy.hp -= 2
                            enemy.hit_t = 60
                        break
                if ((abs(enemy.head_tilt) <= Enemy.SHIFT_SUPPRESSION and abs(d_x) <= head_x * enemy.size / 2) or
                        (enemy.head_tilt > Enemy.SHIFT_SUPPRESSION and abs(d_x - enemy.size / 5) <= head_x * enemy.size / 2) or
                        (enemy.head_tilt < -Enemy.SHIFT_SUPPRESSION and abs(d_x + enemy.size / 5) <= head_x * enemy.size / 2)
                ):
                    if enemy.hp <= 5:
                        enemies.remove(enemy)
                    else:
                        enemy.hp -= 5
                        enemy.hit_h = 60
                    break

    counter = 0
    hit = -1
    for enemy in enemies:
        enemy.move(p_x, p_y)
        if enemy.pos[1] + enemy.size / 2 > utils.SCREEN_H:
            laser = 60
            curr_hp -= 1
            hit = counter
        head_shift = 0
        if enemy.head_tilt > Enemy.SHIFT_SUPPRESSION:
            head_shift = 1
        elif enemy.head_tilt < -Enemy.SHIFT_SUPPRESSION:
            head_shift = -1
        torso_shift = 0
        if enemy.torso_tilt > Enemy.SHIFT_SUPPRESSION:
            torso_shift = 1
        elif enemy.torso_tilt < -Enemy.SHIFT_SUPPRESSION:
            torso_shift = -1
        sdl2.SDL_SetTextureColorMod(enemy.sprite_h.texture, 255, int(255 * (1 - enemy.hit_h / 60.0)), int(255 * (1 - enemy.hit_h / 60.0)))
        sdl2.SDL_RenderCopyEx(renderer.renderer, enemy.sprite_h.texture, None,
                            sdl2.SDL_Rect(
                                int(head_shift * enemy.size / 5 + enemy.pos[0] - head_x * enemy.size / 2), int(enemy.pos[1] - enemy.size / 2),
                                int(head_x * enemy.size), int(head_y * enemy.size)
                            ), 0.0, None, sdl2.SDL_FLIP_HORIZONTAL if enemy.flip else sdl2.SDL_FLIP_NONE
                            )
        sdl2.SDL_SetTextureColorMod(enemy.sprite_t.texture, 255, int(255 * (1 - enemy.hit_t / 60.0)), int(255 * (1 - enemy.hit_t / 60.0)))
        sdl2.SDL_RenderCopyEx(renderer.renderer, enemy.sprite_t.texture, None,
                            sdl2.SDL_Rect(
                                int(torso_shift * enemy.size / 5 + enemy.pos[0] - torso_x * enemy.size / 2), int(enemy.pos[1] - (1 - 2 * head_y) * enemy.size / 2),
                                int(torso_x * enemy.size), int(torso_y * enemy.size)
                            ), 0.0, None, sdl2.SDL_FLIP_HORIZONTAL if enemy.flip else sdl2.SDL_FLIP_NONE
                            )
        sdl2.SDL_SetTextureColorMod(enemy.sprite_l.texture, 255, int(255 * (1 - enemy.hit_l / 60.0)), int(255 * (1 - enemy.hit_l / 60.0)))
        sdl2.SDL_RenderCopyEx(renderer.renderer, enemy.sprite_l.texture, None,
                            sdl2.SDL_Rect(
                                int(enemy.pos[0] - legs_x * enemy.size / 2), int(enemy.pos[1] - (1 - 2 * head_y - 2 * torso_y) * enemy.size / 2),
                                int(legs_x * enemy.size), int(legs_y * enemy.size)
                            ), 0.0, None, sdl2.SDL_FLIP_HORIZONTAL if enemy.flip else sdl2.SDL_FLIP_NONE
                            )
        counter += 1
    if hit >= 0:
        enemies.pop(hit).kill()
    prev_shoot = shoot
    utils.draw_scope(renderer, (p_x, p_y), 20, red if shoot else green, 1)
    current_tick = time.time_ns() / 1e6
    if (current_tick - prev_tick) * utils.FRAMERATE < 1000:
        time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
    prev_tick = time.time_ns() / 1e6
    renderer.present()

if running:
    ticks = 0
    if curr_hp <= 0:
        new_sprite = sprite_laser
        while ticks < 60 and running:
            ticks += 1
            renderer.color = black
            renderer.clear()
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT or (event.type == sdl2.SDL_KEYUP and event.key.keysym.sym == sdl2.SDLK_ESCAPE):
                    running = False
                    break
            sdl2.SDL_SetTextureAlphaMod(new_sprite.texture, 255 - int(255 * abs(ticks - 30) / 30))
            sdl2.SDL_RenderCopy(renderer.renderer, new_sprite.texture, None,
                                sdl2.SDL_Rect(
                                    max(0, int((utils.SCREEN_W - utils.SCREEN_H) / 2)), max(0, int((utils.SCREEN_H - utils.SCREEN_W) / 2)),
                                    min(utils.SCREEN_W, utils.SCREEN_H), min(utils.SCREEN_W, utils.SCREEN_H)
                                )
                                )
            current_tick = time.time_ns() / 1e6
            if (current_tick - prev_tick) * utils.FRAMERATE < 1:
                time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
            prev_tick = time.time_ns() / 1e6
            renderer.present()
        ticks = 0
        sdl2.SDL_SetTextureColorMod(sprite_laser.texture, 255, 63, 63)
    else:
        new_sprite = sprite_trophy
    while ticks < 240 and running:
        ticks += 1
        renderer.color = black
        renderer.clear()
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT or (event.type == sdl2.SDL_KEYUP and event.key.keysym.sym == sdl2.SDLK_ESCAPE):
                running = False
                break
        sdl2.SDL_SetTextureAlphaMod(new_sprite.texture, 255 - int(255 * abs(ticks - 120) / 120))
        sdl2.SDL_RenderCopy(renderer.renderer, new_sprite.texture, None,
                            sdl2.SDL_Rect(
                                max(0, int((utils.SCREEN_W - utils.SCREEN_H) / 2)), max(0, int((utils.SCREEN_H - utils.SCREEN_W) / 2)),
                                min(utils.SCREEN_W, utils.SCREEN_H), min(utils.SCREEN_W, utils.SCREEN_H)
                            )
                            )
        current_tick = time.time_ns() / 1e6
        if (current_tick - prev_tick) * utils.FRAMERATE < 1:
            time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
        prev_tick = time.time_ns() / 1e6
        renderer.present()
webcam.release()
sdl2.ext.quit()
