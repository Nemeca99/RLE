import sqlite3
import grid_base36_utils
import csv
import os
import numpy as np

DB = 'near_magic_candidates_streamable.sqlite'
CSV_OUT = 'good_candidates.csv'
GOOD_TABLE = 'good_grids'

# Strict filter: delta <= 50, is_unique = 1
QUERY = '''
SELECT grid_id, delta, is_unique, is_magic_sum, metadata FROM grids
WHERE (delta IS NOT NULL AND delta <= 50)
  AND (is_unique IS NOT NULL AND is_unique = 1)
ORDER BY delta ASC
'''

# --- Additional filters and exports ---
WIDE_CSV_OUT = 'good_candidates_wide.csv'
WIDE_TABLE = 'good_grids_wide'
WIDE_QUERY = '''
SELECT grid_id, delta, is_unique, is_magic_sum, metadata FROM grids
WHERE (delta IS NOT NULL AND delta <= 150)
  AND (is_unique IS NOT NULL AND is_unique = 1)
ORDER BY delta ASC
'''

NU_CSV_OUT = 'good_candidates_nu.csv'
NU_TABLE = 'good_grids_nu'
NU_QUERY = '''
SELECT grid_id, delta, is_unique, is_magic_sum, metadata FROM grids
WHERE (delta IS NOT NULL AND delta <= 150)
  AND (is_unique IS NOT NULL AND is_unique = 0)
ORDER BY delta ASC
'''

WIDE250_CSV_OUT = 'good_candidates_wide250.csv'
WIDE250_TABLE = 'good_grids_wide250'
WIDE250_QUERY = '''
SELECT grid_id, delta, is_unique, is_magic_sum, metadata FROM grids
WHERE (delta IS NOT NULL AND delta <= 250)
  AND (is_unique IS NOT NULL AND is_unique = 1)
ORDER BY delta ASC
'''

ULTRA_CSV_OUT = 'good_candidates_ultra.csv'
ULTRA_TABLE = 'good_grids_ultra'
ULTRA_QUERY = '''
SELECT grid_id, delta, is_unique, is_magic_sum, metadata FROM grids
WHERE (delta IS NOT NULL AND delta <= 500)
ORDER BY delta ASC
'''

def triad_averaging_check(grid):
    # Check if the average of three corners is close to the center
    center = grid[1,1]
    triads = [
        (grid[0,0], grid[0,2], grid[2,0]),
        (grid[0,0], grid[2,2], grid[2,0]),
        (grid[0,2], grid[2,2], grid[2,0]),
        (grid[0,0], grid[0,2], grid[2,2]),
    ]
    for t in triads:
        avg = sum(t) / 3
        if abs(avg - center) < 10:  # tolerance can be tuned
            return True
    return False

def line_delta_spread(grid):
    # Compute all 8 line sums (3 rows, 3 cols, 2 diags)
    lines = [
        grid[0], grid[1], grid[2],
        grid[:,0], grid[:,1], grid[:,2],
        np.array([grid[i,i] for i in range(3)]),
        np.array([grid[i,2-i] for i in range(3)])
    ]
    sums = [int(np.sum(line)) for line in lines]
    return max(sums) - min(sums), float(np.std(sums))

def attempt_single_cell_repair(grid):
    # Try mutating each cell by ±1 and re-score line delta spread
    best_grid = grid.copy()
    best_spread, _ = line_delta_spread(grid)
    for i in range(3):
        for j in range(3):
            for delta in [-1, 1]:
                new_grid = grid.copy()
                new_grid[i,j] += delta
                spread, _ = line_delta_spread(new_grid)
                if spread < best_spread:
                    best_spread = spread
                    best_grid = new_grid.copy()
    return best_grid, best_spread

def attempt_multi_cell_repair(grid):
    # Try all ±1 pairs of edge-linked cells and nearest perfect square replacements
    best_grid = grid.copy()
    best_spread, _ = line_delta_spread(grid)
    # List of all edge-linked pairs (row/col/diag neighbors)
    pairs = [
        ((0,0),(0,1)), ((0,0),(1,0)), ((0,1),(0,2)), ((0,1),(1,1)),
        ((0,2),(1,2)), ((1,0),(1,1)), ((1,0),(2,0)), ((1,1),(1,2)),
        ((1,1),(2,1)), ((1,2),(2,2)), ((2,0),(2,1)), ((2,1),(2,2)),
        ((0,0),(1,1)), ((0,2),(1,1)), ((2,0),(1,1)), ((2,2),(1,1)),
        ((0,0),(2,2)), ((0,2),(2,0))
    ]
    for (i1,j1),(i2,j2) in pairs:
        for d1 in [-1,1]:
            for d2 in [-1,1]:
                new_grid = grid.copy()
                new_grid[i1,j1] += d1
                new_grid[i2,j2] += d2
                spread, _ = line_delta_spread(new_grid)
                if spread < best_spread:
                    best_spread = spread
                    best_grid = new_grid.copy()
    # Try nearest perfect square replacements for each cell
    squares = [i**2 for i in range(30, 81)]
    for i in range(3):
        for j in range(3):
            orig = grid[i,j]
            candidates = [s for s in squares if s != orig]
            if candidates:
                def dist(s, orig=orig):
                    return abs(s - orig)
                nearest = min(candidates, key=dist)
                new_grid = grid.copy()
                new_grid[i,j] = nearest
                spread, _ = line_delta_spread(new_grid)
                if spread < best_spread:
                    best_spread = spread
                    best_grid = new_grid.copy()
    return best_grid, best_spread

def attempt_edge_swap_repair(grid):
    # Try swapping all pairs of edge (non-center) cells
    best_grid = grid.copy()
    best_spread, _ = line_delta_spread(grid)
    best_path = ''
    edges = [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]
    for i1 in range(len(edges)):
        for i2 in range(i1+1, len(edges)):
            (r1,c1),(r2,c2) = edges[i1], edges[i2]
            new_grid = grid.copy()
            new_grid[r1,c1], new_grid[r2,c2] = new_grid[r2,c2], new_grid[r1,c1]
            spread, _ = line_delta_spread(new_grid)
            if spread < best_spread:
                best_spread = spread
                best_grid = new_grid.copy()
                best_path = f'edge-swap:({r1},{c1})<->({r2},{c2})'
    return best_grid, best_spread, best_path

def attempt_perfect_square_nudge(grid):
    # Replace each cell with its nearest perfect square
    best_grid = grid.copy()
    best_spread, _ = line_delta_spread(grid)
    best_path = ''
    squares = [i**2 for i in range(30, 81)]
    for i in range(3):
        for j in range(3):
            orig = grid[i,j]
            candidates = [s for s in squares if s != orig]
            if candidates:
                def dist(s, orig=orig):
                    return abs(s - orig)
                nearest = min(candidates, key=dist)
                new_grid = grid.copy()
                new_grid[i,j] = nearest
                spread, _ = line_delta_spread(new_grid)
                if spread < best_spread:
                    best_spread = spread
                    best_grid = new_grid.copy()
                    best_path = f'perfect-square-nudge:({i},{j})={nearest}'
    return best_grid, best_spread, best_path

def attempt_triad_harmony_repair(grid):
    # Try nudging cells in triads to bring their average closer to center
    best_grid = grid.copy()
    best_spread, _ = line_delta_spread(grid)
    best_path = ''
    center = grid[1,1]
    triads = [
        [(0,0),(0,2),(2,0)],
        [(0,0),(2,2),(2,0)],
        [(0,2),(2,2),(2,0)],
        [(0,0),(0,2),(2,2)],
    ]
    for triad in triads:
        for idx in range(3):
            i,j = triad[idx]
            for delta in [-1,1]:
                new_grid = grid.copy()
                new_grid[i,j] += delta
                avg = np.mean([new_grid[x,y] for x,y in triad])
                if abs(avg - center) < abs(np.mean([grid[x,y] for x,y in triad]) - center):
                    spread, _ = line_delta_spread(new_grid)
                    if spread < best_spread:
                        best_spread = spread
                        best_grid = new_grid.copy()
                        best_path = f'triad-harmony:({i},{j})+={delta}'
    return best_grid, best_spread, best_path

def attempt_entropy_repair(grid):
    # Nudge the cell in the line with the highest delta
    best_grid = grid.copy()
    best_spread, _ = line_delta_spread(grid)
    best_path = ''
    lines = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
    ]
    sums = [sum(grid[i,j] for i,j in line) for line in lines]
    target = np.argmax(np.abs(np.array(sums) - np.mean(sums)))
    for i,j in lines[target]:
        for delta in [-1,1]:
            new_grid = grid.copy()
            new_grid[i,j] += delta
            spread, _ = line_delta_spread(new_grid)
            if spread < best_spread:
                best_spread = spread
                best_grid = new_grid.copy()
                best_path = f'entropy:({i},{j})+={delta}'
    return best_grid, best_spread, best_path

def compute_triad_stddev(grid):
    # Compute stddev of all triad averages
    triads = [
        (grid[0,0], grid[0,2], grid[2,0]),
        (grid[0,0], grid[2,2], grid[2,0]),
        (grid[0,2], grid[2,2], grid[2,0]),
        (grid[0,0], grid[0,2], grid[2,2]),
        (grid[0,0], grid[1,1], grid[2,2]),
        (grid[0,2], grid[1,1], grid[2,0]),
    ]
    avgs = [np.mean(t) for t in triads]
    return float(np.std(avgs))

def compute_corner_weight(grid):
    # Average of corners
    return float((grid[0,0] + grid[0,2] + grid[2,0] + grid[2,2]) / 4)

def compute_mean_root_deviation(grid):
    # Mean deviation from perfect root symmetry (difference from nearest integer root)
    roots = np.sqrt(grid)
    nearest = np.round(roots)
    return float(np.mean(np.abs(roots - nearest)))

def compute_line_balance_score(grid):
    # Normalized line spread (lower is better)
    lines = [
        grid[0], grid[1], grid[2],
        grid[:,0], grid[:,1], grid[:,2],
        np.array([grid[i,i] for i in range(3)]),
        np.array([grid[i,2-i] for i in range(3)])
    ]
    sums = [int(np.sum(line)) for line in lines]
    mean = np.mean(sums)
    std = np.std(sums)
    return float(1.0 - (std / (mean if mean != 0 else 1)))

def compute_grid_signature(grid):
    # Canonical string: sorted values and row/col/diag sums
    vals = ','.join(map(str, sorted(grid.flatten())))
    lines = [
        grid[0], grid[1], grid[2],
        grid[:,0], grid[:,1], grid[:,2],
        np.array([grid[i,i] for i in range(3)]),
        np.array([grid[i,2-i] for i in range(3)])
    ]
    sums = ','.join(map(str, [int(np.sum(line)) for line in lines]))
    return f"{vals}|{sums}"

def export_candidates(query, csv_out, table_name):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
        grid_id TEXT PRIMARY KEY,
        grid_base36 TEXT,
        delta REAL,
        is_unique INTEGER,
        magic_sum INTEGER,
        triad_avg INTEGER,
        triad_stddev REAL,
        mean_root_deviation REAL,
        multi_spread INTEGER,
        single_spread INTEGER,
        repairable INTEGER,
        best_repair_type TEXT,
        repair_delta_improvement INTEGER,
        repair_path TEXT,
        multi_repaired_b36 TEXT,
        single_repaired_b36 TEXT,
        line_balance_score REAL,
        corner_weight INTEGER,
        grid_signature TEXT
    )''')
    write_header = not os.path.exists(csv_out)
    with open(csv_out, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow([
                'grid_id', 'grid_base36', 'delta', 'is_unique', 'magic_sum',
                'triad_avg', 'triad_stddev', 'mean_root_deviation',
                'multi_spread', 'single_spread', 'repairable', 'best_repair_type',
                'repair_delta_improvement', 'repair_path',
                'multi_repaired_b36', 'single_repaired_b36',
                'line_balance_score', 'corner_weight', 'grid_signature'
            ])
        for row in c.execute(query):
            base36, delta, is_unique, is_magic_sum, _ = row
            grid = grid_base36_utils.base36_to_grid(base36)
            triad_avg = int(triad_averaging_check(grid))
            triad_stddev = compute_triad_stddev(grid)
            mean_root_deviation = compute_mean_root_deviation(grid)
            line_spread, _ = line_delta_spread(grid)
            repairs = []
            single_grid, single_spread = attempt_single_cell_repair(grid)
            repairs.append(('single', single_spread, single_grid, 'single-cell mutation'))
            multi_grid, multi_spread = attempt_multi_cell_repair(grid)
            repairs.append(('multi', multi_spread, multi_grid, 'multi-cell mutation'))
            edge_grid, edge_spread, edge_path = attempt_edge_swap_repair(grid)
            repairs.append(('edge-swap', edge_spread, edge_grid, edge_path))
            square_grid, square_spread, square_path = attempt_perfect_square_nudge(grid)
            repairs.append(('square-swap', square_spread, square_grid, square_path))
            triad_grid, triad_spread, triad_path = attempt_triad_harmony_repair(grid)
            repairs.append(('triad-harmony', triad_spread, triad_grid, triad_path))
            entropy_grid, entropy_spread, entropy_path = attempt_entropy_repair(grid)
            repairs.append(('entropy', entropy_spread, entropy_grid, entropy_path))
            best_type, best_spread, _, best_path = min(repairs, key=lambda x: x[1])
            single_repaired_b36 = grid_base36_utils.grid_to_base36(single_grid)
            multi_repaired_b36 = grid_base36_utils.grid_to_base36(multi_grid)
            repairable = int(best_spread < line_spread)
            repair_delta_improvement = int(line_spread - best_spread)
            line_balance_score = compute_line_balance_score(grid)
            corner_weight = compute_corner_weight(grid)
            grid_signature = compute_grid_signature(grid)
            writer.writerow([
                base36, base36, delta, is_unique, is_magic_sum,
                triad_avg, triad_stddev, mean_root_deviation,
                multi_spread, single_spread, repairable, best_type,
                repair_delta_improvement, best_path,
                multi_repaired_b36, single_repaired_b36,
                line_balance_score, corner_weight, grid_signature
            ])
            c.execute(f'INSERT OR IGNORE INTO {table_name} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      (base36, base36, delta, is_unique, is_magic_sum,
                       triad_avg, triad_stddev, mean_root_deviation, multi_spread, single_spread, repairable, best_type,
                       repair_delta_improvement, best_path,
                       multi_repaired_b36, single_repaired_b36,
                       line_balance_score, corner_weight, grid_signature))
    conn.commit()
    conn.close()
    print(f"Exported candidates to {csv_out} and {table_name} table in {DB}.")

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Expanded schema
    c.execute(f'''CREATE TABLE IF NOT EXISTS {GOOD_TABLE} (
        grid_id TEXT PRIMARY KEY,
        grid_base36 TEXT,
        delta REAL,
        is_unique INTEGER,
        magic_sum INTEGER,
        triad_avg INTEGER,
        triad_stddev REAL,
        mean_root_deviation REAL,
        multi_spread INTEGER,
        single_spread INTEGER,
        repairable INTEGER,
        best_repair_type TEXT,
        repair_delta_improvement INTEGER,
        repair_path TEXT,
        multi_repaired_b36 TEXT,
        single_repaired_b36 TEXT,
        line_balance_score REAL,
        corner_weight INTEGER,
        grid_signature TEXT
    )''')
    # Prepare CSV
    write_header = not os.path.exists(CSV_OUT)
    with open(CSV_OUT, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow([
                'grid_id', 'grid_base36', 'delta', 'is_unique', 'magic_sum',
                'triad_avg', 'triad_stddev', 'mean_root_deviation',
                'multi_spread', 'single_spread', 'repairable', 'best_repair_type',
                'repair_delta_improvement', 'repair_path',
                'multi_repaired_b36', 'single_repaired_b36',
                'line_balance_score', 'corner_weight', 'grid_signature'
            ])
        for row in c.execute(QUERY):
            base36, delta, is_unique, is_magic_sum, _ = row
            grid = grid_base36_utils.base36_to_grid(base36)
            triad_avg = int(triad_averaging_check(grid))
            triad_stddev = compute_triad_stddev(grid)
            mean_root_deviation = compute_mean_root_deviation(grid)
            line_spread, _ = line_delta_spread(grid)
            # Try all repair strategies and pick the best
            repairs = []
            single_grid, single_spread = attempt_single_cell_repair(grid)
            repairs.append(('single', single_spread, single_grid, 'single-cell mutation'))
            multi_grid, multi_spread = attempt_multi_cell_repair(grid)
            repairs.append(('multi', multi_spread, multi_grid, 'multi-cell mutation'))
            edge_grid, edge_spread, edge_path = attempt_edge_swap_repair(grid)
            repairs.append(('edge-swap', edge_spread, edge_grid, edge_path))
            square_grid, square_spread, square_path = attempt_perfect_square_nudge(grid)
            repairs.append(('square-swap', square_spread, square_grid, square_path))
            triad_grid, triad_spread, triad_path = attempt_triad_harmony_repair(grid)
            repairs.append(('triad-harmony', triad_spread, triad_grid, triad_path))
            entropy_grid, entropy_spread, entropy_path = attempt_entropy_repair(grid)
            repairs.append(('entropy', entropy_spread, entropy_grid, entropy_path))
            # Find best repair
            best_type, best_spread, _, best_path = min(repairs, key=lambda x: x[1])
            single_repaired_b36 = grid_base36_utils.grid_to_base36(single_grid)
            multi_repaired_b36 = grid_base36_utils.grid_to_base36(multi_grid)
            repairable = int(best_spread < line_spread)
            repair_delta_improvement = int(line_spread - best_spread)
            line_balance_score = compute_line_balance_score(grid)
            corner_weight = compute_corner_weight(grid)
            grid_signature = compute_grid_signature(grid)
            # Write to CSV
            writer.writerow([
                base36, base36, delta, is_unique, is_magic_sum,
                triad_avg, triad_stddev, mean_root_deviation,
                multi_spread, single_spread, repairable, best_type,
                repair_delta_improvement, best_path,
                multi_repaired_b36, single_repaired_b36,
                line_balance_score, corner_weight, grid_signature
            ])
            # Write to good_grids table (ignore duplicates)
            c.execute(f'INSERT OR IGNORE INTO {GOOD_TABLE} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                      (base36, base36, delta, is_unique, is_magic_sum,
                       triad_avg, triad_stddev, mean_root_deviation, multi_spread, single_spread, repairable, best_type,
                       repair_delta_improvement, best_path,
                       multi_repaired_b36, single_repaired_b36,
                       line_balance_score, corner_weight, grid_signature))
    conn.commit()
    conn.close()
    print(f"Exported good candidates with advanced diagnostics to {CSV_OUT} and {GOOD_TABLE} table in {DB}.")
    
    # Wide shortlist (delta ≤ 150, is_unique=1)
    export_candidates(WIDE_QUERY, WIDE_CSV_OUT, WIDE_TABLE)
    # Non-unique shortlist (delta ≤ 150, is_unique=0)
    export_candidates(NU_QUERY, NU_CSV_OUT, NU_TABLE)
    # Wide250 shortlist (delta ≤ 250, is_unique=1)
    export_candidates(WIDE250_QUERY, WIDE250_CSV_OUT, WIDE250_TABLE)
    # Ultra shortlist (delta ≤ 500, no is_unique filter)
    export_candidates(ULTRA_QUERY, ULTRA_CSV_OUT, ULTRA_TABLE)

if __name__ == '__main__':
    main()
