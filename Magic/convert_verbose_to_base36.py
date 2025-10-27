import grid_base36_utils
import re

INPUT = 'near_magic_candidates.txt'
OUTPUT = 'near_magic_candidates_base36.txt'

def parse_grid(lines):
    grid = []
    for line in lines:
        if re.match(r'^\d+ \d+ \d+$', line):
            grid.append([int(x) for x in line.strip().split()])
    if len(grid) == 3:
        return grid
    return None

def parse_delta(lines):
    for line in lines:
        m = re.match(r'Avg line delta: ([\d.]+)', line)
        if m:
            return float(m.group(1))
    return None

def main():
    with open(INPUT, 'r', encoding='utf-8') as fin, open(OUTPUT, 'w', encoding='utf-8') as fout:
        block = []
        for line in fin:
            if line.strip() == '':
                if block:
                    grid = parse_grid(block)
                    delta = parse_delta(block)
                    if grid:
                        base36 = grid_base36_utils.grid_to_base36(grid)
                        if delta is not None:
                            fout.write(f"{base36}\t{delta:.4f}\n")
                        else:
                            fout.write(f"{base36}\n")
                    block = []
            else:
                block.append(line)
        # Handle last block
        if block:
            grid = parse_grid(block)
            delta = parse_delta(block)
            if grid:
                base36 = grid_base36_utils.grid_to_base36(grid)
                if delta is not None:
                    fout.write(f"{base36}\t{delta:.4f}\n")
                else:
                    fout.write(f"{base36}\n")

if __name__ == '__main__':
    main()
