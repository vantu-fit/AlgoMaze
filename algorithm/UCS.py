import heapq
import sys
import time
import psutil
import os


class UniformCostSearch:
    def __init__(self, input_filename='input.txt', output_filename='UCS_output.txt'):
        """
        Initialize the Sokoban solver with input and output file paths.

        Args:
            input_filename (str): Path to the input file containing problem configuration
            output_filename (str): Path to save the solution output
        """
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.stone_weights = None
        self.game_grid = None

    def is_goal_state(self, game_state):
        """
        Check if all stones have been placed on their goal positions.

        Args:
            game_state (list): 2D grid representing the current game state

        Returns:
            bool: True if all stones are on goal positions, False otherwise
        """
        for row in game_state:
            if '$' in row:
                return False
        return True

    def generate_successors(self, current_grid, grid_costs, total_steps):
        """
        Generate all possible successor states from the current game state.

        Args:
            current_grid (list): Current game grid
            grid_costs (list): Cost associated with each stone
            total_steps (int): Number of steps taken so far

        Returns:
            list: Possible successor states with their respective details
        """
        successors = []
        rows, cols = len(current_grid), len(current_grid[0])
        player_position = None

        # Find player's position
        for r in range(rows):
            for c in range(cols):
                if current_grid[r][c] == '@' or current_grid[r][c] == '+':
                    player_position = (r, c)
                    break
            if player_position:
                break

        move_directions = [(-1, 0, 'u', 'U'), (1, 0, 'd', 'D'),
                           (0, -1, 'l', 'L'), (0, 1, 'r', 'R')]

        for dx, dy, move_action, push_action in move_directions:
            next_x, next_y = player_position[0] + dx, player_position[1] + dy

            if 0 < next_x < rows - 1 and 0 < next_y < cols - 1:
                # Movement without pushing
                if current_grid[next_x][next_y] == ' ':
                    new_grid = [list(row) for row in current_grid]
                    new_grid[player_position[0]][player_position[1]
                                                 ] = ' ' if current_grid[player_position[0]][player_position[1]] == '@' else '.'
                    new_grid[next_x][next_y] = '@'
                    successors.append(
                        (new_grid, grid_costs, 0, total_steps + 1, move_action))

                # Push stone scenarios
                elif current_grid[next_x][next_y] == '$':
                    if current_grid[next_x + dx][next_y + dy] != ' ' and current_grid[next_x + dx][next_y + dy] != '.':
                        continue

                    stone_x, stone_y = next_x, next_y
                    new_stone_x = stone_x + dx
                    new_stone_y = stone_y + dy

                    # Push to empty space
                    if current_grid[new_stone_x][new_stone_y] == ' ':
                        new_grid = [list(row) for row in current_grid]
                        new_grid_costs = [row[:] for row in grid_costs]

                        new_grid[player_position[0]][player_position[1]
                                                     ] = ' ' if current_grid[player_position[0]][player_position[1]] == '@' else '.'
                        new_grid[next_x][next_y] = '@'
                        new_grid[new_stone_x][new_stone_y] = '$'

                        new_grid_costs[new_stone_x][new_stone_y] = new_grid_costs[stone_x][stone_y]
                        new_grid_costs[stone_x][stone_y] = 0

                        successors.append(
                            (new_grid, new_grid_costs, new_grid_costs[new_stone_x][new_stone_y], total_steps + 1, push_action))

                    # Push to goal
                    if current_grid[new_stone_x][new_stone_y] == '.':
                        new_grid = [list(row) for row in current_grid]
                        new_grid_costs = [row[:] for row in grid_costs]

                        new_grid[player_position[0]][player_position[1]
                                                     ] = ' ' if current_grid[player_position[0]][player_position[1]] == '@' else '.'
                        new_grid[next_x][next_y] = '@'
                        new_grid[new_stone_x][new_stone_y] = '*'

                        new_grid_costs[new_stone_x][new_stone_y] = grid_costs[stone_x][stone_y]
                        new_grid_costs[stone_x][stone_y] = 0

                        successors.append(
                            (new_grid, new_grid_costs, grid_costs[stone_x][stone_y], total_steps + 1, push_action))

                # Move to goal space
                elif current_grid[next_x][next_y] == '.':
                    new_grid = [list(row) for row in current_grid]
                    new_grid[player_position[0]][player_position[1]] = ' '
                    new_grid[next_x][next_y] = '+'
                    successors.append(
                        (new_grid, grid_costs, 0, total_steps + 1, move_action))

                # Push stone from goal space
                elif current_grid[next_x][next_y] == '*':
                    if current_grid[next_x + dx][next_y + dy] != ' ' and current_grid[next_x + dx][next_y + dy] != '.':
                        continue

                    stone_x, stone_y = next_x, next_y
                    new_stone_x = stone_x + dx
                    new_stone_y = stone_y + dy

                    # Push to empty space
                    if current_grid[new_stone_x][new_stone_y] == ' ':
                        new_grid = [list(row) for row in current_grid]
                        new_grid_costs = [row[:] for row in grid_costs]

                        new_grid[player_position[0]][player_position[1]
                                                     ] = ' ' if current_grid[player_position[0]][player_position[1]] == '@' else '.'
                        new_grid[next_x][next_y] = '+'
                        new_grid[new_stone_x][new_stone_y] = '$'

                        new_grid_costs[new_stone_x][new_stone_y] = new_grid_costs[stone_x][stone_y]
                        new_grid_costs[stone_x][stone_y] = 0

                        successors.append(
                            (new_grid, new_grid_costs, new_grid_costs[new_stone_x][new_stone_y], total_steps + 1, push_action))

                    # Push to goal
                    if current_grid[new_stone_x][new_stone_y] == '.':
                        new_grid = [list(row) for row in current_grid]
                        new_grid_costs = [row[:] for row in grid_costs]

                        new_grid[player_position[0]][player_position[1]
                                                     ] = ' ' if current_grid[player_position[0]][player_position[1]] == '@' else '.'
                        new_grid[next_x][next_y] = '+'
                        new_grid[new_stone_x][new_stone_y] = '*'

                        new_grid_costs[new_stone_x][new_stone_y] = grid_costs[stone_x][stone_y]
                        new_grid_costs[stone_x][stone_y] = 0

                        successors.append(
                            (new_grid, new_grid_costs, grid_costs[stone_x][stone_y], total_steps + 1, push_action))

        return successors

    def calculate_stone_grid_costs(self, game_grid, stone_weights):
        """
        Calculate cost for each stone in the game grid.

        Args:
            game_grid (list): Current game grid
            stone_weights (list): List of weights for each stone

        Returns:
            list: 2D grid of stone costs
        """
        rows, cols = len(game_grid), len(game_grid[0])
        grid_costs = [[0] * cols for _ in range(rows)]

        weight_index = 0

        for r in range(rows):
            for c in range(cols):
                if game_grid[r][c] == '$' or game_grid[r][c] == '*':
                    grid_costs[r][c] = stone_weights[weight_index]
                    weight_index += 1

        return grid_costs

    def get_process_memory_usage(self):
        """
        Get current process memory usage.

        Returns:
            float: Memory usage in megabytes
        """
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
        return mem

    def uniform_cost_search(self, game_grid, stone_weights):
        """
        Perform Uniform Cost Search to solve the Sokoban puzzle.

        Args:
            game_grid (list): Initial game grid
            stone_weights (list): List of stone weights

        Returns:
            tuple: Solution details (steps, total_cost, nodes_generated, time_taken, memory_used, solution_path)
        """
        start_node = game_grid
        start_node_hash = ''.join(''.join(row) for row in game_grid)
        grid_costs = self.calculate_stone_grid_costs(game_grid, stone_weights)
        frontier = [(0, 0, start_node, grid_costs, '')]
        explored = {start_node_hash: (0, None, 0)}

        start_time = time.time()
        nodes_generated = 0

        while frontier:
            current_cost, steps, node, current_grid_cost, path = heapq.heappop(
                frontier)

            nodes_generated += 1
            if self.is_goal_state(node):
                end_time = time.time()
                time_taken = (end_time - start_time) * 1000  # in ms
                memory_used = self.get_process_memory_usage()
                return steps, current_cost, nodes_generated, time_taken, memory_used, path

            successors = self.generate_successors(
                node, current_grid_cost, steps)
            for successor, successor_grid_cost, move_cost, successor_steps, action in successors:
                successor_hash = ''.join(''.join(row) for row in successor)
                total_cost = current_cost + move_cost
                new_path = path + action

                if successor_hash not in explored or (total_cost, successor_steps) < (explored[successor_hash][0], explored[successor_hash][2]):
                    explored[successor_hash] = (
                        total_cost, node, successor_steps)
                    heapq.heappush(
                        frontier, (total_cost, successor_steps, successor, successor_grid_cost, new_path))

        return None

    def read_input_configuration(self, filename=None):
        """
        Read input file to extract stone weights and game grid.

        Args:
            filename (str, optional): Input file path. Defaults to self.input_filename.

        Returns:
            tuple: Stone weights and game grid configuration
        """
        filename = filename or self.input_filename
        with open(filename, 'r') as f:
            lines = f.readlines()
        weights_line = lines[0]
        grid_lines = lines[1:]
        self.stone_weights = [int(w) for w in weights_line.strip().split()]
        self.game_grid = [line.rstrip('\n') for line in grid_lines]
        for i in range(len(self.game_grid)):
            for j in range(len(self.game_grid[i])):
                if self.game_grid[i][j] == '#':
                    break
                if self.game_grid[i][j] == ' ':
                    self.game_grid[i] = self.game_grid[i][:j] + \
                        '#' + self.game_grid[i][j+1:]

        for i in range(len(self.game_grid)):
            for j in range(len(self.game_grid[i])-1, -1, -1):
                if self.game_grid[i][j] == '#':
                    break
                if self.game_grid[i][j] == ' ':
                    self.game_grid[i] = self.game_grid[i][:j] + \
                        '#' + self.game_grid[i][j+1:]
        # fill ' ' at the end to max length
        max_length = max([len(row) for row in self.game_grid])
        for i in range(len(self.game_grid)):
            self.game_grid[i] = self.game_grid[i] + '#' * \
                (max_length - len(self.game_grid[i]))
        print(self.game_grid)
        return self.stone_weights, self.game_grid

    def write_solution_output(self, algorithm_name, steps, total_weight, nodes_generated, time_taken, memory_used, solution, filename=None):
        """
        Write solution details to output file.

        Args:
            algorithm_name (str): Name of the solving algorithm
            steps (int): Number of steps in the solution
            total_weight (int): Total weight of moves
            nodes_generated (int): Number of nodes explored
            time_taken (float): Time taken to solve
            memory_used (float): Memory used during solving
            solution (str): Solution path
            filename (str, optional): Output file path. Defaults to self.output_filename.
        """
        filename = filename or self.output_filename
        with open(filename, 'w') as f:
            f.write(f"{algorithm_name}\n")
            f.write(
                f"Steps: {steps}, Weight: {total_weight}, Node: {nodes_generated}, Time (ms): {time_taken:.2f}, Memory (MB): {memory_used:.2f}\n")
            f.write(f"{solution}\n")

    def solve(self):
        """
        Main solving method that coordinates input reading, solving, and output writing.
        """
        # Read input
        stone_weights, game_grid = self.read_input_configuration()

        # Run UCS algorithm
        result = self.uniform_cost_search(game_grid, stone_weights)

        # Write output
        if result:
            steps, total_weight, nodes_generated, time_taken, memory_used, solution = result
            self.write_solution_output("UCS", steps, total_weight,
                                       nodes_generated, time_taken, memory_used, solution)
        else:
            with open(self.output_filename, 'w') as f:
                f.write("No solution found.\n")


def main():
<<<<<<< HEAD
    input_filename = 'maze\\input-01.txt'
    output_filename = 'ucs\\output-01.txt'
    solver = UniformCostSearch(input_filename, output_filename)
    solver.solve()
    # if len(sys.argv) >= 2:
    #     input_filename = sys.argv[1]
    # if len(sys.argv) >= 3:
    #     output_filename = sys.argv[2]
    # for i in range(1, 10):
    #     input_filename = f'map\\input-0{i}.txt'
    #     output_filename = f'ucs\\output-0{i}.txt'
    #     solver = UniformCostSearch(input_filename, output_filename)
    #     solver.solve()


=======
    # input_filename = 'maze\\input-06.txt'
    # output_filename = 'ucs\\output-06.txt'
    # solver = UniformCostSearch(input_filename, output_filename)
    # solver.solve()
    if len(sys.argv) >= 2:
        input_filename = sys.argv[1]
    if len(sys.argv) >= 3:
        output_filename = sys.argv[2]
    # for i in range(1, 10):
    #     input_filename = f'maze\\input-0{i}.txt'
    #     output_filename = f'new_ucs\\output-0{i}.txt'
    #     solver = UniformCostSearch(input_filename, output_filename)
    #     solver.solve()
    input_filename = 'maze\\input-10.txt'
    output_filename = 'new_ucs\\output-10.txt'
    solver = UniformCostSearch(input_filename, output_filename)
    solver.solve()
>>>>>>> 23c07bfd40bd2ff8f46cff556dc12d33ee5a3052
if __name__ == "__main__":
    main()
