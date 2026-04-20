import argparse
import csv
import time
from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

import config
import path
import test_control as tc
from sprite import Ball, Hole
from table import Table
from tree import Tree

radius = config.radius
length = config.length
width = config.width
holes = [Hole(np.matrix([[radius], [radius]])), Hole(np.matrix([[radius], [width/2]])), Hole(np.matrix([[radius], [width - radius]])),
         Hole(np.matrix([[length - radius], [radius]])), Hole(np.matrix([[length-radius], [width/2]])), Hole(np.matrix([[length - radius], [width - radius]]))]
origin = np.matrix([[0], [0]])

def pool(mball, tballs, cushion_amt, path_amt, visualize=False):
    table = Table(np.matrix([[cushion_amt], [cushion_amt]]),
                  origin, mball, tballs, holes)
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

    # Collect (evaluation, node) pairs into a list — using a dict keyed by
    # evaluation would silently drop paths that happen to tie on the score.
    path_node = avail_paths.first
    scored_paths = []
    while path_node is not None:
        moving_list = path_node.moving_list
        evaluation = path.calculate_evaluation(moving_list)
        scored_paths.append((evaluation, path_node))
        path_node = path_node.next

    sorted_paths = sorted(scored_paths, key=lambda item: item[0])

    if len(sorted_paths) > path_amt:
        for i in range(len(sorted_paths)-path_amt, len(sorted_paths)):
            path_no = sorted_paths[i][1].no
            evaluation = sorted_paths[i][0]
            print(path_no, "evaluation", evaluation, '\n')
            moving_list = sorted_paths[i][1].moving_list

    tball_simple_pos = [
        [tb.pos[0].item()/100, tb.pos[1].item()/100] for tb in tballs
    ]
    p1x, p1y = moving_list[0].pos[0].item(), moving_list[0].pos[1].item()
    p2x, p2y = moving_list[1].pos[0].item(), moving_list[1].pos[1].item()
    p3x, p3y = moving_list[2].pos[0].item(), moving_list[2].pos[1].item()
    p4x, p4y = moving_list[3].pos[0].item(), moving_list[3].pos[1].item()
    angle = tc.angle_between_vectors(p1x, p1y, p2x, p2y, p3x, p3y, p4x, p4y)
    print(f'\nContact point = ({p2x}, {p2y})')

    print('angle:', angle, '\n')
    cue_final_positions = []

    def record_shot(cutangle, spin_mag, spin_ang, speed):
        res = tc.simulate(p1x/100, p1y/100, tball_simple_pos, cutangle, spin_mag, spin_ang, speed, visualize=visualize)
        res_x, res_y, res_angle, res_spin_mag, res_spin_ang, res_speed = res
        cue_final_positions.append([
            round(res_x, 4), round(res_y, 4), round(res_angle, 2),
            round(res_spin_mag, 2), res_spin_ang, res_speed,
        ])
        print('simulate', len(cue_final_positions), 'times\r', end=' ')

    # Baseline shots (no spin). First uses a fixed cut angle; next two use the computed angle.
    record_shot(-13.21, 0, 0, 1)
    record_shot(angle, 0, 0, 2.5)
    record_shot(angle, 0, 0, 2)

    # Spin sweep grid — preserves the speeds/mags/angs from the original triple-nested while loop.
    speeds = [1.0, 1.5, 2.0, 2.5]
    spin_mags = [round(0.05 * i, 2) for i in range(1, 13)]  # 0.05 .. 0.60
    spin_angs = list(range(0, 316, 45))                     # 0, 45, .., 315

    for speed, spin_mag, spin_ang in product(speeds, spin_mags, spin_angs):
        record_shot(angle, spin_mag, spin_ang, speed)

    return cue_final_positions


def load_scenario(path):
    """Load a ball layout from a YAML file.

    Expected keys: `name`, `cue: [x, y]`, `targets: [[x, y], ...]` (cm).
    Returns the full dict; callers pick the fields they need.
    """
    with open(path) as f:
        return yaml.safe_load(f)


def parse_args():
    p = argparse.ArgumentParser(description="Pool-path simulator and experiment runner.")
    p.add_argument("--scenario", type=Path, default=Path("scenarios") / "9ball.yaml",
                   help="Path to a scenario YAML file (default: scenarios/9ball.yaml).")
    p.add_argument("--visualize", action="store_true",
                   help="Open the 3D ShotViewer for every shot (blocks per shot).")
    p.add_argument("--output-dir", type=Path, default=Path("."),
                   help="Directory to write output artifacts (default: current directory).")
    return p.parse_args()


def main():
    args = parse_args()
    start_time = time.time()

    scenario = load_scenario(args.scenario)
    name = scenario.get("name", args.scenario.stem)
    cue_pos = scenario["cue"]
    target_positions = scenario["targets"]

    mball = Ball(np.matrix([[cue_pos[0]], [cue_pos[1]]]))
    tballs = [Ball(np.matrix([[x], [y]])) for x, y in target_positions]

    cue_final_positions = pool(mball, tballs, 4, 1, visualize=args.visualize)

    # extract x and y coordinates of the candidate cue final positions
    x = [point[0] for point in cue_final_positions]
    y = [point[1] for point in cue_final_positions]

    heatmap = np.load(Path("allheatmap") / "eval_interpolated" / "reshape_60_100.npy")
    scored_positions = []
    for i, pos in enumerate(cue_final_positions):
        # clamp into the heatmap grid
        if pos[0] * 100 <= 0:
            pos[0] = 0
        if pos[0] * 100 > 98:
            pos[0] = 0.98
        if pos[1] <= 0:
            pos[1] = 0
        if pos[1] * 100 > 197:
            pos[1] = 1.97
        score = heatmap[int(pos[0] * 100)][int(pos[1] * 100)]
        scored_positions.append([i, score])

    # print the top-10 highest-scoring positions
    scored_positions_sorted = sorted(scored_positions, key=lambda entry: entry[1])
    for rank in range(11, len(scored_positions_sorted) + 1):
        entry = scored_positions_sorted[len(scored_positions_sorted) - rank]
        print('\n', entry)
        print('info = ', cue_final_positions[entry[0]])
    print('\n\n')

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # dump per-shot results to CSV: one row per simulated shot, including heatmap score.
    csv_path = args.output_dir / f"results_{name}.csv"
    score_by_index = {i: s for i, s in scored_positions}
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["shot", "x", "y", "cut_angle", "spin_mag", "spin_ang", "speed", "score"])
        for i, pos in enumerate(cue_final_positions):
            writer.writerow([i, *pos, score_by_index[i]])

    # scatter plot of candidate cue final positions overlaid on the table
    scatter_path = args.output_dir / f"scatter_{name}.png"

    plt.cla()
    plt.clf()
    ax = plt.axes()
    img = plt.imread('table.png')
    ax.imshow(img, extent=[-0.11, 1.11, -0.11, 2.11])
    plt.scatter(x, y, s=30, color='r')
    plt.xlim(-0.12, 1.12)
    plt.ylim(-0.12, 2.12)
    plt.xticks(ticks=[0, 1.0], labels=[0, 100])
    plt.yticks(ticks=[0, 2.0], labels=[0, 200])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.title(f'Cue Ball Final Position — {name}')
    plt.savefig(scatter_path, dpi=600)

    end_time = time.time()
    print(f'\nResults saved to {csv_path}')
    print(f'Scatter saved to {scatter_path}')
    print('Cost : ', end_time - start_time)


if __name__ == "__main__":
    main()
