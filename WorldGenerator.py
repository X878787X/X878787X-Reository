import ctypes
import math
import pygame as pg
import sys


ctypes.windll.user32.SetProcessDPIAware() #Correct Pixel Count
pg.init()
pg.mixer.set_num_channels(69420)
FPS = 60
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 400
SURF = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pg.RESIZABLE)
SURF.fill((26, 26, 26))
pg.display.set_caption("World")
pg.display.flip()
clock = pg.time.Clock()

keys = pg.key.get_pressed()
mouse_buttons = pg.mouse.get_pressed()
mouse_pos = pg.mouse.get_pos()



def get_noise_at(x_cord, y_cord, seed, scale=0.007):
    # Scale and floor coordinates
    x_scaled, y_scaled = x_cord * scale, y_cord * scale
    x0, y0 = math.floor(x_scaled), math.floor(y_scaled)
    x1, y1 = x0 + 1, y0 + 1
    # Smoothstep interpolation weights
    u, v = x_scaled - x0, y_scaled - y0
    u = u * u * (3 - 2 * u)
    v = v * v * (3 - 2 * v)
    # Compute corner values
    corners = []
    for ix, iy in [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]:
        # Hash coordinate
        n = (ix * 1619 + iy * 31337 + seed * 1013) & 0x7fffffff
        n = (n ^ (n >> 13)) * 1274126177
        h = (n ^ (n >> 16)) / 0x7fffffff
        # Gradient
        gx, gy = math.cos(2 * math.pi * h), math.sin(2 * math.pi * h)
        # Dot product
        corners.append(gx * (x_scaled - ix) + gy * (y_scaled - iy))
    # Interpolate
    nx0 = corners[0] + u * (corners[1] - corners[0])
    nx1 = corners[2] + u * (corners[3] - corners[2])
    # Final interpolation and scaling
    return (nx0 + v * (nx1 - nx0) + 1) * 127.5









class World(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.seed = 1145141919810
        self.chunk_size = 16 # aka resolution
        self.chunk_x = 0 # actual chunk
        self.chunk_y = 0
        self.x_pos = 0
        self.y_pos = 0

        self.color = (255, 0, 0)

    def update(self):

        if keys[pg.K_DOWN]: #HAVE TO BE A WHOLE NUMBER
            self.y_pos += 1
        if keys[pg.K_UP]:
            self.y_pos -= 1
        if keys[pg.K_LEFT]:
            self.x_pos -= 1
        if keys[pg.K_RIGHT]:
            self.x_pos += 1


        for y in range(WINDOW_HEIGHT // self.chunk_size):
            y = y * self.chunk_size # resize y
            for x in range(WINDOW_WIDTH // self.chunk_size):
                x = x * self.chunk_size # resize x


                self.chunk_x = x
                self.chunk_y = y





                self.chunk_y += self.y_pos * self.chunk_size
                self.chunk_x += self.x_pos * self.chunk_size





                # color/biome setup
                noise_value = round(get_noise_at(round(self.chunk_x), round(self.chunk_y), self.seed), 2)
                if 180 <= noise_value: # snow_mountain
                    self.color = (255, 250, 250)
                elif 150 <= noise_value <= 190: # mountain
                    self.color = (136, 140, 150)
                elif 120 < noise_value < 160: # dark_grass
                    self.color = (19,133,16)
                elif 90 < noise_value <= 120: # light_grass
                    self.color = (65,152,10)
                elif noise_value <= 90: # lakes
                    self.color = (38, 102, 145)

                # display
                rect = pg.Rect(x, y, self.chunk_size, self.chunk_size)
                pg.draw.rect(SURF, self.color , rect)















def Main():
    global keys, mouse_buttons, mouse_pos, WINDOW_WIDTH, WINDOW_HEIGHT

    while True:
        # SURF.fill((26, 26, 26))
        for event in pg.event.get():
            keys = pg.key.get_pressed()
            mouse_buttons = pg.mouse.get_pressed()
            mouse_pos = pg.mouse.get_pos()
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.VIDEORESIZE:
                # Handle resize event
                WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pg.RESIZABLE)


        world.update()
        pg.display.update()
        clock.tick(FPS)




if __name__ == "__main__":
    world = World()
    Main()



# better camera, though 1 chunk at a time
