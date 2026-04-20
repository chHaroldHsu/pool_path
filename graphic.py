import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import config
import random
import numpy as np

plt.switch_backend('TkAgg')
tmp = []

class Graphic:
    def __init__(self):

        # img = plt.imread('table.png')
        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        self.ax.set_aspect('equal')
        self._set_lim()
        # self.ax.imshow(
        #     img, extent=[-30, config.length + 30, -30, config.width + 30])

        # self._set_facecolor("#62A66F")

    def _set_clear(self):
        self.ax.patches.pop()

    def _set_lim(self):
        self.ax.set_xlim((-30, config.length + 30))
        self.ax.set_ylim((-30, config.width + 30))

    def _set_facecolor(self):
        img = plt.imread('table.png')
        self.ax.imshow(
            img, extent=[-12, config.length + 12, -12, config.width + 12])
        # self.ax.set_facecolor(color)

    def _set_mball(self, mball, color):
        if self.ax.patches != None:
            # self.ax.patches.pop()
            # print(self.ax.patches)
            mball_plt = plt.Circle(
                [mball.pos[0, 0], mball.pos[1, 0]], radius=config.radius -1, color=color)
        # self._set_text(mball.pos, (mball.pos[0, 0], mball.pos[1, 0]), 6)
        self.ax.add_patch(mball_plt)

    def _set_holes(self, holes, color):
        for hole in holes:
            hole = plt.Circle(
                [hole.pos[0, 0], hole.pos[1, 0]], radius=1, color=color)
            self.ax.add_patch(hole)

    def _set_mball_final(self, mball, color):
        mball_plt = plt.Circle(
            mball, radius=config.radius, color=color, fill=False)
        self.ax.add_patch(mball_plt)
        # self._set_mball_text(mball, (int(mball[0]), int(mball[1])), 6)

    def _set_mball_text(self, pos, text, fontsize):
        self.ax.text(pos[0], pos[1], text, fontsize=fontsize, color='b')

    def _set_tballs(self, tballs, color):
        color = ['#f6de01', '#0264E6','#ce0000','#a001f6','#f66f01','#57ff9d', '#781a1a','#000000', '#e2ed09']
        for i in range(len(tballs)):
            tball_plt = plt.Circle(
                [tballs[i].pos[0, 0], tballs[i].pos[1, 0]], radius=config.radius-1, color=color[i])
            self.ax.add_patch(tball_plt)
            # self._set_text(tballs[i].pos, i+1, 6)

    def _set_moving_list(self, moving_list):
        for j in range(len(moving_list)-1):
            if j == 1:
                j = j + 1
            elif j > 0:
                color = 'r'
            else:
                color = 'w'
            current_pos = moving_list[j].pos
            next_pos = moving_list[j+1].pos
            if j >= 0:
                self._set_line(current_pos, next_pos, color)

    def _set_mball_path(self, mballpath):
        color = 'w'
        for j in range(len(mballpath)-1):
            current_pos = mballpath[j]
            next_pos = mballpath[j+1]
            self._set_line(current_pos, next_pos, color)

    def _set_line(self, current_pos, next_pos, color):
        line = Line2D([current_pos[0, 0], next_pos[0, 0]], [
                      current_pos[1, 0], next_pos[1, 0]], linewidth=1, color=color, linestyle='--')
        self.ax.add_line(line)

    def _set_text(self, pos, text, fontsize):
        self.ax.text(pos[0, 0], pos[1, 0], text, fontsize=fontsize,weight='bold')

    def _set_balls_pos(self, moving_list):
        ball_plt = plt.Circle([float(moving_list[len(moving_list)-3].pos[0, 0]),
            float(moving_list[len(moving_list)-3].pos[1, 0])], radius=config.radius-0.1, color='w', fill=False)

        self.ax.add_patch(ball_plt)

    def _set_area(self, tballs):
        # x = np.linspace(150, 248, num=500)
        # y = -x + 254
        # line = plt.plot(x, y, color='w', linestyle='--', linewidth=1)
        line = Line2D([0, 248], [169.2, 7], linewidth=1,
                      color='r', linestyle='--')
        self.ax.add_line(line)

    def _show(self):
        plt.show()

    def _savefig(self, name, dpi):
        plt.savefig(name, dpi=dpi)

    def _set_holes(self, holes, color):
        for hole in holes:
            hole = plt.Circle([hole.pos[0, 0], hole.pos[1, 0]],
                              radius=1, color=color)
            self.ax.add_patch(hole)
