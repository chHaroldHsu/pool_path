from math import ceil, floor
import math
import numpy as np

import config


def contact_pos(tpos, hpos):
    """Return contact position of the target ball."""
    diff = hpos - tpos
    if diff[0, 0] != 0:
        theta = math.atan(abs(diff[1, 0] / diff[0, 0]))
    else:
        theta = math.pi / 2
    x_coef = -1 if diff[0, 0] > 0 else 1
    y_coef = -1 if diff[1, 0] > 0 else 1
    x = tpos[0, 0] + x_coef*2*config.radius*math.cos(theta)
    y = tpos[1, 0] + y_coef*2*config.radius*math.sin(theta)
    contact_pos = np.matrix([[x], [y]])
    return contact_pos


def mirror_transformation(pos: np.matrix, index_rr: np.matrix = None, index_ij: np.matrix = None, inverse=False):
    """Return mirror transformation of input position with (i,j) and (r,r)."""
    x_reflect = np.matrix([[1, 0], [0, -1]])
    y_reflect = np.matrix([[-1, 0], [0, 1]])

    if inverse:
        i = floor((pos[0, 0] / config.length))
        j = floor((pos[1, 0] / config.width))
        index_ij = np.matrix([[i], [j]]) + index_rr

    index_diff = index_ij - index_rr
    cx = abs(index_diff[1, 0] % 2)
    cy = abs(index_diff[0, 0] % 2)

    if cx:
        index_diff = index_diff + np.matrix([[0], [1]])
    if cy:
        index_diff = index_diff + np.matrix([[1], [0]])

    if (inverse == False):
        comp_mat = x_reflect ** cx * y_reflect ** cy
        return comp_mat * pos + config.conf * index_diff
    else:
        comp_mat = y_reflect ** (-cy) * x_reflect ** (-cx)
        return comp_mat * (pos - config.conf * index_diff)


def multiples_between_interval(start, end, multiple):
    """Return list of multiples between given interval."""
    mx = max(start, end)
    mn = min(start, end)
    mn = ceil(mn/multiple) * multiple
    mx = ceil(mx/multiple) * multiple
    return list(range(mn, mx, multiple))


def point_between_two_points(x, p1, p2, inverse=False):
    """Return (x,y) with given x or y that on a line between two points."""
    slope = (p2[1, 0]-p1[1, 0]) / (p2[0, 0]-p1[0, 0])
    if not inverse:
        return np.matrix([[x], [slope * (x-p1[0, 0]) + p1[1, 0]]])
    else:
        return np.matrix([[(x-p1[1, 0]) / slope + p1[0, 0]], [x]])

'''
def angle_between_two_vectors(p1, p2):
    """Return angle between two vectors by dot computing."""
    dot_product = dot(p1, p2)
    norm_p1 = norm(p1)
    norm_p2 = norm(p2)
    print(f'點積: {dot_product}, 向量1範數: {norm_p1}, 向量2範數: {norm_p2}')
    cos_angle = math.acos(dot(p1, p2) / (norm(p1) * norm(p2)))
    print(f'夾角的cos值 (修正前): {cos_angle}')
    cos_angle = max(min(cos_angle, 1), -1)  # 將數值限定在 [-1, 1] 範圍內
    print(f'夾角的cos值 (修正後): {cos_angle}')
    return math.acos(dot(p1, p2) / (norm(p1) * norm(p2)))
'''
def angle_between_two_vectors(p1, p2):
    """Return angle between two vectors by dot computing."""
    dot_product = dot(p1, p2)
    norm_p1 = norm(p1)
    norm_p2 = norm(p2)
    cos_angle = dot_product / (norm_p1 * norm_p2)
    # 將數值限定在 [-1, 1] 範圍內
    cos_angle = max(min(cos_angle, 1), -1)
    return math.acos(cos_angle)

def distance_from_point_to_segment(p, p1, p2):
    """Return distance from point to segment by projection computing."""
    ab_vect = p2 - p1
    ap_vect = p - p1
    ac_proj_vect = dot(ap_vect, ab_vect) * ab_vect / (norm(ab_vect) ** 2)
    r = dot(ab_vect, ap_vect) / (norm(ab_vect) ** 2)
    # print('r=', r)
    if r <= 0:
        return norm(ap_vect)
    elif r >= 1:
        bp_vect = p - p2
        return norm(bp_vect)
    else:
        cp_vect = ap_vect - ac_proj_vect
        return norm(cp_vect)


def distance_from_point_to_line(p, p1, p2):
    """Return distance from point to line by mathematic formula."""
    slope = (p2[1, 0]-p1[1, 0]) / (p2[0, 0]-p1[0, 0])
    b = -slope * p1[0, 0] + p1[1, 0]
    x, y = p[0, 0], p[1, 0]
    return abs((slope * x - y + b) / ((slope ** 2 + 1) ** (1/2)))


def norm(p):
    """Return norm of point."""
    return (p[0, 0] ** 2 + p[1, 0] ** 2) ** (0.5)


def dot(p1, p2):
    """Return dot product with p1, p2."""
    return (p1.T * p2)[0, 0]
