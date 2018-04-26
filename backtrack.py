'backtrack.py'

import copy
import math
import click
from typing import List

class _NotFound(Exception):
    pass

class Grid(object):
    'tbd'
    def __init__(self, zero_rows: List[List[int]]) -> None:
        self._zero_rows = zero_rows
        self._num_rows = len(zero_rows)
        self._num_cols = len(zero_rows[0])
        self._order = int(math.sqrt(self._num_rows))
    def get_num(self, row: int, col: int) -> int:
        'tbd'
        return self._zero_rows[row][col]
    def set_num(self, row: int, col: int, num: int) -> None:
        'tbd'
        self._zero_rows[row][col] = num
    def get_order(self) -> int:
        'tbd'
        return self._order
    def num_rows(self) -> int:
        'tbd'
        return self._num_rows
    def num_cols(self) -> int:
        'tbd'
        return self._num_cols

def _solve_sudoku(grid: Grid) -> bool:
    try:
        row, col = _find_unassigned_location(grid)
        for num in range(1, grid.num_rows() + 1):
            if _no_conflicts(grid, row, col, num):
                grid.set_num(row, col, num)
                if _solve_sudoku(grid):
                    return True
                grid.set_num(row, col, 0)
    except _NotFound:
        return True
    return False

def _find_unassigned_location(grid: Grid):
    for row in range(grid.num_rows()):
        for col in range(grid.num_cols()):
            if grid.get_num(row, col) == 0:
                return row, col
    raise _NotFound

def _no_conflicts(grid: Grid, row: int, col: int, num: int) -> bool:
    if _used_in_row(grid, row, num):
        return False
    elif _used_in_col(grid, col, num):
        return False
    elif _used_in_box(grid, row, col, num):
        return False
    else:
        return True

def _used_in_row(grid: Grid, row: int, num: int) -> bool:
    for col  in range(grid.num_cols()):
        if grid.get_num(row, col) == num:
            return True
    return False

def _used_in_col(grid: Grid, col: int, num: int) -> bool:
    for row in range(grid.num_rows()):
        if grid.get_num(row, col) == num:
            return True
    return False

def _used_in_box(grid: Grid, row: int, col: int, num: int) -> bool:
    order = grid.get_order()
    box_start_row = row - (row % order)
    box_start_col = col - (col % order)
    for row in range(order):
        for col in range(order):
            if grid.get_num(row + box_start_row, col + box_start_col) == num:
                return True
    return False

def _solve_dot_rows(dot_rows):
    from sudoku import _dot_rows_to_zero_rows, _get_chars_ex
    from drawsudoku import draw_sudoku

    zero_rows = _dot_rows_to_zero_rows(dot_rows)
    solution = copy.deepcopy(zero_rows)
    grid = Grid(solution)

    order = grid.get_order()
    if order == 3:
        labels = _get_chars_ex(('1', '9'))
    elif order == 4:
        labels = _get_chars_ex(('0','9'), ('A', 'F'))
    elif order == 5:
        labels = _get_chars_ex(('A', 'Y'))
    elif order == 6:
        labels = _get_chars_ex(('0', '9'), ('A', 'Z'))
    else:
        raise NotImplementedError

    if _solve_sudoku(grid):
        for i, row in enumerate(zero_rows):
            for j, z in enumerate(row):
                if z != 0:
                    solution[i][j] = 0
        draw_sudoku(zero_rows, solution, order, labels)
    else:
        print("no solution")

def work(path: str, puzzle: int) -> None:
    'Loads puzzles from a YAML file and solve the puzzle of your choice'
    import yaml
    with open(path, 'r') as fobj:
        ans = yaml.load(fobj)
    dot_rows = ans[puzzle]['dot_rows']
    _solve_dot_rows(dot_rows=dot_rows)

@click.command()
@click.option("--path", type=str, help='path to input yaml file', prompt=True)
@click.option("--puzzle", type=int, help='zero based puzzle number', prompt=True)
def main(path: str, puzzle: int) -> None:
    'main entry point'
    work(path, puzzle)

if __name__ == '__main__':
    # main() # pylint: disable=no-value-for-parameter
    main()
