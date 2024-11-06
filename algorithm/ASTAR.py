import sys
import time
import heapq
import psutil
import os
import json
from datetime import datetime
import numpy as np

class SokobanSolver:
    def __init__(self, weights, grid):
        self.weights = weights
        self.grid = grid
        self.walls = set()
        self.switches = set()
        self.stones = {}
        self.ares_pos = None
        self.grid_height = len(grid)
        self.grid_width = max(len(row) for row in grid)
        self.weight_index = 0

        self.initial_state = self.initialize_state()

    def initialize_state(self):
        for y, line in enumerate(self.grid):
            for x, ch in enumerate(line):
                if ch == '#':
                    self.walls.add((x, y))
                elif ch == '@':
                    self.ares_pos = (x, y)
                elif ch == '+':
                    self.ares_pos = (x, y)
                    self.switches.add((x, y))
                elif ch == '$':
                    self.stones[(x, y)] = self.weights[self.weight_index]
                    self.weight_index += 1
                elif ch == '*':
                    self.stones[(x, y)] = self.weights[self.weight_index]
                    self.switches.add((x, y))
                    self.weight_index += 1
                elif ch == '.':
                    self.switches.add((x, y))
                elif ch == ' ':
                    pass  # Empty space

        return {
            'ares_pos': self.ares_pos,
            'stones': self.stones,
            'actions': [],
            'total_weight': 0,
            'cost_so_far': 0
        }

    def print_json(self, obj, indent=4):
        def convert_to_serializable(o):
            if isinstance(o, dict):
                return {f"{k[0]},{k[1]}" if isinstance(k, tuple) else k: convert_to_serializable(v) for k, v in o.items()}
            elif isinstance(o, list):
                return [convert_to_serializable(i) for i in o]
            else:
                return o

        serializable = convert_to_serializable(obj)
        print(json.dumps(serializable, indent=indent))

    def write_output(self, filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution):
        with open(filename, 'w') as f:
            f.write(f"{algorithm_name}\n")
            f.write(f"Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.2f}\n")
            f.write(f"{solution}\n")

    def heuristic(self, state):
        # Use sum of Manhattan distances from stones to nearest switches * weight of stone
        stones = state['stones']
        total = 0
        for stone_pos in stones.keys():
            min_dist = min((abs(stone_pos[0] - s[0])**2 + abs(stone_pos[1] - s[1])) * stones[stone_pos] for s in self.switches)
            total += min_dist
        return total

    def is_goal_state(self, state):
        stones = state['stones']
        return all(pos in self.switches for pos in stones.keys())

    def get_memory_usage(self):
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
        return mem

    def a_star_search(self):
        start_time = time.time()
        nodes_generated = 0
        counter = 0  # Unique sequence count

        open_list = []
        h = self.heuristic(self.initial_state)
        f = self.initial_state['cost_so_far'] + h
        heapq.heappush(open_list, (f, counter, self.initial_state))
        closed_set = set()

        while open_list:
            _, _, current_state = heapq.heappop(open_list)
            current_state_key = (current_state['ares_pos'], frozenset(current_state['stones'].items()))
            if current_state_key in closed_set:
                continue
            closed_set.add(current_state_key)

            nodes_generated += 1

            if self.is_goal_state(current_state):
                end_time = time.time()
                time_taken = (end_time - start_time) * 1000  # in ms
                memory_used = self.get_memory_usage()
                steps = len(current_state['actions'])
                total_weight = current_state['total_weight']
                solution = ''.join(current_state['actions'])
                return steps, total_weight, nodes_generated, time_taken, memory_used, solution

            cost_so_far = current_state['cost_so_far']

            # Generate successors
            for move, action_char in [((0, -1), 'u'), ((0, 1), 'd'), ((-1, 0), 'l'), ((1, 0), 'r')]:
                new_ares_x = current_state['ares_pos'][0] + move[0]
                new_ares_y = current_state['ares_pos'][1] + move[1]
                if 0 <= new_ares_x < self.grid_width and 0 <= new_ares_y < self.grid_height:
                    if (new_ares_x, new_ares_y) not in self.walls:
                        if (new_ares_x, new_ares_y) in current_state['stones']:
                            # Try to push the stone
                            new_stone_x = new_ares_x + move[0]
                            new_stone_y = new_ares_y + move[1]
                            if 0 <= new_stone_x < self.grid_width and 0 <= new_stone_y < self.grid_height:
                                if (new_stone_x, new_stone_y) not in self.walls and (new_stone_x, new_stone_y) not in current_state['stones']:
                                    # Push is possible
                                    new_stones = current_state['stones'].copy()
                                    weight = new_stones.pop((new_ares_x, new_ares_y))
                                    new_stones[(new_stone_x, new_stone_y)] = weight
                                    action = action_char.upper()
                                    new_total_weight = current_state['total_weight'] + weight
                                    new_actions = current_state['actions'] + [action]
                                    new_cost_so_far = cost_so_far + weight
                                    new_state = {
                                        'ares_pos': (new_ares_x, new_ares_y),
                                        'stones': new_stones,
                                        'actions': new_actions,
                                        'total_weight': new_total_weight,
                                        'cost_so_far': new_cost_so_far
                                    }
                                    h = self.heuristic(new_state)
                                    f = new_cost_so_far + h
                                    counter += 1
                                    heapq.heappush(open_list, (f, counter, new_state))
                        else:
                            # Move without pushing
                            action = action_char.lower()
                            new_actions = current_state['actions'] + [action]
                            new_state = {
                                'ares_pos': (new_ares_x, new_ares_y),
                                'stones': current_state['stones'],
                                'actions': new_actions,
                                'total_weight': current_state['total_weight'],
                                'cost_so_far': cost_so_far + 1
                            }
                            h = self.heuristic(new_state)
                            f = new_state['cost_so_far'] + h
                            counter += 1
                            heapq.heappush(open_list, (f, counter, new_state))
        # If no solution is found
        return None

    def solve(self):
        self.print_json(self.initial_state)
        result = self.a_star_search()
        if result:
            steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
            return steps, total_weight, nodes_generated, time_taken, memory_used, solution
        else:
            return None

def read_input(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    weights_line = lines[0]
    grid_lines = lines[1:]
    weights = [int(w) for w in weights_line.strip().split()]
    grid = [line.rstrip('\n') for line in grid_lines]
    return weights, grid

if __name__ == "__main__":
    # input_filename = 'input.txt'
    # output_filename = 'ASTART_output.txt'
    # if len(sys.argv) >= 2:
    #     input_filename = sys.argv[1]
    # if len(sys.argv) >= 3:
    #     output_filename = sys.argv[2]

    # weights, grid = read_input(input_filename)
    # solver = SokobanSolver(weights, grid)
    # result = solver.solve()
    # if result:
    #     steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
    #     algorithm_name = "A*"
    #     solver.write_output(output_filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution)
    # else:
    #     with open(output_filename, 'w') as f:
    #         f.write("No solution found.\n")

    input_dir = 'maze'
    # output_dir = f'algorithm/logs/output_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    output_dir = 'output/a_star'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    start_time = time.time()
    for input_filename in os.listdir(input_dir):
        print(f"Solving {input_filename}...")
        input_filename = os.path.join(input_dir, input_filename)
        output_filename = os.path.join(output_dir, f"output-{input_filename.strip('.txt')[-2:]}.txt")
        weights, grid = read_input(input_filename)
        solver = SokobanSolver(weights, grid)
        result = solver.solve()
        if result:
            steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
            algorithm_name = "A*"
            solver.write_output(output_filename, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution)
        else:
            with open(output_filename, 'w') as f:
                f.write("No solution found.\n")
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f}s")

    print("Done!")
