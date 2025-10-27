from ortools.sat.python import cp_model
import math

# Configurable parameters
MIN_ROOT = 30
MAX_ROOT = 80
GRID_SIZE = 3
TOP_N = 10  # Number of near-magic grids to log
DELTA_TOL = 100  # Only log grids with max delta <= this

# Generate all perfect squares in range
squares = [i**2 for i in range(MIN_ROOT, MAX_ROOT+1)]

model = cp_model.CpModel()
# 3x3 grid flattened
cells = [model.NewIntVarFromDomain(cp_model.Domain.FromValues(squares), f'cell_{i}') for i in range(GRID_SIZE**2)]
model.AddAllDifferent(cells)

# Compute all 8 lines (rows, cols, diags)
lines = [
    [cells[0], cells[1], cells[2]],
    [cells[3], cells[4], cells[5]],
    [cells[6], cells[7], cells[8]],
    [cells[0], cells[3], cells[6]],
    [cells[1], cells[4], cells[7]],
    [cells[2], cells[5], cells[8]],
    [cells[0], cells[4], cells[8]],
    [cells[2], cells[4], cells[6]],
]

# Variables for each line sum
line_sums = [model.NewIntVar(3*min(squares), 3*max(squares), f'line_sum_{i}') for i in range(8)]
for i, line in enumerate(lines):
    model.Add(line_sums[i] == sum(line))

# Compute max and min line sum
max_sum = model.NewIntVar(3*min(squares), 3*max(squares), 'max_sum')
min_sum = model.NewIntVar(3*min(squares), 3*max(squares), 'min_sum')
model.AddMaxEquality(max_sum, line_sums)
model.AddMinEquality(min_sum, line_sums)
# Delta is the difference between max and min line sum
delta = model.NewIntVar(0, 3*max(squares), 'delta')
model.Add(delta == max_sum - min_sum)
# Only log grids with delta <= DELTA_TOL
model.Add(delta <= DELTA_TOL)
# Minimize delta
model.Minimize(delta)

# Search and log top N near-magic grids
class NearMagicLogger(cp_model.CpSolverSolutionCallback):
    def __init__(self, cells, line_sums, delta, top_n=10):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.cells = cells
        self.line_sums = line_sums
        self.delta = delta
        self.top_n = top_n
        self.results = []
    def on_solution_callback(self):
        grid = [self.Value(c) for c in self.cells]
        lines = [self.Value(s) for s in self.line_sums]
        delta = self.Value(self.delta)
        self.results.append((delta, grid, lines))
        if len(self.results) >= self.top_n:
            self.StopSearch()

solver = cp_model.CpSolver()
logger = NearMagicLogger(cells, line_sums, delta, top_n=TOP_N)
status = solver.SolveWithSolutionCallback(model, logger)

with open('near_magic_ortools_results.txt', 'w') as f:
    if logger.results:
        logger.results.sort()
        for i, (delta, grid, lines) in enumerate(logger.results):
            f.write(f'Grid #{i+1}\n')
            for r in range(GRID_SIZE):
                f.write(' '.join(str(grid[r*GRID_SIZE+c]) for c in range(GRID_SIZE)) + '\n')
            f.write(f'Line sums: {lines}\n')
            f.write(f'Delta: {delta}\n\n')
        print(f"Logged {len(logger.results)} near-magic grids to near_magic_ortools_results.txt")
    else:
        f.write('No near-magic grids found.\n')
        print('No near-magic grids found.')
