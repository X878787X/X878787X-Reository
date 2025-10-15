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


all_season_tick = 1
world_data = {} # store all the info/data
"""Perlin_Noise"""
_perm_cache = {}
def terrain_generation(x, y, seed, scale=5000):
    # === Cached permutation table for the given seed ===
    if seed not in _perm_cache:
        p = list(range(256))
        for i in range(255, 0, -1):
            j = (seed + i * 31) % 256
            p[i], p[j] = p[j], p[i]
        _perm_cache[seed] = p + p
    p = _perm_cache[seed]

    def fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(a, b, t):
        return a + t * (b - a)

    def grad(hashi, xi, yi):
        h = hashi & 7
        u = xi if h < 4 else yi
        v = yi if h < 4 else xi
        return ((u if (h & 1) == 0 else -u) +
                (v if (h & 2) == 0 else -v))

    # Proper floor to handle negative x/y correctly
    def floor_int(v):
        return math.floor(v) if v >= 0 or v == int(v) else int(v) - 1

    # === Perlin Noise Core ===
    def perlin(xu, yu):
        xi = floor_int(xu) & 255
        yi = floor_int(yu) & 255
        xf = xu - floor_int(xu)
        yf = yu - floor_int(yu)

        u = fade(xf)
        v = fade(yf)

        aa = p[p[xi] + yi]
        ab = p[p[xi] + yi + 1]
        ba = p[p[xi + 1] + yi]
        bb = p[p[xi + 1] + yi + 1]

        x1 = lerp(grad(aa, xf, yf), grad(ba, xf - 1, yf), u)
        x2 = lerp(grad(ab, xf, yf - 1), grad(bb, xf - 1, yf - 1), u)
        return (lerp(x1, x2, v) + 1) * 0.5  # 0–1

    # === Fractal (multi-octave) noise ===
    def fractal_noise(xi, yi):
        total = 0
        amp = 1.0
        freq = 1.0
        max_amp = 0
        for _ in range(3):
            total += perlin(xi * freq, yi * freq) * amp
            max_amp += amp
            amp *= 0.5
            freq *= 2.0
        return total / max_amp

    # === Apply scale ===
    nx, ny = x / scale, y / scale
    base = fractal_noise(nx, ny)

    # === Lightweight erosion/smoothing ===
    d = 0.002
    smooth = (
        fractal_noise(nx + d, ny) +
        fractal_noise(nx - d, ny) +
        fractal_noise(nx, ny + d) +
        fractal_noise(nx, ny - d)
    ) * 0.25

    correction = 1.5 # to make the data fit more
    height = (base * 0.7 + smooth * 0.3) ** 1.5 * 255 * correction
    return height

def etc_generation(x_cord, y_cord, seed, scale=0.007):
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
"""Pearling_Noise"""




class World(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.seed = 1145141919810
        self.seed_etc = round((terrain_generation(self.seed/2, self.seed*2, self.seed, scale = 100) * terrain_generation(self.seed*2, self.seed/2, self.seed, scale = 200) / 255) ** 3.14)
        self.chunk_size = 16 # aka resolution
        self.chunk_x = 0 # actual chunk
        self.chunk_y = 0
        self.x_pos = 0
        self.y_pos = 0
        self.speed = 2

        self.color = {
            "high_snow": (255, 250, 250),
            "snow_mountain": (245, 240, 240),
            "mountain": (136, 140, 150),
            "dark_grass": (19, 133, 16),
            "light_grass": (65, 152, 10),
            "lakes": (38, 102, 145),
            "gold": (255, 223, 10),
            "forest": (20, 91, 40),
            "brick": (188, 74, 60),


        }



    def update(self):
        self.move()
        self.draw()


    def move(self):
        if keys[pg.K_DOWN]:
            self.y_pos += self.speed
        if keys[pg.K_UP]:
            self.y_pos -= self.speed
        if keys[pg.K_LEFT]:
            self.x_pos -= self.speed
        if keys[pg.K_RIGHT]:
            self.x_pos += self.speed

        if keys[pg.K_s]:
            self.y_pos += self.speed
        if keys[pg.K_w]:
            self.y_pos -= self.speed
        if keys[pg.K_a]:
            self.x_pos -= self.speed
        if keys[pg.K_d]:
            self.x_pos += self.speed

    def draw(self): # display and generation if needed
        for y in range(WINDOW_HEIGHT // self.chunk_size): # Screen location
            for x in range(WINDOW_WIDTH // self.chunk_size):

                ry = y + self.y_pos # Real location & chunk number
                rx = x + self.x_pos

                chunk_y = ry * self.chunk_size # Real Location, but resized
                chunk_x = rx * self.chunk_size

                if (rx, ry) in world_data:
                    color = world_data.get((rx, ry))
                else:
                    color = (0, 255, 0)
                    self.generate(rx, ry, chunk_x, chunk_y)

                rect = pg.Rect(x * self.chunk_size, y * self.chunk_size, self.chunk_size, self.chunk_size)
                self.interaction(rect, rx, ry, chunk_x, chunk_y)
                pg.draw.rect(SURF, color, rect)


    def generate(self, rx, ry, chunk_x, chunk_y, do_etc = True): # usage of perlin_noise & color
        color = (255, 0, 0)
        terrain_value = round(terrain_generation(chunk_x, chunk_y, self.seed, 750), 2)
        etc_value = round(etc_generation(chunk_x, chunk_y, self.seed, 0.003), 2)
        mountain = 240
        dark_grass = 210
        light_grass = 130
        water = 90

        if 255 < terrain_value:  # high_snow
            color = self.color["high_snow"]
        elif mountain <= terrain_value <= 255:  # snow_mountain
            color = self.color["snow_mountain"]
        elif dark_grass <= terrain_value < mountain:  # mountain
            color = self.color["mountain"]
        elif light_grass < terrain_value < dark_grass:  # dark_grass
            color = self.color["dark_grass"]
        elif water < terrain_value <= light_grass:  # light_grass
            color = self.color["light_grass"]
        elif 0 <= terrain_value <= water:  # lakes
            color = self.color["lakes"]

        if do_etc:
            if color == self.color["mountain"] and 180 <= etc_value <= 190: # gold
                color = self.color["gold"]
            elif color == self.color["dark_grass"] and (0 <= etc_value <= 90 or 95 <= etc_value <= 110): # forest
                color = self.color["forest"]

        # Store to world data
        world_data[(rx, ry)] = color


    def interaction(self, rect, rx, ry, chunk_x, chunk_y):
        mx, my = mouse_pos
        if rect.collidepoint(mx, my):
            if mouse_buttons[0]:
                world_data[(rx, ry)] = self.color["brick"]
            if mouse_buttons[2]:
                self.generate(rx, ry, chunk_x, chunk_y, do_etc=False)









def Main():
    global keys, mouse_buttons, mouse_pos, WINDOW_WIDTH, WINDOW_HEIGHT, all_season_tick

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
                pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pg.RESIZABLE)

        if all_season_tick % 60 == 0:
            # print(world_data, all_season_tick, clock.get_fps())
            print(all_season_tick, clock.get_fps())

        world.update()
        pg.display.update()
        clock.tick(FPS)
        all_season_tick += 1




if __name__ == "__main__":
    world = World()
    Main()



# I think it's the final version, the Perlin noise part is full on AI.
# It's way efficient than ealier version, but still pretty bad
