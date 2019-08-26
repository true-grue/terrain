# A simple Python port of VoxelSpace by Sebastian Macke
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


def draw_vline(screen, x, y1, y2, color):
    r, g, b = color
    y1 = 3 * (max(y1, 0) * SCREEN_WIDTH + x)
    y2 = 3 * (min(y2, SCREEN_HEIGHT) * SCREEN_WIDTH + x)
    for y in range(y1, y2, 3 * SCREEN_WIDTH):
        screen[y] = r
        screen[y + 1] = g
        screen[y + 2] = b


class Terrain:
    def __init__(self, widget):
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
        self.widget = label

    def render(self):
        ybuf = self.ybuffer[:]
        z = 1
        dz = 1
        while z < self.distance:
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
                if h < ybuf[i]:
                    draw_vline(self.screen, i, h, ybuf[i], self.colors[offs])
                    ybuf[i] = h
                left_x += dx
            z += dz
            dz += 0.02

    def update_screen(self):
        self.screen[:] = self.background
        self.render()
        self.player_y += 8
        data = to_ppm(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        image = tk.PhotoImage(data=data).zoom(2, 2)
        self.widget.config(image=image)
        self.widget.image = image
        Root.after(10, self.update_screen)


Root = tk.Tk()
label = tk.Label()
label.pack()
terrain = Terrain(label)
Root.after(0, terrain.update_screen)
tk.mainloop()
