# magic_gpu.py
"""
GPU-accelerated Magic Square of Squares search (NumPy/CuPy unified backend)
- Use --use_gpu to enable GPU (requires cupy)
- All core math (roots, sums, deltas, ratios) is vectorized
- Drop-in compatible with your current project
"""
import argparse
import itertools
import numpy as np
import json
import csv
from itertools import islice
try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    cp = np
    GPU_AVAILABLE = False

import matplotlib.pyplot as plt
import concurrent.futures
from magic_gpu_helpers import process_batch
import grid_base36_utils

# Backend selection logic
def get_backend(use_gpu):
    if use_gpu and GPU_AVAILABLE:
        return cp
    return np

def ratio_based_diagonal_check_batch(roots, tol=1.5, xp=np):
    center = roots[:,1,1]
    diag1 = roots[:,0,0]
    diag2 = roots[:,2,2]
    diag3 = roots[:,0,2]
    diag4 = roots[:,2,0]
    up = roots[:,0,1]
    down = roots[:,2,1]
    left = roots[:,1,0]
    right = roots[:,1,2]
    gm1 = xp.sqrt(center * up)
    gm2 = xp.sqrt(center * down)
    gm3 = xp.sqrt(center * left)
    gm4 = xp.sqrt(center * right)
    return (
        (xp.abs(diag1 - gm1) < tol) &
        (xp.abs(diag2 - gm2) < tol) &
        (xp.abs(diag3 - gm3) < tol) &
        (xp.abs(diag4 - gm4) < tol)
    )

def curvature_balance_batch(roots, tol=1.0, xp=np):
    energies = xp.stack([
        roots[:,0,:].sum(axis=1),
        roots[:,1,:].sum(axis=1),
        roots[:,2,:].sum(axis=1)
    ], axis=1)
    return (energies.max(axis=1) - energies.min(axis=1)) < tol

def triangle_difference_harmony_batch(grids, tol=1.0, xp=np):
    """
    Vectorized triangle harmony check for a batch of grids.
    Checks if the sorted deltas between center and cross roots match known harmonic patterns within a tolerance.
    """
    roots = xp.sqrt(grids)
    center = roots[:,1,1]
    cross = xp.stack([
        roots[:,0,1],  # up
        roots[:,2,1],  # down
        roots[:,1,0],  # left
        roots[:,1,2],  # right
    ], axis=1)
    deltas = xp.abs(center[:,None] - cross)
    deltas_sorted = xp.sort(deltas, axis=1)
    # Known harmonic patterns (expand as needed)
    patterns = xp.array([
        [1,2,3], [3,6,9], [6,12,18], [12,24,36],
        [2,4,6], [4,8,12], [5,10,15], [7,14,21]
    ], dtype=roots.dtype)
    # Broadcast: (N,4) vs (P,3) -> (N,P,3)
    # Only compare first 3 sorted deltas to patterns
    deltas3 = deltas_sorted[:,:3][:,None,:]  # (N,1,3)
    patterns = patterns[None,:,:]            # (1,P,3)
    close = xp.all(xp.isclose(deltas3, patterns, atol=tol), axis=2)  # (N,P)
    # Pass if any pattern matches
    return close.any(axis=1)

def is_unique_grid_batch(grids, xp):
    # Vectorized uniqueness: True if all 9 values are unique in each grid
    # grids: (N, 3, 3)
    flat = grids.reshape((grids.shape[0], 9))
    # Use xp.unique with axis=1 if available, else fallback
    def unique_count(row):
        return len(xp.unique(row))
    if hasattr(xp, 'unique'):
        return xp.apply_along_axis(lambda row: len(xp.unique(row)) == 9, 1, flat)
    else:
        # fallback for numpy
        return np.apply_along_axis(lambda row: len(np.unique(row)) == 9, 1, flat)

def average_line_delta_batch(grids, target_sums, xp):
    # grids: (N, 3, 3), target_sums: (N,)
    lines = xp.stack([
        grids[:,0,:], grids[:,1,:], grids[:,2,:],
        grids[:,:,0], grids[:,:,1], grids[:,:,2],
        xp.stack([grids[:,0,0], grids[:,1,1], grids[:,2,2]], axis=1),
        xp.stack([grids[:,0,2], grids[:,1,1], grids[:,2,0]], axis=1)
    ], axis=1)  # (N, 8, 3)
    line_sums = lines.sum(axis=2)  # (N, 8)
    delta = xp.abs(line_sums - target_sums[:, None])
    return delta.mean(axis=1)

def evaluate_grid_batch(grids, xp, delta_tol=18, phi_tol=0.05, diag_tol=1.5, curv_tol=1.0, triangle_harmony=False, triangle_tol=1.0, return_details=True, mode="full"):
    # Uniqueness check (Tier 1, always applied)
    unique_mask = is_unique_grid_batch(grids, xp)
    # Basic magic sum check (Tier 1)
    row_sums = grids.sum(axis=2)
    col_sums = grids.sum(axis=1)
    diag1 = grids[:, [0,1,2], [0,1,2]].sum(axis=1)
    diag2 = grids[:, [0,1,2], [2,1,0]].sum(axis=1)
    magic_sum = row_sums[:,0]
    magic_mask = (
        (row_sums == magic_sum[:,None]).all(axis=1) &
        (col_sums == magic_sum[:,None]).all(axis=1) &
        (diag1 == magic_sum) & (diag2 == magic_sum)
    )
    # Early exit for tier1
    if mode == "tier1":
        mask = unique_mask & magic_mask
        score_detail = {"unique": ~unique_mask, "magic_sum": ~magic_mask}
        score = (~mask).astype(int)
        if return_details:
            return mask, score, score_detail
        else:
            return mask, score
    # Tier 2: add delta/root harmony
    roots = xp.sqrt(grids)
    center = roots[:,1,1]
    cross = xp.stack([roots[:,0,1], roots[:,2,1], roots[:,1,0], roots[:,1,2]], axis=1)
    deltas = xp.abs(center[:,None] - cross)
    delta_spread = deltas.max(axis=1) - deltas.min(axis=1)
    delta_mask = delta_spread <= delta_tol
    if mode == "tier2":
        mask = unique_mask & magic_mask & delta_mask
        score_detail = {"unique": ~unique_mask, "magic_sum": ~magic_mask, "delta_check": ~delta_mask}
        score = (~mask).astype(int)
        if return_details:
            return mask, score, score_detail
        else:
            return mask, score
    # Full mode: all checks
    def phi_ratio(a, b):
        ratio = xp.maximum(a, b) / xp.minimum(a, b)
        return (xp.abs(ratio - 1.618) < phi_tol) | (xp.abs(ratio - 0.618) < phi_tol)
    phi1 = phi_ratio(roots[:,0,1], roots[:,2,1])
    phi2 = phi_ratio(roots[:,1,0], roots[:,1,2])
    phi_mask = phi1 & phi2
    diag_mask = ratio_based_diagonal_check_batch(roots, tol=diag_tol, xp=xp)
    curv_mask = curvature_balance_batch(roots, tol=curv_tol, xp=xp)
    if triangle_harmony:
        tri_mask = triangle_difference_harmony_batch(grids, tol=triangle_tol, xp=xp)
    else:
        tri_mask = xp.ones(grids.shape[0], dtype=bool)
    mask = unique_mask & magic_mask & delta_mask & phi_mask & diag_mask & curv_mask & tri_mask
    avg_line_delta = average_line_delta_batch(grids, magic_sum, xp)
    score_detail = {
        "unique": ~unique_mask,
        "magic_sum": ~magic_mask,
        "delta_check": ~delta_mask,
        "phi_check": ~phi_mask,
        "diag_check": ~diag_mask,
        "curv_check": ~curv_mask,
        "triangle_harmony": ~tri_mask if triangle_harmony else xp.zeros(grids.shape[0], dtype=bool),
        "avg_line_delta": avg_line_delta
    }
    score = sum(v.astype(int) for k, v in score_detail.items() if k != "avg_line_delta") + avg_line_delta
    if return_details:
        return mask, score, score_detail
    else:
        return mask, score

def export_valid_grids(grids, mask, filename="valid_grids.npy", txtfile="valid_grids.txt"):
    valid = grids[mask]
    if hasattr(valid, 'get'):
        valid = valid.get()
    np.save(filename, valid)
    with open(txtfile, "w", encoding="utf-8") as f:
        for grid in valid:
            base36 = grid_base36_utils.grid_to_base36(grid)
            # Only write base36 encoding (one line per grid)
            f.write(f"{base36}\n")

def export_empty_valid_grids(filename="valid_grids.npy", txtfile="valid_grids.txt"):
    np.save(filename, np.array([]))
    with open(txtfile, "w", encoding="utf-8") as f:
        f.write("No valid grids found.\n")

def plot_score_histogram(scores):
    if hasattr(scores, 'get'):
        scores = scores.get()
    plt.hist(scores, bins=range(int(scores.min()), int(scores.max())+2), color='skyblue', edgecolor='black')
    plt.xlabel('Grid Score (lower is better)')
    plt.ylabel('Count')
    plt.title('Distribution of Grid Scores')
    plt.show()

def plot_score_scatter(scores, score_detail, x_metric, y_metric, z_metric=None, mask=None):
    x = score_detail[x_metric]
    y = score_detail[y_metric]
    if hasattr(x, 'get'):
        x = x.get()
    if hasattr(y, 'get'):
        y = y.get()
    if mask is not None:
        x = x[~mask]
        y = y[~mask]
    if z_metric:
        z = score_detail[z_metric]
        if hasattr(z, 'get'):
            z = z.get()
        if mask is not None:
            z = z[~mask]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z, c='red', alpha=0.5)
        ax.set_xlabel(x_metric)
        ax.set_ylabel(y_metric)
        ax.set_zlabel(z_metric)
        plt.title(f'3D Scatter: {x_metric} vs {y_metric} vs {z_metric}')
    else:
        plt.scatter(x, y, c='red', alpha=0.5)
        plt.xlabel(x_metric)
        plt.ylabel(y_metric)
        plt.title(f'Scatter: {x_metric} vs {y_metric}')
    plt.show()

def export_score_detail(score_detail, filename_csv="score_detail.csv", filename_json="score_detail.json"):
    # Convert all arrays to lists for export
    keys = list(score_detail.keys())
    n = len(next(iter(score_detail.values())))
    rows = [dict((k, bool(score_detail[k][i])) for k in keys) for i in range(n)]
    # CSV
    with open(filename_csv, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    # JSON
    with open(filename_json, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

def generate_grid_batches(numbers, batch_size=1000, center=None, xp=np):
    """
    Generator that yields batches of 3x3 grids as arrays, only with unique values.
    """
    combos = itertools.combinations(numbers.tolist(), 9)  # all unique sets of 9 squares
    batch = []
    for combo in combos:
        if center is not None and center not in combo:
            continue
        centers = [center] if center is not None else combo
        for c in centers:
            rest = [x for x in combo if x != c]
            for perm in itertools.permutations(rest, 8):
                grid = xp.array([
                    [perm[0], perm[1], perm[2]],
                    [perm[3], c, perm[4]],
                    [perm[5], perm[6], perm[7]]
                ])
                # All values are unique by construction
                batch.append(grid)
                if len(batch) >= batch_size:
                    yield xp.stack(batch)
                    batch = []
    if batch:
        yield xp.stack(batch)

def log_candidate(grid, score_detail, xp, label="tier1"):
    # Only log if unique and magic_sum are True
    if score_detail.get("unique", True) and score_detail.get("magic_sum", True):
        with open(f"candidates_{label}.txt", "a", encoding="utf-8") as f:
            for row in grid:
                f.write(" ".join(str(int(x)) for x in row) + "\n")
            f.write("\n")

def symmetry_boost_score(grid):
    sym_pairs = [((0,0),(2,2)), ((0,2),(2,0)), ((0,1),(2,1)), ((1,0),(1,2))]
    score = 0
    for (i1,j1), (i2,j2) in sym_pairs:
        if grid[i1][j1] == grid[i2][j2]:
            score += 1
    return score

def log_top_near_magic_candidates(grids, avg_line_deltas, score_detail, N=10, filename="near_magic_candidates.txt"):
    if hasattr(grids, 'get'):
        grids = grids.get()
    if hasattr(avg_line_deltas, 'get'):
        avg_line_deltas = avg_line_deltas.get()
    idx = np.argsort(avg_line_deltas)[:N]
    with open(filename, "a", encoding="utf-8") as f:
        for i in idx:
            grid = grids[i]
            base36 = grid_base36_utils.grid_to_base36(grid)
            delta = avg_line_deltas[i]
            # Only write base36 encoding and delta (tab-separated)
            f.write(f"{base36}\t{delta:.4f}\n")
# NOTE: For visualization or re-testing, use grid_base36_utils.base36_to_grid() to decode.

def smart_mutate_near_magic(grid, used_squares, all_squares):
    # Try to mutate a near-magic grid by replacing duplicate values with unused perfect squares.
    grid_flat = grid.flatten()
    unique_vals, counts = np.unique(grid_flat, return_counts=True)
    dups = unique_vals[counts > 1]
    unused = [x for x in all_squares if x not in grid_flat]
    mutated_grids = []
    for dup in dups:
        for replacement in unused:
            new_grid = grid_flat.copy()
            idx = np.where(new_grid == dup)[0][0]  # replace first occurrence
            new_grid[idx] = replacement
            if len(set(new_grid)) == 9:
                new_grid = new_grid.reshape((3,3))
                mutated_grids.append(new_grid)
    return mutated_grids

def main():
    parser = argparse.ArgumentParser(description="GPU-accelerated Magic Square of Squares search.")
    parser.add_argument('--use_gpu', action='store_true', help='Use GPU acceleration with CuPy if available')
    parser.add_argument('--workers', type=int, default=4, help='Number of CPU workers for permutation generation')
    parser.add_argument('--sample', type=int, default=1000, help='Number of grid permutations to test (for benchmarking)')
    parser.add_argument('--batch_mode', action='store_true', help='Loop over multiple combos and aggregate results')
    parser.add_argument('--center', type=int, default=None, help='Lock a specific value in the center square (optional)')
    parser.add_argument('--plot_scores', action='store_true', help='Plot histogram of grid scores')
    parser.add_argument('--triangle_harmony', action='store_true', help='Enable triangle difference harmony filter')
    parser.add_argument('--triangle_tol', type=float, default=1.0, help='Tolerance for triangle harmony filter')
    parser.add_argument('--export_scores', action='store_true', help='Export score_detail for all grids to CSV/JSON')
    parser.add_argument('--scatter', nargs='+', help='Plot 2D or 3D scatter of score metrics, e.g. --scatter delta_check phi_check [curv_check]')
    parser.add_argument('--batch_size', type=int, default=1000, help='Batch size for grid generation and evaluation')
    parser.add_argument('--mode', choices=["full", "tier1", "tier2"], default="full",
                        help="Level of filtering: 'tier1' logs magic sum only, 'tier2' adds delta and triangle checks, 'full' runs all tests.")
    args = parser.parse_args()

    xp = get_backend(args.use_gpu)
    print(f"Using backend: {'CuPy (GPU)' if xp is cp else 'NumPy (CPU)'}")

    numbers = xp.array([i**2 for i in range(30, 81)])
    total_valid = 0
    total_grids = 0
    found_valid = False

    cpu_mode = (xp is np)
    if cpu_mode:
        args_dict = {
            'triangle_harmony': args.triangle_harmony,
            'triangle_tol': args.triangle_tol,
            'mode': args.mode
        }
        with concurrent.futures.ProcessPoolExecutor() as executor:
            batch_futures = []
            for grids in generate_grid_batches(numbers, batch_size=args.batch_size, center=args.center, xp=np):
                batch_futures.append(executor.submit(process_batch, grids, args_dict))
            for future in concurrent.futures.as_completed(batch_futures):
                mask, score_detail, grids = future.result()
                if int(mask.sum()) > 0:
                    found_valid = True
                    print(f"Batch: Valid magic grids found: {int(mask.sum())} / {len(grids)}")
                    print("Sample valid grid (roots):")
                    print(xp.sqrt(grids[mask][0]))
                    export_valid_grids(grids, mask)
                total_valid += int(mask.sum())
                total_grids += len(grids)
                # Optionally, print diagnostics for failed grids in this batch
                if mask.sum() < len(grids):
                    print("\nDiagnostics for failed grids (first 5 in batch):")
                    for i in range(min(5, len(grids))):
                        if mask[i]:
                            continue
                        print(f"Grid {i}: Fails:")
                        for k, v in score_detail.items():
                            if isinstance(v, np.ndarray) or hasattr(v, 'get'):
                                if v[i]:
                                    print(f"  - {k}")
                # Log top 10 near-magic candidates by avg_line_delta (even if not fully magic)
                if 'avg_line_delta' in score_detail:
                    log_top_near_magic_candidates(grids, score_detail['avg_line_delta'], score_detail, N=10)
    else:
        # GPU mode: single process, avoid pickling issues
        for grids in generate_grid_batches(numbers, batch_size=args.batch_size, center=args.center, xp=xp):
            mask, _, score_detail = evaluate_grid_batch(
                grids, xp,
                triangle_harmony=args.triangle_harmony,
                triangle_tol=args.triangle_tol,
                return_details=True,
                mode=args.mode
            )
            if int(mask.sum()) > 0:
                found_valid = True
                print(f"Batch: Valid magic grids found: {int(mask.sum())} / {len(grids)}")
                print("Sample valid grid (roots):")
                print(xp.sqrt(grids[mask][0]))
                export_valid_grids(grids, mask)
            total_valid += int(mask.sum())
            total_grids += len(grids)
            # Optionally, print diagnostics for failed grids in this batch
            if mask.sum() < len(grids):
                print("\nDiagnostics for failed grids (first 5 in batch):")
                for i in range(min(5, len(grids))):
                    if mask[i]:
                        continue
                    print(f"Grid {i}: Fails:")
                    for k, v in score_detail.items():
                        if isinstance(v, np.ndarray) or hasattr(v, 'get'):
                            if v[i]:
                                print(f"  - {k}")
            # Log top 10 near-magic candidates by avg_line_delta (even if not fully magic)
            if 'avg_line_delta' in score_detail:
                log_top_near_magic_candidates(grids, score_detail['avg_line_delta'], score_detail, N=10)

    print(f"Total valid magic grids found: {total_valid} / {total_grids}")
    # Always export valid_grids, even if empty
    if not found_valid:
        export_empty_valid_grids()
        print("No valid grids found. Wrote empty valid_grids.npy and valid_grids.txt.")
    # Diagnostics and plotting are now optional and not memory-intensive
    # (remove score_detail and scores accumulation)
    if args.plot_scores:
        print("Plotting is disabled in streaming mode. Use a post-processing script on the output file.")
    if args.scatter:
        print("Scatter plotting is disabled in streaming mode. Use a post-processing script on the output file.")

if __name__ == "__main__":
    main()
