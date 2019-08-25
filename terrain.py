# A simple Python port of https://github.com/s-macke/VoxelSpace by Sebastian Macke
# Autor: Peter Sovietov

import json
import gzip
import tkinter as tk


SCREEN_WIDTH = 320
SCREEN_HEIGHT = 200
BACK_COLOR = (153, 204, 255)


def to_ppm(array, width, height):
    return bytes("P6\n%d %d\n255\n" % (width, height), "ascii") + array


def load_data():
    with gzip.GzipFile("c1w.json.gz", "rb") as f:
        colors = json.loads(f.read().decode())
    with gzip.GzipFile("d1.json.gz", "rb") as f:
        heights = json.loads(f.read().decode())
    return colors, heights


class Terrain:
    def __init__(self):
        self.player_x = 0
        self.player_y = 0
        self.height = 70
        self.horizon = 70
        self.scale_height = 100
        self.distance = 800
        self.colors, self.heights = load_data()
        self.heights = [SCREEN_HEIGHT - x for x in self.heights]
        self.background = bytearray(BACK_COLOR * SCREEN_WIDTH * SCREEN_HEIGHT)
        self.screen = self.background[:]
        self.ybuffer = [SCREEN_HEIGHT for i in range(SCREEN_WIDTH)]

    def draw_vline(self, x, y1, y2, color):
        r, g, b = color
        y1 = max(int(y1), 0)
        y1 = 3 * (y1 * SCREEN_WIDTH + x)
        y2 = 3 * (y2 * SCREEN_WIDTH + x)
        screen = self.screen
        for y in range(y1, y2, 3 * SCREEN_WIDTH):
            screen[y] = r
            screen[y + 1] = g
            screen[y + 2] = b

    def render(self):
        ybuffer = self.ybuffer[:]
        z = 1
        dz = 1
        while int(z) < self.distance:
            left_x = self.player_x - z
            left_y = self.player_y + z
            right_x = self.player_x + z
            right_y = self.player_y - z
            dx = (right_x - left_x) / SCREEN_WIDTH
            scale = self.scale_height / z
            offs_y = 1024 * (int(left_y) % 1024)
            for i in range(SCREEN_WIDTH):
                offs = offs_y + int(left_x) % 1024
                h = int(self.heights[offs] * scale) + self.horizon
                if h < ybuffer[i]:
                    self.draw_vline(i, h, ybuffer[i], self.colors[offs])
                    ybuffer[i] = h
                left_x += dx
            z += dz
            dz += 0.02

    def update_screen(self):
        self.screen[:] = self.background
        self.render()
        self.player_y += 8
        data = to_ppm(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        image = tk.PhotoImage(data=data).zoom(2, 2)
        label.config(image=image)
        label.image = image
        root.after(10, self.update_screen)


root = tk.Tk()
label = tk.Label()
label.pack()
terrain = Terrain()
root.after(0, terrain.update_screen)
tk.mainloop()
