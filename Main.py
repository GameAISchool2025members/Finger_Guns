import sys
import ctypes
import sdl2
import sdl2.sdlttf as sdlttf

sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
sdlttf.TTF_Init()

font = sdlttf.TTF_OpenFont(b"./fonts/Roboto-Regular.ttf", 20)

if not font:
    print("Errore:", sdlttf.TTF_GetError().decode())
    sdlttf.TTF_Quit()
    sdl2.SDL_Quit()
    sys.exit(1)

print("Font caricato:", font)

if isinstance(font, ctypes.POINTER(sdlttf.TTF_Font)):
    print("HA!")
    sdlttf.TTF_CloseFont(font)
    font = None

sdlttf.TTF_Quit()
sdl2.SDL_Quit()
