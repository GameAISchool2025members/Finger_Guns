import random
import time
import ctypes

import cv2
import mediapipe as mp
import sdl2.ext
import sdl2.sdlttf
import sdl2.sdlmixer

import utils
import Enemy

MAX_ENEMIES = 30
MAX_HP = 5

hand_finder = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
sdl2.ext.init(sdl2.SDL_INIT_AUDIO | sdl2.SDL_INIT_VIDEO)
sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.sdlmixer.MIX_DEFAULT_FORMAT, 1, 1024)
sdl2.sdlttf.TTF_Init()
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
sprite_heart = factory.from_image("pictures/Heart.png")
sdl2.SDL_SetTextureBlendMode(sprite_heart.texture, sdl2.SDL_BLENDMODE_BLEND)

font = sdl2.sdlttf.TTF_OpenFont(b"./fonts/Roboto-Regular.ttf", 50)
shoot_sound = sdl2.sdlmixer.Mix_LoadWAV(b"./sounds/Shoot_sound.wav")
victory_sound = sdl2.sdlmixer.Mix_LoadWAV(b"./sounds/Applause.wav")
defeat_sound = sdl2.sdlmixer.Mix_LoadWAV(b"./sounds/Annoying.mp3")
sdl2.sdlmixer.Mix_VolumeChunk(defeat_sound, 16)

file = open("high_scores.txt")
high_scores = sorted([(int(line[1]), int(line[2]), line[0]) for line in map(lambda ln: ln.split(";"), file)], reverse=True)
file.close()

window.show()
red = sdl2.ext.Color(255, 0, 0)
green = sdl2.ext.Color(0, 255, 0)
blue = sdl2.ext.Color(0, 0, 255)
black = sdl2.ext.Color(0, 0, 0)
white_sdl = sdl2.SDL_Color(255, 255, 255)

p_x = 0
p_y = 0
enemies = []
head_x = 660.0 / 4630.0
head_y = 690.0 / 4630.0
torso_x = 1528.0 / 4630.0
torso_y = 1526.0 / 4630.0
legs_x = 1400.0 / 4630.0
legs_y = 2412.0 / 4630.0

webcam = cv2.VideoCapture(0)
shoot = False
laser = 0
curr_hp = MAX_HP
tot_enemies = 0
enemies_killed = 0
running = True
prev_shoot = False
prev_tick = time.time_ns() / 1e6
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
                enemies_killed = MAX_ENEMIES
                break
            if event.key.keysym.sym == sdl2.SDLK_l:
                curr_hp = 0
                break

    if laser > 0:
        sdl2.SDL_SetTextureAlphaMod(sprite_laser.texture, 255 - int(255 * abs(laser - 30) / 30))
        sdl2.SDL_RenderCopy(renderer.sdlrenderer, sprite_laser.texture, None,
                            sdl2.SDL_Rect(
                                max(0, int((utils.SCREEN_W - utils.SCREEN_H) / 2)), max(0, int((utils.SCREEN_H - utils.SCREEN_W) / 2)),
                                min(utils.SCREEN_W, utils.SCREEN_H), min(utils.SCREEN_W, utils.SCREEN_H)
                            )
                            )
        laser -= 1
        current_tick = time.time_ns() / 1e6
        if (current_tick - prev_tick) * utils.FRAMERATE < 1000:
            time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
        prev_tick = time.time_ns() / 1e6
        renderer.present()
        continue

    for i in range(curr_hp):
        sdl2.SDL_RenderCopy(renderer.sdlrenderer, sprite_heart.texture, None, sdl2.SDL_Rect(10 + 100 * i, 10, 100, 100))

    text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"ENEMIES KILLED: {enemies_killed}".encode("utf-8"), white_sdl)
    texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
    text_rect = sdl2.SDL_Rect(1450, 10, text_surface.contents.w, 50)
    sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
    sdl2.SDL_DestroyTexture(texture)
    sdl2.SDL_FreeSurface(text_surface)

    while (len(enemies) < 1 or random.randint(1,  int(utils.FRAMERATE * (1.5 - tot_enemies / MAX_ENEMIES))) == 1) and len(enemies) < 4 and tot_enemies < MAX_ENEMIES:
        tot_enemies += 1
        enemies.append(Enemy.Enemy(Enemy.random_controller, sprite_head, sprite_torso, sprite_legs,
                                   int(random.random() * (utils.SCREEN_W - Enemy.DEFAULT_SIZE) + Enemy.DEFAULT_SIZE / 2)
                       )
                       )
    success, image = webcam.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hand_result = hand_finder.process(image_rgb)
    if hand_result.multi_hand_landmarks:
        if (len(hand_result.multi_hand_landmarks) > 1):
            hand_landmarks = max(hand_result.multi_hand_landmarks, key=lambda h: hand_landmarks[4].y - hand_landmarks[3].y).landmark
        else:
            hand_landmarks = hand_result.multi_hand_landmarks[0].landmark
        thumb = (int(hand_landmarks[4].x * utils.SCREEN_W), int(hand_landmarks[4].y * utils.SCREEN_H))
        index_tip = (int(hand_landmarks[8].x * utils.SCREEN_W), int(hand_landmarks[8].y * utils.SCREEN_H))
        index_base = (int(hand_landmarks[6].x * utils.SCREEN_W), int(hand_landmarks[6].y * utils.SCREEN_H))
        shoot = hand_landmarks[3].y < hand_landmarks[4].y + 0.01
        if not shoot:
            p_x = int(hand_landmarks[8].x * utils.SCREEN_W)
            p_y = int(hand_landmarks[8].y * utils.SCREEN_H)
    else:
        shoot = False
    if shoot and not prev_shoot:
        sdl2.sdlmixer.Mix_PlayChannel(-1, shoot_sound, 0)
        for enemy in enemies:
            if abs(enemy.pos[1] - p_y) <= enemy.size / 2:
                d_x = p_x - enemy.pos[0]
                d_y = p_y - enemy.pos[1]
                if d_y >= (head_y + torso_y - 0.5) * enemy.size:
                    if abs(d_x) <= legs_x * enemy.size / 2:
                        if enemy.hp == 1:
                            enemies.remove(enemy)
                            enemies_killed += 1
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
                            enemies_killed += 1
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
                        enemies_killed += 1
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
        sdl2.SDL_RenderCopyEx(renderer.sdlrenderer, enemy.sprite_h.texture, None,
                            sdl2.SDL_Rect(
                                int(head_shift * enemy.size / 5 + enemy.pos[0] - head_x * enemy.size / 2), int(enemy.pos[1] - enemy.size / 2),
                                int(head_x * enemy.size), int(head_y * enemy.size)
                            ), 0.0, None, sdl2.SDL_FLIP_HORIZONTAL if enemy.flip else sdl2.SDL_FLIP_NONE
                            )
        sdl2.SDL_SetTextureColorMod(enemy.sprite_t.texture, 255, int(255 * (1 - enemy.hit_t / 60.0)), int(255 * (1 - enemy.hit_t / 60.0)))
        sdl2.SDL_RenderCopyEx(renderer.sdlrenderer, enemy.sprite_t.texture, None,
                            sdl2.SDL_Rect(
                                int(torso_shift * enemy.size / 5 + enemy.pos[0] - torso_x * enemy.size / 2), int(enemy.pos[1] - (1 - 2 * head_y) * enemy.size / 2),
                                int(torso_x * enemy.size), int(torso_y * enemy.size)
                            ), 0.0, None, sdl2.SDL_FLIP_HORIZONTAL if enemy.flip else sdl2.SDL_FLIP_NONE
                            )
        sdl2.SDL_SetTextureColorMod(enemy.sprite_l.texture, 255, int(255 * (1 - enemy.hit_l / 60.0)), int(255 * (1 - enemy.hit_l / 60.0)))
        sdl2.SDL_RenderCopyEx(renderer.sdlrenderer, enemy.sprite_l.texture, None,
                            sdl2.SDL_Rect(
                                int(enemy.pos[0] - legs_x * enemy.size / 2), int(enemy.pos[1] - (1 - 2 * head_y - 2 * torso_y) * enemy.size / 2),
                                int(legs_x * enemy.size), int(legs_y * enemy.size)
                            ), 0.0, None, sdl2.SDL_FLIP_HORIZONTAL if enemy.flip else sdl2.SDL_FLIP_NONE
                            )
        counter += 1
    if hit >= 0:
        enemies.pop(hit).kill()
    prev_shoot = shoot
    utils.draw_scope(renderer, (p_x, p_y), 20, red if shoot else green, 5)
    current_tick = time.time_ns() / 1e6
    if (current_tick - prev_tick) * utils.FRAMERATE < 1000:
        time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
    prev_tick = time.time_ns() / 1e6
    renderer.present()

webcam.release()

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
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, new_sprite.texture, None,
                                sdl2.SDL_Rect(
                                    max(0, int((utils.SCREEN_W - utils.SCREEN_H) / 2)), max(0, int((utils.SCREEN_H - utils.SCREEN_W) / 2)),
                                    min(utils.SCREEN_W, utils.SCREEN_H), min(utils.SCREEN_W, utils.SCREEN_H)
                                )
                                )
            current_tick = time.time_ns() / 1e6
            if (current_tick - prev_tick) * utils.FRAMERATE < 1000:
                time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
            prev_tick = time.time_ns() / 1e6
            renderer.present()
        ticks = 0
        sdl2.SDL_SetTextureColorMod(sprite_laser.texture, 255, 63, 63)
        sdl2.sdlmixer.Mix_PlayChannel(-1, defeat_sound, 0)
    else:
        new_sprite = sprite_trophy
        sdl2.sdlmixer.Mix_PlayChannel(-1, victory_sound, 0)
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
        sdl2.SDL_RenderCopy(renderer.sdlrenderer, new_sprite.texture, None,
                            sdl2.SDL_Rect(
                                max(0, int((utils.SCREEN_W - utils.SCREEN_H) / 2)), max(0, int((utils.SCREEN_H - utils.SCREEN_W) / 2)),
                                min(utils.SCREEN_W, utils.SCREEN_H), min(utils.SCREEN_W, utils.SCREEN_H)
                            )
                            )
        current_tick = time.time_ns() / 1e6
        if (current_tick - prev_tick) * utils.FRAMERATE < 1000:
            time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
        prev_tick = time.time_ns() / 1e6
        renderer.present()

get_score = running
if running:
    tick = 0
    while running:
        tick += 1
        renderer.color = black
        renderer.clear()
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT or (event.type == sdl2.SDL_KEYUP and event.key.keysym.sym == sdl2.SDLK_ESCAPE):
                running = False
                break
        index = 0
        text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, b"HIGH SCORES", white_sdl)
        texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
        text_rect = sdl2.SDL_Rect(50, 50, utils.SCREEN_W - 50, 200)
        sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
        sdl2.SDL_DestroyTexture(texture)
        sdl2.SDL_FreeSurface(text_surface)
        while index < len(high_scores) and index < 8 and (high_scores[index][0] > enemies_killed or (high_scores[index][0] == enemies_killed and high_scores[index][1] > curr_hp)):
            score = high_scores[index]
            text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"{score[2]}: ".encode("utf-8"), white_sdl)
            texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
            text_rect = sdl2.SDL_Rect(600, 300 + 100 * index, min(text_surface.contents.w, 200), 50)
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
            sdl2.SDL_DestroyTexture(texture)
            sdl2.SDL_FreeSurface(text_surface)
            text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"{score[0]} enemies killed".encode("utf-8"), white_sdl)
            texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
            text_rect = sdl2.SDL_Rect(900, 300 + 100 * index, min(text_surface.contents.w, 200), 50)
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
            sdl2.SDL_DestroyTexture(texture)
            sdl2.SDL_FreeSurface(text_surface)
            if score[0] == MAX_ENEMIES:
                text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"{score[1]} hp".encode("utf-8"), white_sdl)
                texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
                text_rect = sdl2.SDL_Rect(1200, 300 + 100 * index, text_surface.contents.w, 50)
                sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
                sdl2.SDL_DestroyTexture(texture)
                sdl2.SDL_FreeSurface(text_surface)
            index += 1
        if index < 8 and (tick % 60) < 30:
            text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, b"YOU: ", white_sdl)
            texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
            text_rect = sdl2.SDL_Rect(600, 300 + 100 * index, min(text_surface.contents.w, 200), 50)
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
            sdl2.SDL_DestroyTexture(texture)
            sdl2.SDL_FreeSurface(text_surface)
            text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"{enemies_killed} enemies killed".encode("utf-8"), white_sdl)
            texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
            text_rect = sdl2.SDL_Rect(900, 300 + 100 * index, min(text_surface.contents.w, 200), 50)
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
            sdl2.SDL_DestroyTexture(texture)
            sdl2.SDL_FreeSurface(text_surface)
            if enemies_killed == MAX_ENEMIES:
                text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"{curr_hp} hp".encode("utf-8"), white_sdl)
                texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
                text_rect = sdl2.SDL_Rect(1200, 300 + 100 * index, text_surface.contents.w, 50)
                sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
                sdl2.SDL_DestroyTexture(texture)
                sdl2.SDL_FreeSurface(text_surface)
        while index < len(high_scores) and index < 8:
            score = high_scores[index]
            text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"{score[2]}: ".encode("utf-8"), white_sdl)
            texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
            text_rect = sdl2.SDL_Rect(600, 400 + 100 * index, min(text_surface.contents.w, 200), 50)
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
            sdl2.SDL_DestroyTexture(texture)
            sdl2.SDL_FreeSurface(text_surface)
            text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"{score[0]} enemies killed".encode("utf-8"), white_sdl)
            texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
            text_rect = sdl2.SDL_Rect(900, 400 + 100 * index, min(text_surface.contents.w, 200), 50)
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
            sdl2.SDL_DestroyTexture(texture)
            sdl2.SDL_FreeSurface(text_surface)
            if score[0] == MAX_ENEMIES:
                text_surface = sdl2.sdlttf.TTF_RenderText_Solid(font, f"{score[1]} hp".encode("utf-8"), white_sdl)
                texture = sdl2.SDL_CreateTextureFromSurface(renderer.sdlrenderer, text_surface)
                text_rect = sdl2.SDL_Rect(1200, 400 + 100 * index, text_surface.contents.w, 50)
                sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, text_rect)
                sdl2.SDL_DestroyTexture(texture)
                sdl2.SDL_FreeSurface(text_surface)
            index += 1
        current_tick = time.time_ns() / 1e6
        if (current_tick - prev_tick) * utils.FRAMERATE < 1000:
            time.sleep((1000 / utils.FRAMERATE - current_tick + prev_tick) / 1000)
        prev_tick = time.time_ns() / 1e6
        renderer.present()

sdl2.sdlttf.TTF_CloseFont(font)
sdl2.sdlttf.TTF_Quit()
sdl2.sdlmixer.Mix_FreeChunk(shoot_sound)
sdl2.sdlmixer.Mix_FreeChunk(victory_sound)
sdl2.sdlmixer.Mix_FreeChunk(defeat_sound)
sdl2.sdlmixer.Mix_CloseAudio()
sdl2.ext.quit()
if get_score:
    print("Your name? ")
    name = input()
    if name != "":
        file = open("high_scores.txt", 'a')
        file.write(f"{name};{enemies_killed};{curr_hp}\n")
        file.close()
