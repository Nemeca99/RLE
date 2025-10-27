from ortools.sat.python import cp_model
import math

def is_perfect_square(n):
    root = int(math.isqrt(n))
    return root * root == n

def main():
    model = cp_model.CpModel()
    # All possible perfect squares in your range
    squares = [i**2 for i in range(30, 81)]
    # 9 variables for the grid
    cells = [model.NewIntVarFromDomain(cp_model.Domain.FromValues(squares), f'cell_{i}') for i in range(9)]
    # All values must be unique
    model.AddAllDifferent(cells)
    # Magic sum variable
    magic_sum = model.NewIntVar(3 * min(squares), 3 * max(squares), 'magic_sum')
    # Rows, columns, diagonals must sum to magic_sum
    model.Add(cells[0] + cells[1] + cells[2] == magic_sum)
    model.Add(cells[3] + cells[4] + cells[5] == magic_sum)
    model.Add(cells[6] + cells[7] + cells[8] == magic_sum)
    model.Add(cells[0] + cells[3] + cells[6] == magic_sum)
    model.Add(cells[1] + cells[4] + cells[7] == magic_sum)
    model.Add(cells[2] + cells[5] + cells[8] == magic_sum)
    model.Add(cells[0] + cells[4] + cells[8] == magic_sum)
    model.Add(cells[2] + cells[4] + cells[6] == magic_sum)
    # Optional: symmetry breaking (e.g., fix top-left cell to smallest square)
    model.Add(cells[0] == min(squares))
    # Search for a solution
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        grid = [solver.Value(cells[i]) for i in range(9)]
        print("Magic square of unique perfect squares:")
        for i in range(0, 9, 3):
            print(grid[i:i+3])
        print("Magic sum:", solver.Value(magic_sum))
    else:
        print("No solution found.")

if __name__ == '__main__':
    main()