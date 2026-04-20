#! /usr/bin/env python

import math

import pooltool as pt

_interface = None


def distance(Ax, Ay, Bx, By):
    return math.sqrt((Ax - Bx) ** 2 + (Ay - By) ** 2)


def calculate_vector(point1, point2):
    """Vector from point1 to point2."""
    return [point2[0] - point1[0], point2[1] - point1[1]]


def dot_product(vector1, vector2):
    return vector1[0] * vector2[0] + vector1[1] * vector2[1]


def magnitude(vector):
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


def angle_between_vectors(x1, y1, x2, y2, x3, y3, x4, y4, in_degrees=True):
    """Angle between vector (p1→p2) and vector (p3→p4).

    Sign: negative when the dot product is negative.
    """
    vector1 = calculate_vector([x1, y1], [x2, y2])
    vector2 = calculate_vector([x3, y3], [x4, y4])
    dot = dot_product(vector1, vector2)
    magnitude_product = magnitude(vector1) * magnitude(vector2)
    angle_rad = math.acos(dot / magnitude_product)
    angle_deg = math.degrees(angle_rad)
    if in_degrees:
        angle_deg *= -1 if dot < 0 else 1
        return -angle_deg
    else:
        angle_rad *= -1 if dot < 0 else 1
        return angle_rad


def _build_target_balls(target_positions, ballset):
    """Map n target positions onto balls [9-n+1 … 9].

    n=9 is a special case: balls 4 and 8 are intentionally skipped,
    matching the original paper's 9-ball setup.
    """
    n = len(target_positions)
    balls = {}
    if n == 9:
        lowest_ball = 1
        skip_ids = {"4", "8"}
    else:
        lowest_ball = 9 - n + 1
        skip_ids = set()

    for i, (x, y) in enumerate(target_positions):
        ball_id = str(lowest_ball + i)
        if ball_id in skip_ids:
            continue
        balls[ball_id] = pt.Ball.create(ball_id, xy=[x, y], ballset=ballset)
    return balls


def simulate(Cuex, Cuey, Target, cutangle, D, E, speed, visualize=False):
    global _interface

    ballset = pt.get_ball_set("pooltool_pocket")
    n = len(Target)

    balls = {"cue": pt.Ball.create("cue", xy=[Cuex, Cuey], ballset=ballset)}
    balls.update(_build_target_balls(Target, ballset))

    shot = pt.System(
        table=pt.Table.default(pt.TableType.POCKET),
        cue=pt.Cue.default(),
        balls=balls,
    )

    shot.strike(
        cue_ball_id="cue",
        V0=speed,
        b=D * math.sin(math.radians(E)),
        a=D * math.cos(math.radians(E)),
        theta=0,
    )

    # Aim at the lowest-numbered target ball. The +3 cut offset for n=8
    # is preserved from the original code — all other n use -3.
    aim_target_id = "1" if n == 9 else str(9 - n + 1)
    cut_offset = 3 if n == 8 else -3
    shot.strike(phi=pt.aim.at_ball(shot, aim_target_id, cut=-cutangle + cut_offset))

    pt.simulate(shot, continuous=True, inplace=True)
    if visualize:
        if _interface is None:
            _interface = pt.ShotViewer()
        _interface.show(shot)

    for i in range(len(shot.events) - 1, -1, -1):
        ev = shot.events[i]
        # Original precedence: (cue AND rolling_stationary) OR spinning_stationary OR ball_pocket
        if (
            (ev.agents[0].id == 'cue' and ev.event_type == 'rolling_stationary')
            or ev.event_type == 'spinning_stationary'
            or ev.event_type == 'ball_pocket'
        ):
            important_time = ev.time
            cue_ball_history = shot.balls['cue'].history_cts.states
            closest_state = min(cue_ball_history, key=lambda state: abs(state.t - important_time))
            x, y = closest_state.rvw[0][:2]
            return x, y, cutangle, D, E, speed
