import ctypes
import pygame as pg
import random as r
import math as m

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

bullet_group = pg.sprite.Group()



class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 10
        self.x, self.y = WINDOW_WIDTH//2 - self.size//2, WINDOW_HEIGHT//2 - self.size//2
        self.rect = pg.Rect(self.x, self.y, self.size, self.size)
        self.x_velocity, self.y_velocity = 0, 0
        self.maxspeed = 6

    def update(self):
        self.x += self.x_velocity
        self.y += self.y_velocity
        # Keep player within screen bounds
        self.x = max(0, min(self.x, WINDOW_WIDTH - self.rect.width))
        self.y = max(0, min(self.y, WINDOW_HEIGHT - self.rect.height))
        # Update rect position
        self.rect.x, self.rect.y = self.x, self.y
        self.control()

        pg.draw.rect(SURF, (0, 255, 0), self.rect)

    def control(self): # all input into Player
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


        if mouse_buttons[0]:
            self.shot()



    def shot(self):
        Bullet(self, mouse_pos)

class Bullet(pg.sprite.Sprite):
    # Notes
    # Self.Rect.Center is the head of moving line
    # In hit_box_list, first element is near the pos(vectorized self.rect.center), last element is prev_pos
    #   (Clarification https://grok.com/chat/b13629a6-bcdc-429c-a32f-8e2b002fc49b)
    def __init__(self, parent, target):
        super().__init__()
        self.parent = parent
        self.target = pg.Vector2(target)
        self.pos = pg.Vector2(parent.rect.center)
        self.prev_pos = pg.Vector2(parent.rect.center)
        self.hit_box_list = []  # Positions for hit detection between prev_pos and current pos
        self.life_tick = 0 # count how long the bullet exist
        self.size = 2 # 2 work the best

        self.pb_speed = True  # Add parent speed to bullet speed
        self.pb_degradation = 10  # Retain percentage of parent's speed (0-100)
        self.low_performance = False # ~double the frame rate
        self.life_spam = 3 # how many seconds, 60 frame/tick = 1 second


        self.color = (255, 255, 0)
        self.speed = 30
        self.speed_offset = 0  # slight offset in speed
        self.angle_offset = 1  # Spread offset in degrees


        self.speed += r.uniform(-self.speed_offset, self.speed_offset) # offset in speed

        self.rect = pg.Rect(self.pos.x - self.size / 2, self.pos.y - self.size / 2, self.size, self.size)
        if parent.rect.center == target:  # Avoid division by zero in normalization
            return
        else:
            # noinspection ALL
            bullet_group.add(self)

        base_direction = (self.target - self.pos).normalize().rotate(r.uniform(-self.angle_offset, self.angle_offset))
        if self.pb_speed: # turn the target pos into angle
            player_velocity = pg.Vector2(parent.x_velocity, parent.y_velocity) * (self.pb_degradation / 100)
            self.direction = base_direction * self.speed + player_velocity
            self.speed = self.direction.length()
        else:
            self.direction = base_direction * self.speed

    def update(self):
        self.life_tick += 1
        print(self.life_tick)

        self.position_readout()
        self.render() # Draw small rect at interpolated position

        # check lifetime/speed (you don't want to wait 10 years for it to be out of bounds)
        if self.life_tick >= self.life_spam*FPS or self.speed <= 0.5:
            self.kill()

    def position_readout(self): # interpolate the points between frames
        self.hit_box_list = []

        self.prev_pos = self.pos.copy()
        self.pos += self.direction
        distance = self.pos.distance_to(self.prev_pos)

        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

        # Check if out of bounds (using rect for precision)
        if self.rect.right < -10 or self.rect.left > WINDOW_WIDTH + 10 or self.rect.bottom < -10 or self.rect.top > WINDOW_HEIGHT + 10:
            self.kill()

        # Interpolate only if significant movement to fill visual/hit gaps
        if distance >= 2:
            num_points = int(distance / 2)
            for i in range(1, num_points + 1):  # Start from 1 to exclude prev_pos (already handled last frame)
                t = i / num_points
                interp_pos = self.prev_pos + (self.pos - self.prev_pos) * t
                interp_center = (int(interp_pos.x), int(interp_pos.y))
                self.hit_box_list.append(interp_center)

        else:
            # For small movements, just use current position
            current_center = (self.rect.centerx, self.rect.centery)
            self.hit_box_list.append(current_center)
            pg.draw.rect(SURF, self.color, self.rect)

        self.hit_box_list.reverse() # Inverse the hit_box_list so the head of line is first of the list

    def render(self):
        if self.low_performance: # simpler render
            for i in self.hit_box_list:
                pg.draw.rect(SURF, self.color, (i[0] - self.size / 2, i[1] - self.size / 2, self.size, self.size))
        else:  # The head of the bullet is the brightest and back is dark
            # Get the first coordinate as reference
            start_x, start_y = self.hit_box_list[0]

            # Find the maximum distance from the first point
            max_distance = 0
            for x, y in self.hit_box_list[1:]:
                distance = m.sqrt((x - start_x) ** 2 + (y - start_y) ** 2)
                max_distance = max(max_distance, distance)

            # Draw each dot
            for i, (x, y) in enumerate(self.hit_box_list):
                # Calculate distance from first point
                distance = m.sqrt((x - start_x) ** 2 + (y - start_y) ** 2)

                # Calculate alpha (0 = transparent, 255 = opaque)
                if max_distance == 0:  # If all points are at the same location
                    alpha = 255
                else:
                    # Linear interpolation: closer points are more opaque
                    alpha = int(255 * (1 - distance / max_distance))

                # Create a surface for the dot
                dot_surface = pg.Surface((5, 5), pg.SRCALPHA)
                # Draw circle on the surface
                pg.draw.circle(dot_surface, (*self.color, alpha), (2.5, 2.5), self.size/2)
                # Blit the dot onto the main screen
                SURF.blit(dot_surface, (x - 2.5, y - 2.5))



















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
        bullet_group.update()

        pg.display.update()
        clock.tick(FPS)
        # print(clock.get_fps())






if __name__ == "__main__":
    player = Player()
    Main()





