from re import L
import numpy as np
from table import Table
from sprite import Ball, Hole
import algo
import config
import copy
import math
from graphic import Graphic
from math import floor, ceil


class PathNode:
    """A class representing the head of the path."""
    counter = 0

    def __init__(self, no=None, prev=None, next=None, moving_list=None):
        self.set_no(no)
        self.next = next
        self.prev = prev
        self.moving_list = moving_list

    def insert_next(self, node):
        """Insert next node to current and assign prev node of next node to current."""
        self.next = node
        node.prev = self

    def set_no(self, no):
        """Set the number by default counter if there's no one setting number manually."""
        if no == None:
            PathNode.counter += 1
            self.no = "PATH " + str(PathNode.counter)
        else:
            self.no = str(no)

    def __str__(self) -> str:
        return "No: " + self.no


"""Todo: Optimize the time complexity and space complexity"""


class LinkedList:
    """Use LinkedList to optimized frequent method, like REMOVE, INSERT."""

    def __init__(self, first=None):
        self.first = first

    # Time Complexity = O(n), it can be implemented in O(1)
    def push_back(self, node):
        """Push the node back to the last of the linked list."""
        current_node = self.first
        if current_node == None:
            self.first = node
        else:
            while current_node.next != None:
                current_node = current_node.next
            current_node.insert_next(node)

    def remove(self, node):
        """Remove specific node in the linked list."""
        current_node = self.first
        if current_node == None:
            return False
        else:
            while current_node != None:
                if current_node == node:
                    # Case of only one node in linkedlist, then free the first node to None
                    if current_node.prev == None and current_node.next == None:
                        self.first = None
                    # Case of node being head
                    elif current_node.prev == None:
                        next = current_node.next
                        next.prev = None
                        self.first = next
                    elif current_node.next == None:
                        prev = current_node.prev
                        prev.next = None
                    else:
                        current_node.prev.next = current_node.next
                        current_node.next.prev = current_node.prev
                current_node = current_node.next

    def traverse(self):
        current = self.first
        while current != None:
            print("Current", current, "Next",
                  current.next, "Prev", current.prev)
            current = current.next


class MovingNode:
    """A class representing the moving of the path.
        Because it is only for READ, using List to store is enough."""

    def __init__(self, pos: np.matrix, type):
        self.pos = pos
        self.type = type

    def __str__(self) -> str:
        return "Type: " + str(self.type) + "\nPos: " + str(self.pos)


radius = config.radius - 4
length = config.length
width = config.width

holes = [Hole(np.matrix([[radius], [radius]])), Hole(np.matrix([[radius], [width/2]])), Hole(np.matrix([[radius], [width - radius]])),
         Hole(np.matrix([[length - radius], [radius]])), Hole(np.matrix([[length-radius], [width/2]])), Hole(np.matrix([[length - radius], [width - radius]]))]


def line_intersect_circle(p, lsp, esp):
    '''when the first shot collide next target, use this function to calculate the contact point'''
    # p is the circle parameter, lsp and lep is the two end of the line
    x0, y0, r0 = p
    x1, y1 = lsp
    x2, y2 = esp
    if r0 == 0:
        return [[x1, y1]]
    if x1 == x2:
        if abs(r0) >= abs(x1 - x0):
            p1 = x1, y0 - math.sqrt(r0 ** 2 - (x1 - x0) ** 2)
            p2 = x1, y0 + math.sqrt(r0 ** 2 - (x1 - x0) ** 2)
            inp = [p1, p2]
            # select the points lie on the line segment
            inp = [p for p in inp if p[0] >= min(
                x1, x2) and p[0] <= max(x1, x2)]
        else:
            inp = []
    else:
        k = (y1 - y2) / (x1 - x2)
        b0 = y1 - k * x1
        a = k ** 2 + 1
        b = 2 * k * (b0 - y0) - 2 * x0
        c = (b0 - y0) ** 2 + x0 ** 2 - r0 ** 2
        delta = b ** 2 - 4 * a * c
        if delta >= 0:
            p1x = (-b - math.sqrt(delta)) / (2 * a)
            p2x = (-b + math.sqrt(delta)) / (2 * a)
            p1y = k * p1x + b0
            p2y = k * p2x + b0
            inp = [[p1x, p1y], [p2x, p2y]]
            # select the points lie on the line segment
            inp = [p for p in inp if p[0] >= min(
                x1, x2) and p[0] <= max(x1, x2)]
        else:
            inp = []

    return inp if inp != [] else [[x1, y1]]


def next_tball_pos_angle(mballpath, tball_hole_vector, target_score):
    '''use while loop to try the better position for next ball'''
    best_pocket_id = target_score[0][0]
    best_pocket_pos = holes[best_pocket_id].pos
    path_vector = best_pocket_pos - mballpath
    cos = math.degrees(math.acos((int(path_vector[0]) * int(tball_hole_vector[best_pocket_id][0]) + int(path_vector[1]) * int(tball_hole_vector[best_pocket_id][1])) / (
        np.sqrt(int(path_vector[0]) ** 2 + int(path_vector[1]) ** 2) * np.sqrt(int(tball_hole_vector[best_pocket_id][0]) ** 2 + int(tball_hole_vector[best_pocket_id][1]**2)))))

    return cos


def find_all_path_for_next_tball(tballs):
    '''to find path for next target ball to all the hole'''
    tball = tballs[1]
    tball_hole_vector = []
    for hole in holes:
        vector = hole.pos - tball.pos
        tball_hole_vector.append(vector)
    return tball_hole_vector


def calculate_cosine_value_to_pocket_for_next_tball(tball_hole_vector):
    '''to calculate the value of cosine theta for the next target ball'''
    vector_for_holes = [np.matrix([[1], [1]]), np.matrix([[1], [0]]), np.matrix(
        [[1], [-1]]), np.matrix([[-1], [1]]), np.matrix([[-1], [1]]), np.matrix([[-1], [-1]])]
    i = 0
    cosine = []
    while i <= 5:
        A = tball_hole_vector
        B = vector_for_holes
        cos = (int(A[i][0]) * int(B[i][0]) + int(A[i][1]) * int(B[i][1])) / \
            (np.sqrt(int(A[i][0]) ** 2 + int(A[i][1]) ** 2)
             * np.sqrt(int(B[i][0]) ** 2 + int(B[i][1]**2)))
        i = i + 1
        cosine.append(cos)
    return cosine


def calculate_distance_to_pocket_for_next_tball(tball_hole_vector):
    '''get the distance from each pocket to tball'''
    next_tball_distance = []
    i = 0
    while i <= 5:
        distance = (
            np.sqrt(int(tball_hole_vector[i][0])**2 + int(tball_hole_vector[i][1])**2))/100
        next_tball_distance.append(distance)
        i = i + 1
    return next_tball_distance


def pocket_rank(target_score):
    '''to sort the target score from high to low'''
    i = 0
    while i < 5:
        j = 0
        while j < 5:
            if target_score[j][1] < target_score[j+1][1]:
                temp = target_score[j]
                target_score[j] = target_score[j+1]
                target_score[j+1] = temp
            j = j + 1
        i = i + 1
    return target_score


def calculate_target_score(cosine_value, next_tball_distance):
    '''to calculate the target score (cos^2/distance)'''
    target_score = []
    i = 0
    while i <= 5:
        score = round((cosine_value[i]**2) / (next_tball_distance[i]), 4)
        score = (i, score)
        target_score.append(score)
        i = i + 1
    # print(target_score)
    return target_score


def mball_path_after_hit(moving_list, path_size):
    """Return the position of mball after hitting tball"""
    mballpath = []
    rotate_90 = np.matrix([[0, 1], [-1, 0]])
    rotate_270 = np.matrix([[0, -1], [1, 0]])
    tballpath_vector = moving_list[3].pos - moving_list[2].pos
    mball_to_contactpos_vector = moving_list[1].pos - moving_list[0].pos
    mballpath.append(moving_list[1].pos)
    path1_vector = rotate_90*tballpath_vector*path_size
    path2_vector = rotate_270*tballpath_vector*path_size
    mballpath1_pos = path1_vector + moving_list[1].pos
    mballpath2_pos = path2_vector + moving_list[1].pos

    theta1 = (path1_vector.T * mball_to_contactpos_vector).item() / (math.sqrt(float(path1_vector[0, 0])**2 + float(path1_vector[1, 0])**2)*math.sqrt(
        float(mball_to_contactpos_vector[0, 0])**2 + float(mball_to_contactpos_vector[1, 0])**2))
    theta2 = (path2_vector.T * mball_to_contactpos_vector).item() / (math.sqrt(float(path2_vector[0, 0])**2 + float(path2_vector[1, 0])**2)*math.sqrt(
        float(mball_to_contactpos_vector[0, 0])**2 + float(mball_to_contactpos_vector[1, 0])**2))
    if theta1 > 0:
        # mballpath.append(mballpath1)
        mballpath0_pos = mballpath1_pos
        path_vector = path1_vector
    elif theta2 > 0:
        # mballpath.append(mballpath2)
        mballpath0_pos = mballpath2_pos
        path_vector = path2_vector

    # cloth_points = mballpath_cloth(mballpath0_pos, path_vector)
    # i = 0
    # while i < len(cloth_points):
    #     mballpath.append(cloth_points[i])
    #     i += 1
    # mballpath.append(mballpath_mirror_transfrom(mballpath0_pos))
    return mball_vector_size_after_collide(mballpath, mballpath0_pos, path_vector)


def mball_vector_size_after_collide(mballpath, mballpath0_pos, path_vector):
    cloth_points = mballpath_cloth(mballpath0_pos, path_vector)
    i = 0
    while i < len(cloth_points):
        mballpath.append(cloth_points[i])
        i += 1
    mballpath.append(mballpath_mirror_transfrom(mballpath0_pos))
    return mballpath


def mballpath_cloth(mballpath, path_vector):
    '''Return the positions that mball will collide the cushion'''
    cloth_point = []
    x_cloth_time = floor(float(mballpath[0, 0])/config.length)
    y_cloth_time = floor(float(mballpath[1, 0])/config.width)
    while x_cloth_time > 0:
        cloth_point.append(path_formula(
            mballpath, path_vector, True, x_cloth_time*config.length))
        x_cloth_time -= 1
    while x_cloth_time < 0:
        cloth_point.append(path_formula(
            mballpath, path_vector, True, (x_cloth_time+1)*config.length))
        x_cloth_time += 1
    while y_cloth_time > 0:
        cloth_point.append(path_formula(
            mballpath, path_vector, False, y_cloth_time*config.width))
        y_cloth_time -= 1
    while y_cloth_time < 0:
        cloth_point.append(path_formula(
            mballpath, path_vector, False, (y_cloth_time+1)*config.width))
        y_cloth_time += 1
    i = j = 0
    if len(cloth_point) > 1:
        while i < len(cloth_point):
            while j < len(cloth_point)-1:
                if cloth_point[j][0] > cloth_point[j+1][0]:
                    temp = cloth_point[j][0]
                    cloth_point[j] = cloth_point[j+1]
                    cloth_point[j+1] = temp
                    j += 1
                i += 1
    i = 0
    while i < len(cloth_point):
        if cloth_point[i][0] % config.length == 0:
            cloth_point[i][1] = cloth_point[i][1] % config.width
            if cloth_point[i][0] > 0:
                cloth_point[i][0] = cloth_point[i][0]
            else:
                cloth_point[i][0] = cloth_point[i][0]
        elif cloth_point[i][1] % config.width == 0:
            cloth_point[i][0] = cloth_point[i][0] % config.length
            if cloth_point[i][1] > 0:
                cloth_point[i][1] = cloth_point[i][1]
            else:
                cloth_point[i][1] = cloth_point[i][1]
        else:
            cloth_point[i][0] = cloth_point[i][0] % config.length
            cloth_point[i][1] = cloth_point[i][1] % config.width
            if cloth_point[i][0] > (config.length):
                cloth_point[i][0] = cloth_point[i][0]
            elif cloth_point[i][0] < config.radius:
                cloth_point[i][0] = cloth_point[i][0]
            if cloth_point[i][1] > (config.width):
                cloth_point[i][1] = cloth_point[i][1]
            elif cloth_point[i][1] < config.radius:
                cloth_point[i][1] = cloth_point[i][1] + config.radius
        i += 1
    return cloth_point


def path_formula(mballpath, path_vector, x_or_y, A):
    '''Find the point on the line equation'''
    a = int(path_vector[0, 0])
    b = int(path_vector[1, 0])
    c = int(b*float(mballpath[0, 0]) - a*float(mballpath[1, 0]))
    if x_or_y:
        y = (b*A-c)/a
        pos = np.matrix([[A], [y]])
        return pos
    else:
        x = (c-a*A)/b
        pos = np.matrix([[x], [A]])
        return pos


def mballpath_mirror_transfrom(mballpath):
    '''Find the final position of mball in the table'''
    x = float(mballpath[0, 0])
    y = float(mballpath[1, 0])

    if x > 0:
        y_reflect_times = floor(x / config.length)
        if y_reflect_times == 0:
            x = abs(x)
        elif y_reflect_times >= 1 & y_reflect_times % 2 == 1:
            x = config.length*(y_reflect_times+1) - x
        elif y_reflect_times >= 1 & y_reflect_times % 2 == 0:
            x = x - config.length*y_reflect_times
    elif x < 0:
        y_reflect_times = floor(abs(x) / config.length)
        x = abs(x)
        if y_reflect_times == 0:
            x = abs(x)
        elif y_reflect_times >= 1 & y_reflect_times % 2 == 1:
            x = config.length*(y_reflect_times+1) - x
        elif y_reflect_times >= 1 & y_reflect_times % 2 == 0:
            x = x - config.length*y_reflect_times

    if y > 0:
        x_reflect_times = floor(y / config.width)
        if x_reflect_times == 0:
            y = abs(y)
        elif x_reflect_times >= 1 & x_reflect_times % 2 == 1:
            y = config.width*(x_reflect_times+1) - y
        elif x_reflect_times >= 1 & x_reflect_times % 2 == 0:
            y = y - config.width*x_reflect_times
    elif y < 0:
        x_reflect_times = floor(abs(y) / config.width)
        y = abs(y)
        if x_reflect_times == 0:
            y = abs(y)
        elif x_reflect_times >= 1 & x_reflect_times % 2 == 1:
            y = config.width*(x_reflect_times+1) - y
        elif x_reflect_times >= 1 & x_reflect_times % 2 == 0:
            y = y - config.width*x_reflect_times

    mballpath[0, 0] = x
    mballpath[1, 0] = y
    return mballpath


def calculate_evaluation(moving_list):
    """Return the evaluation of moving list with angles, distance and cushion_count."""
    angles = angles_of_approach_in_moving_list(moving_list)
    distance = total_distance(moving_list)
    cushion_cnt = cushion_count(moving_list)

    return evaluation(angles, cushion_cnt, distance)


def cushion_count(moving_list):
    """Return the cushion count of moving list"""
    cushion_count = -4
    cushion_type_count_dict = {}
    for moving in moving_list:
        if cushion_type_count_dict.get(moving.type) == None:
            cushion_type_count_dict[moving.type] = 1
        else:
            cushion_type_count_dict[moving.type] += 1
    for type in cushion_type_count_dict:
        cushion_count += cushion_type_count_dict[type]
    return cushion_count


def total_distance(moving_list):
    """Return total distance of all moving path."""
    distance = 0
    for i in range(len(moving_list)-1):
        current_moving = moving_list[i]
        next_moving = moving_list[i+1]
        distance += algo.norm(next_moving.pos - current_moving.pos)
    return distance


def evaluation(angles, cushion_count, dist):
    """Return the evaluation of the path with crucial params, like angle, cushion_count, distance."""
    angle_evaluation = 1
    for angle in angles:
        angle_evaluation *= math.cos(angle)
    cushion_evaluation = config.alpha ** cushion_count
    diagonal_dist = (config.length ** 2 + config.width ** 2) ** (1/2)
    dist_evaluation = math.tanh(diagonal_dist / dist)
    # print("angle", angle_evaluation)
    # print("cushion", cushion_evaluation)
    # print("dist", dist_evaluation)
    # print("\n")
    return angle_evaluation * cushion_evaluation * dist_evaluation


def is_moving_valid(moving_list, table):
    """Determine if the path is valid or not."""
    if not is_angle_valid(moving_list) or are_sprites_on_table_collided_to_path(table, moving_list):
        return False
    return True


def is_angle_valid(moving_list):
    """Check if the angles of approach is less than 90 degree or not,
        if no, it suggests that the mother ball will hit the target ball on the premature position."""

    # There must exist one angle of balls in the moving list.
    angles = angles_of_approach_in_moving_list(moving_list)
    max_angle = max(angles)
    return max_angle < math.pi/2


def angles_of_approach_in_moving_list(moving_list):
    """Return the list of angles of approach in moving list."""
    angles = []
    for i in range(1, len(moving_list)-1):
        current_moving = moving_list[i]
        next_moving = moving_list[i+1]
        prev_moving = moving_list[i-1]
        # If the current type is different from next type, it implys that balls are collided.
        # And it's time to calculate the angle of approach.
        # There is at least one collision in the moving list.
        if current_moving.type != next_moving.type:
            current_to_next_vect = next_moving.pos - current_moving.pos
            prev_to_current_vect = current_moving.pos - prev_moving.pos
            angle = algo.angle_between_two_vectors(
                current_to_next_vect, prev_to_current_vect)
            angles.append(angle)
    return angles


def are_sprites_on_table_collided_to_path(table, moving_list):
    """Check if table is collided to path or not by holes, tballs."""
    # This is extremely important, preventing from popping out the reference object.
    tballs = copy.deepcopy(table.tballs)
    holes = copy.deepcopy(table.holes)

    target_ball = tballs.pop(0)

    sprites = []

    for tball in tballs:
        sprites.append(tball)

    for hole in holes:
        sprites.append(hole)

    if is_target_ball_collided_to_mother_cushion_path(moving_list, target_ball):
        return True

    for sprite in sprites:
        if is_sprite_collided_to_path(moving_list, sprite):
            return True

    return False


def is_target_ball_collided_to_mother_cushion_path(moving_list, tball):
    """Check if the target ball is collided to the path of mother ball cushion."""
    mtype_count = 0
    for i in range(len(moving_list)):
        mtype_count += 1 if moving_list[i].type == "m" else 0
    mother_cushion_moving_list = moving_list[0:mtype_count]
    return is_sprite_collided_to_path(mother_cushion_moving_list, tball, False)


def is_sprite_collided_to_path(moving_list, sprite, is_default_radius=False):
    """Check if the sprite is collided to path or not."""
    sprite_pos = sprite.pos
    hole_pos = moving_list[len(moving_list)-1].pos
    for i in range(len(moving_list)-1):
        current_moving_pos = moving_list[i].pos
        next_moving_pos = moving_list[i+1].pos

        # If the sprite is the end point (HOLE), we must exclude this sprite.
        if algo.norm(sprite_pos - hole_pos) < config.e:
            return False

        # config.e is very crucial because the error of floating computing may occurs.
        if algo.distance_from_point_to_segment(sprite_pos, current_moving_pos, next_moving_pos) < 2*config.radius - config.e:
            return True
    return False


def find_all_paths(root_table: Table, mirror_table: Table, cushion_type=None):
    """Return all paths including not valid ones."""
    path_ll = LinkedList()
    mball = root_table.mball
    tballs = None
    holes = mirror_table.holes

    if cushion_type == 'mball':
        tballs = mirror_table.tballs
    elif cushion_type == 'tball':
        tballs = root_table.tballs

    tball = tballs[0]
    for hole in holes:
        moving_list = calculate_path(
            mball.pos, tball.pos, hole.pos, config.length, config.width)
        # Remember to transform coordinates of moving node to the form of root table
        transform_moving_list(moving_list, mirror_table.index_rr)
        path_ll.push_back(PathNode(moving_list=moving_list))
    return path_ll


def transform_moving_list(moving_list, index_rr):
    """Transform moving list by linear tranformation"""
    for index in range(len(moving_list)):
        moving_list[index].pos = algo.mirror_transformation(
            moving_list[index].pos, index_rr, inverse=True)


def calculate_path(mball_pos, tball_pos, hole_pos, length, width):
    """Calculate the path from mball to contact pos and tball to hole respectively"""
    moving_list = []
    contact_pos = algo.contact_pos(tball_pos, hole_pos)

    # line between mball_pos and contact_pos
    mball_contact_moving_list = calculate_moving_nodes(
        mball_pos, contact_pos, length, width, "m")
    # line between tball_pos and hole_pos
    tball_hole_moving_list = calculate_moving_nodes(
        tball_pos, hole_pos, length, width, "t")

    append_to_list(moving_list, mball_contact_moving_list)
    append_to_list(moving_list, tball_hole_moving_list)

    return moving_list


def calculate_moving_nodes(start, end, length, width, type):
    """Calculate moving nodes by the intersection in geometric way"""
    moving_list = []
    points_passing_by_border = [start]
    # Find out x, y passing by border
    xs_passing_by_border = algo.multiples_between_interval(
        start[0, 0], end[0, 0], length)
    ys_passing_by_border = algo.multiples_between_interval(
        start[1, 0], end[1, 0], width)

    for x in xs_passing_by_border:
        border_point = algo.point_between_two_points(x, start, end, False)
        points_passing_by_border.append(border_point)

    for y in ys_passing_by_border:
        border_point = algo.point_between_two_points(y, start, end, True)
        # Because it is probable that the y border point is identical to x border point
        # Hence, it must traverse points_passing_by_border to prevent repeated elements
        is_repeated = False
        for point in points_passing_by_border:
            if point[0, 0] == border_point[0, 0] and point[1, 0] == border_point[1, 0]:
                is_repeated = True
        if not is_repeated:
            points_passing_by_border.append(border_point)

    # Maybe the end point is identical to the last element of points_passing_by_border
    if end[0, 0] != points_passing_by_border[len(points_passing_by_border)-1][0, 0] and \
            end[1, 0] != points_passing_by_border[len(points_passing_by_border)-1][1, 0]:
        points_passing_by_border.append(end)

    reversed = (end-start)[0, 0] < 0
    points_passing_by_border.sort(key=lambda p: p[0, 0], reverse=reversed)

    for point in points_passing_by_border:
        moving_list.append(MovingNode(point, type))

    return moving_list


def append_to_list(target_list, src_list):
    for src in src_list:
        target_list.append(src)
