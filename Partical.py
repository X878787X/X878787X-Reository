import ctypes
import pygame as pg
import random as r

ctypes.windll.user32.SetProcessDPIAware() #Correct Pixel Count
pg.init()
pg.mixer.set_num_channels(69420)
FPS = 60
WINDOW_WIDTH, WINDOW_HEIGHT = 1600, 1000
SURF = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
SURF.fill((26, 26, 26))
pg.display.set_caption("Main")
pg.display.flip()
clock = pg.time.Clock()

keys = pg.key.get_pressed()
mouse_buttons = pg.mouse.get_pressed()
mouse_pos = pg.mouse.get_pos()

particle_group = pg.sprite.Group()
blue_particle_surfaces = {}
def particle_init():
    particle_diction = { # total 25 digit, 0 for empty, 1&2 for color, in a 5*5 grid
        "horizontal": (0, 0, 0, 0, 0,
                       0, 1, 1, 1, 0,
                       1, 2, 2, 2, 1,
                       0, 1, 1, 1, 0,
                       0, 0, 0, 0, 0,),
        "tiltLeft": (0, 1, 0, 0, 0,
                     1, 2, 1, 0, 0,
                     0, 1, 2, 1, 0,
                     0, 0, 1, 2, 1,
                     0, 0, 0, 1, 0,),
        "vertical": (0, 0, 1, 0, 0,
                     0, 1, 2, 1, 0,
                     0, 1, 2, 1, 0,
                     0, 1, 2, 1, 0,
                     0, 0, 1, 0, 0,),
        "tiltRight": (0, 0, 0, 1, 0,
                      0, 0, 1, 2, 1,
                      0, 1, 2, 1, 0,
                      1, 2, 1, 0, 0,
                      0, 1, 0, 0, 0,),
    }
    scale = 2 # increase size by *
    color_set = ((0, 0, 0, 0),         # 0, Transparent (forth number in color is transparency)
                 (0, 160, 230, 255),   # 1, First Color
                 (150, 210, 230, 255)) # 2, Second Color

    for name, pattern in particle_diction.items(): # turn the diction into Shape/Surfaces
        # Create surface with scaled size (e.g., 10x10 for scale_factor=2)
        surface = pg.Surface((5 * scale, 5 * scale), pg.SRCALPHA)
        for i in range(25):
            x, y = i % 5, i // 5
            # Scale each pixel to a block (e.g., 2x2 for scale_factor=2)
            for dx in range(scale):
                for dy in range(scale):
                    surface.set_at(
                        (x * scale + dx, y * scale + dy),
                        color_set[pattern[i]]
                    )
        blue_particle_surfaces[name] = surface




class Particle(pg.sprite.Sprite):
    def __init__(self, pos, species):
        super().__init__()
        # noinspection ALL
        particle_group.add(self)
        self.x, self.y = pos
        self.speed = 5
        self.speed_decay = 0.9
        self.minimum_speed = 0.01


        self.life_tick = 0
        self.version = 0 # which one in particle list


        self.direction = r.randint(0, 1) # 0 for left, 1 for right
        self.rotating_speed = 1 # larger is slower

        self.x_velocity = r.uniform(-self.speed, self.speed)
        self.y_velocity = r.uniform(-self.speed, self.speed)

        if species == "blue_particle":
            self.particle_list = list(blue_particle_surfaces.keys()) # get all particle
            self.particle = blue_particle_surfaces[self.particle_list[self.version]] # current displayed particle
        else:
            self.kill()

        self.velocity_bias = "None" # Up, Left, Right, Down
        if self.velocity_bias == "up":
            self.y_velocity = -abs(self.y_velocity)
        elif self.velocity_bias == "left":
            self.x_velocity = -abs(self.x_velocity)
        elif self.velocity_bias == "right":
            self.x_velocity = abs(self.x_velocity)
        elif self.velocity_bias == "down":
            self.y_velocity = abs(self.y_velocity)

    def update(self):
        self.particle = blue_particle_surfaces[self.particle_list[self.version]] # current displayed particle

        # change in speed
        self.x += self.x_velocity
        self.y += self.y_velocity
        self.x_velocity *= self.speed_decay
        self.y_velocity *= self.speed_decay
        if self.minimum_speed >= self.x_velocity >= -self.minimum_speed and self.minimum_speed >= self.y_velocity >= -self.minimum_speed:
            if not r.randint(0, 10): # randomize the chance of death
                self.kill()


        self.rotating_speed += 0.1


        if self.life_tick % int(self.rotating_speed) == 0:
            if self.direction:
                self.version += 1
            else:
                self.version -= 1
        if self.version >= len(self.particle_list) or self.version <= -len(self.particle_list):
            self.version = 0


        self.life_tick += 1
        SURF.blit(self.particle, (int(self.x), int(self.y)))










def Main():
    global keys, mouse_buttons, mouse_pos

    while True:
        SURF.fill((26, 26, 26))
        for event in pg.event.get():
            keys = pg.key.get_pressed()
            mouse_buttons = pg.mouse.get_pressed()
            mouse_pos = pg.mouse.get_pos()
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        if mouse_buttons[0]:
            Particle(mouse_pos, "blue_particle")

        particle_group.update()
        pg.display.update()
        clock.tick(FPS)




if __name__ == "__main__":
    particle_init()
    Main()



# thought
# list for data (color/empty)
#