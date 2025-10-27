import numpy as np

BASE36_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'

def int_to_base36(n):
    if n == 0:
        return '0'
    digits = []
    while n:
        digits.append(BASE36_ALPHABET[n % 36])
        n //= 36
    return ''.join(reversed(digits))

def base36_to_int(s):
    n = 0
    for c in s:
        n = n * 36 + BASE36_ALPHABET.index(c)
    return n

def grid_to_base36(grid):
    # grid: 3x3 numpy array or list of ints
    flat = np.array(grid).flatten()
    return '-'.join(int_to_base36(int(x)) for x in flat)

def base36_to_grid(s):
    # s: base36 string with '-' separators
    nums = [base36_to_int(part) for part in s.split('-')]
    return np.array(nums).reshape((3,3))

# Example usage:
if __name__ == '__main__':
    grid = np.array([
        [961, 1444, 1089],
        [1296, 1156, 1024],
        [1225, 900, 1369]
    ])
    encoded = grid_to_base36(grid)
    print('Base36 encoded:', encoded)
    decoded = base36_to_grid(encoded)
    print('Decoded grid:\n', decoded)
