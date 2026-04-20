from matplotlib.backend_bases import MouseButton
import numpy as np
import config
from sprite import Ball, Hole
from table import Table
from tree import Tree
import path
from graphic import Graphic
import math
import tkinter as tk
import algo


radius = config.radius
length = config.length
width = config.width

holes = [Hole(np.matrix([[radius], [radius]])), Hole(np.matrix([[radius], [width/2]])), Hole(np.matrix([[radius], [width - radius]])),
         Hole(np.matrix([[length - radius], [radius]])), Hole(np.matrix([[length-radius], [width/2]])), Hole(np.matrix([[length - radius], [width - radius]]))]
origin = np.matrix([[0], [0]])


def pool(mball, tballs, cushion_amt, path_amt):
    table = []
    table = Table(np.matrix([[cushion_amt], [cushion_amt]]),
                  origin, mball, tballs, holes)
    tree_node = []
    tree_node = Tree.find_mtable_tree(cushion_amt).root

    avail_paths = path.LinkedList()
    q = []
    q.append(tree_node)
    while (len(q) > 0):
        current = q.pop(0)

        # mother cushion path
        mball_paths = path.find_all_paths(table, table.mirror_table(
            np.matrix([[current.index[0]], [current.index[1]]])), "mball")
        path_node = mball_paths.first
        while path_node != None:
            if not path.is_moving_valid(path_node.moving_list, table):
                mball_paths.remove(path_node)
            else:
                to_be_inserted_node = path.PathNode(
                    no=path_node.no, moving_list=path_node.moving_list)
                avail_paths.push_back(to_be_inserted_node)
            path_node = path_node.next

        # target cushion path
        tball_paths = path.find_all_paths(table, table.mirror_table(
            np.matrix([[current.index[0]], [current.index[1]]])), "tball")
        path_node = tball_paths.first
        while path_node != None:
            if not path.is_moving_valid(path_node.moving_list, table):
                tball_paths.remove(path_node)
            else:
                to_be_inserted_node = path.PathNode(
                    no=path_node.no, moving_list=path_node.moving_list)
                avail_paths.push_back(to_be_inserted_node)
            path_node = path_node.next

        for child in current.child:
            q.append(child)

    # print("after validation")
    path_node = avail_paths.first
    path_dict = {}
    while path_node != None:
        moving_list = path_node.moving_list
        evaluation = path.calculate_evaluation(moving_list)
        path_dict[evaluation] = path_node
        path_node = path_node.next

    sorted_paths = sorted(path_dict.items())

    if len(sorted_paths) > path_amt:
        for i in range(len(sorted_paths)-path_amt, len(sorted_paths)):
            path_no = sorted_paths[i][1].no
            evaluation = sorted_paths[i][0]
            print(path_no, "evaluation", evaluation)
            moving_list = sorted_paths[i][1].moving_list

    mballpath = path.mball_path_after_hit(
        moving_list, 1)  
    print('\n=========moving list==========')
    testinfo = 0
    while testinfo <= len(moving_list)-1:
        print(moving_list[testinfo])
        testinfo += 1
    print('=========moving list==========')
    draw(moving_list, mballpath, 1)
    return mballpath[0]


def draw_balls(moving_list, mballpath, save_or_show):
    graphic = Graphic()
    graphic._set_facecolor()
    graphic._set_mball(mball, "w")
    graphic._set_tballs(tballs, "#f6de01")
    graphic._set_moving_list(moving_list)
    graphic._set_mball_path(mballpath)
    graphic._set_mball_final([float(mballpath[-1][0]), float(mballpath[-1][1])], 'w')
    if save_or_show == 1:
        graphic._savefig("collision_path.png", dpi=1200)
    else:
        graphic._show()


def draw(moving_list, mballpath, save_or_show):
    '''draw the graphic'''
    global graphic
    graphic = Graphic()
    graphic._set_facecolor()
    graphic._set_mball(mball, "w")
    graphic._set_tballs(tballs, "#f6de01")
    graphic._set_balls_pos(moving_list)
    graphic._set_moving_list(moving_list)
    

    if save_or_show == 0:
        graphic._savefig("case_8ball.png", dpi=1200)
        print("case_8ball.png Figure Saved!")
    else:
        # print(mballpath[len(mballpath)-1])  # cue ball's final position
        graphic._show()




tballs = []
'''Case 8 ball'''
# cue
cuex, cuey = 21, 192.5
# ball 2
xb2, yb2 = 81.5, 176
# ball 3
xb3, yb3 = 48.5, 162
# ball 4
xb4, yb4 = 44, 155
# ball 5
xb5, yb5 = 65.5, 158
# ball 6
xb6, yb6 = 29.75, 38.5
# ball 7
xb7, yb7 = 27, 124.25
# ball 8
xb8, yb8 = 4, 159
# ball 9
xb9, yb9 = 64, 94
# ----------------------------------------
mball = Ball(np.matrix([[cuex], [cuey]]))


tballs.append(Ball(np.matrix([[xb2], [yb2]])))
tballs.append(Ball(np.matrix([[xb3], [yb3]])))
tballs.append(Ball(np.matrix([[xb4], [yb4]])))
tballs.append(Ball(np.matrix([[xb5], [yb5]])))
tballs.append(Ball(np.matrix([[xb6], [yb6]])))
tballs.append(Ball(np.matrix([[xb7], [yb7]])))
tballs.append(Ball(np.matrix([[xb8], [yb8]])))
tballs.append(Ball(np.matrix([[xb9], [yb9]])))
contact_point = pool(mball, tballs, 4, 1)