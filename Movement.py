import ctypes
import pygame as pg

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




class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 10
        self.x, self.y = WINDOW_WIDTH//2 - self.size//2, WINDOW_HEIGHT//2 - self.size//2
        self.rect = pg.Rect(self.x, self.y, self.size, self.size)
        self.x_velocity, self.y_velocity = 0, 0
        self.maxspeed = 6

    def update(self):
        self.control()
        self.x += self.x_velocity
        self.y += self.y_velocity
        # Keep player within screen bounds
        self.x = max(0, min(self.x, WINDOW_WIDTH - self.rect.width))
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.rect.height))
        # Update rect position
        self.rect.x, self.rect.y = self.x, self.y

        pg.draw.rect(SURF, (0, 255, 0), self.rect)

    def control(self):
        # wasd control with diagonal normalization
        move_x, move_y = 0, 0

        if keys[pg.K_w]:
            move_y -= self.maxspeed
        if keys[pg.K_s]:
            move_y += self.maxspeed
        if keys[pg.K_a]:
            move_x -= self.maxspeed
        if keys[pg.K_d]:
            move_x += self.maxspeed
        # Normalize diagonal movement
        if move_x != 0 and move_y != 0:
            factor = 1 / 1.41421356237 # Square root of 2
            move_x *= factor
            move_y *= factor
        self.x_velocity = move_x
        self.y_velocity = move_y










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

        player.update()
        pg.display.update()
        clock.tick(FPS)




if __name__ == "__main__":
    player = Player()
    Main()