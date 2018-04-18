'''
sudoku.py

    1. Turn the Sudoku puzzle into an exact cover problem
       by representing the contraints on the solution as
       a list of bit lists

    2. Call Knuth's Dancing Links algorithm to solve the exact
       cover problem.

    3. Represent the solution as a filled Sudoku puzzle and
       display the results using the \'graphics\' module


Every sudoku puzzle has an order which I shall call \'N\' for the purposes
of this discussion. N = 1, 2, 3, 4, ...
The Sudoku puzzle has N^2 rows, columns and boxes. Each row, column and
box has N^2 cells. The total number of cells in a sudoku puzzle is N^4.
For example the usual 9 x 9 Sudoku puzzle corresponds to N = 3. The
Sudoku cells are filled with N^2 different symbols. Usually symbols
used are the integers 1, 2, .., N^2 but you could use any other set
of symbols as well. N=4 Sudoku uses the 16 hexadecimal digits
'0', '1', .. 'F' and N=5 Sudoku uses 25 symbols 'A','B', .., 'Y'.


Under the rules of Sudoku, a solution to a puzzle is valid if
the following constraints are obeyed:

    1.  Each cell contains one symbol
    2.  Each row contains exactly one copy of each symbol
    3.  Each column contains exactly one copy of each symbol
    4.  Each box contains exatly one copy of each symbol

The job now is to convert this into an exact cover problem.

What is a an \'exact cover\' problem?

(From Knuth\'s paper: https://arxiv.org/abs/cs/0011047)

"Given a matrix of 0s and 1s, does it have a set of rows containing exactly
one 1 in each column?"

How can we express the Sudoku puzzle as and exact cover problem?

Each time we put a value in a cell we are putting that value in a row
column and box. We allocate one bit (1 or 0) for each of the N^4
cells. Once a cell has a value written in it, that particular bit is set.
We allocate one cell for each of the N^4 row-value combinations. When
we write a value in a row we set that paticular bit. The same goes
for the N^4 value-column and N^4 value-box combinations. This means
that each row of the cover matrix has 4 * (N^4) bits. Each time a cell
is given a value 4 bits in a row are set corresponding to the cell,
row, column and box affected. Since there are N^4 cells and N^2 values
there are N^6 possible cell entries and thus N^6 possible bit rows
in the cover matrix. Thus the exact cover matrix for all Sudoku
puzzles has N^6 rows and 4 * N^4 columns. Each row has 4 bits set.

Such a cover matrix corresponds to a Sudoku puzzle where none have
the cells have been given a value initially. Such a puzzle would
have a large number of solutions since there are no constraints.
Each initial cell value implies that one of the rows must be
in the solution. It also means that any row that shares a bit
in the same columns of these inital rows must be elimiated
from consideration. This sounds hard to do but fortunately the Dancing
Links algorithm includes a function called \'cover\' that accomplishes
this \'pruning\' of the cover matrix. So here is the procedure

    1. Create a cover matrix assuming no initial values
    2. For each initial cell value \'cover\' the column corresponding
       to each bit in the corresponding row in the cover matrix.
    3. Call the dancing links algorithm for the solutions(s)
    4. Convert the solution (i.e. the value of every cell) into
       a human readable form.
'''

import click
from typing import List, Tuple, Iterator
import dlx
from drawsudoku import draw_sudoku

IValue = int
IRow = int
IColumn = int
IVRC = Tuple[IValue, IRow, IColumn]
Order = int
Puzzle = List[List[int]]                    # pylint: disable=invalid-name
COLUMN_NAME = int                           # pylint: disable=invalid-name

COUNT = 0 # count of the number of Sudoku solutions found

_order_isomorphism = [                          # pylint: disable=invalid-name
    ('.', 0),
    ('1', 1), ('2', 2), ('3', 3),
    ('4', 4), ('5', 5), ('6', 6),
    ('7', 7), ('8', 8), ('9', 9),
]
_order4_isomorphism = [                         # pylint: disable=invalid-name
    ('.', 0),
    ('0', 1), ('1', 2), ('2', 3), ('3', 4),
    ('4', 5), ('5', 6), ('6', 7), ('7', 8),
    ('8', 9), ('9', 10), ('A', 11), ('B', 12),
    ('C', 13), ('D', 14), ('E', 15), ('F', 16)
]
TEMP = ['.']
TEMP.extend([chr(i) for i in range(ord('A'), ord('Z'))])
# pylint: disable=invalid-name
_order5_isomorphisms = [(c, i) for (i, c) in enumerate(TEMP)]

class Sudoku(object):
    '''
Sudoku class

Constructor Arguments:

    order: 1, 2, 3, ...
    puzzle: zero-based representation of the intial state
            of the Sudoku puzzle

The zero based representation is a list of rows where each row
is a list of integers where zero represents an empty cell while
the numbers 1 .. order^2 represent specified initial cell values.
For exampl, suppose we have a 4 x 4 sudoku matrix, then the
integers representing the legal values are 1, 2, 3, 4 and
0 represents a blank cell in the Sudoku puzzle

Typical 4 X 4 Sudoku Puzzle

                +-------+
                |1  |4  |
                |   |  3|
                +-------+
                |2  |   |
                |  1|  4|
                +-------+

Zero row representation

            zero_rows = [
                [1, 0, 4, 0],
                [0, 0, 0, 3],
                [2, 0, 0, 0],
                [0, 1, 0, 4]
            ]
    '''
    def __init__(self, order: Order, puzzle: Puzzle) -> None:
        self.N = order                      # pylint: disable=invalid-name
        self.N2 = order * order             # pylint: disable=invalid-name
        self.N4 = self.N2 * self.N2         # pylint: disable=invalid-name
        self.n_dlx_columns = 4 * self.N4
        self.N6 = self.N2 * self.N4         # pylint: disable=invalid-name
        self._check_puzzle(puzzle)

    # pylint: disable=invalid-name
    def _get_iBox(self, i_row: int, i_col: int) -> int:
        'returns the index of the box for a given row and column'
        assert i_row >= 0  and i_row < self.N2
        assert i_col >= 0 and i_col < self.N2
        ans = (i_col // self.N) + self.N * (i_row // self.N)
        assert ans >= 0 and ans < self.N2
        return ans

    def _check_puzzle(self, puzzle: Puzzle) -> None:
        'checks that the incoming puzzle is valid'
        for row in puzzle:
            for value in row:
                if value < 0 or value > self.N2:
                    raise ValueError

    def get_bit_column_row_ex(self,
                              i_value: int,
                              i_row: int,
                              i_col: int
                             ) -> List[int]:
        'gets the occupation numbers for the row of a dlx matrix'
        assert i_value >= 0 and i_value < self.N2
        assert i_row >= 0 and i_row < self.N2
        assert i_col >= 0 and i_col < self.N2
        i_box = self._get_iBox(i_row=i_row, i_col=i_col)
        j_e = i_col   + self.N2 * i_row
        j_r = i_value + self.N2 * (i_row + self.N2 * 1)
        j_c = i_value + self.N2 * (i_col + self.N2 * 2)
        j_b = i_value + self.N2 * (i_box + self.N2 * 3)
        assert 0 * self.N4 <= j_e and j_e < 1 * self.N4
        assert 1 * self.N4 <= j_r and j_r < 2 * self.N4
        assert 2 * self.N4 <= j_c and j_c < 3 * self.N4
        assert 3 * self.N4 <= j_b and j_b < 4 * self.N4
        return [j_e, j_r, j_c, j_b]

    def _get_ivrc(self, i_dlx: int) -> IVRC:
        'return the value, row and column indexes'
        assert i_dlx >= 0 and i_dlx < self.N6
        i_row = i_dlx // self.N4
        rem = i_dlx - self.N4 * i_row
        i_col = rem // self.N2
        i_value = rem - self.N2 * i_col
        return i_value, i_row, i_col

    def _get_bit_column_row(self, i_dlx: int) -> List[int]:
        'get a list of the occupied columns in the row of a dlx matrix'
        assert i_dlx >= 0 and i_dlx < self.N6
        args = self._get_ivrc(i_dlx)
        return self.get_bit_column_row_ex(*args)

    def get_set_bits(self) -> List[List[int]]:
        'get the full dlx matrix for Sudoku puzzles of this order'
        return [self._get_bit_column_row(i) for i in range(self.N6)]

# pylint: disable=too-many-locals
def solve_zero_rows(zero_rows: Puzzle) -> None:
    ''''
    Solving a Sudoku puzzle represented as a zero base list of integer lists
    '''
    import math
    order = int(math.sqrt(len(zero_rows)))
    sudoku = Sudoku(order, zero_rows)
    set_bits = sudoku.get_set_bits()
    column_names = list(range(sudoku.n_dlx_columns))
    root = dlx.Root(column_names, set_bits)

    # cover the columns already accounted for in the initial state of
    # the Sudoku puzzle. If the constraint is already satisfied, then
    # cover the column corresponding to the constraint
    for i_row, row in enumerate(zero_rows):
        for i_col, i_value in enumerate(row):
            i_value -= 1
            if i_value < 0:
                continue
            column_names = sudoku.get_bit_column_row_ex(i_value, i_row, i_col)
            for column_name in column_names:
                # search for the column in the current dlx matrix
                # it may have been deleted by a previous call to cover
                for column in root.get_columns():
                    if column.name == column_name:
                        column.cover()

    # zero out the representation of the solution which is an
    # N^2 bo N^2 matrix
    solution = []
    for i_row in range(sudoku.N2):
        solution.append([0] * sudoku.N2)

    def bcaster(name_lists: Iterator[List[COLUMN_NAME]]) -> None:
        '''
        callback for the dancing links search function
        Each time this is called it adds a value to
        \'solution\' (the Sudoku solution matrix)
        '''
        global COUNT                # pylint: disable=global-statement
        if COUNT != 0:
            raise ValueError("More than one solution")
        COUNT += 1
        for names in name_lists:
            names.sort()
            j_e = names[0]
            j_r = names[1]
            N2 = sudoku.N2           # pylint: disable=invalid-name

            i_row = j_e // N2
            i_col = j_e - N2 * i_row
            i_value = j_r - N2 * (i_row + N2 * 1)
            solution[i_row][i_col] = i_value + 1

    root.search(bcaster=bcaster)
    if order == 4:
        labels = ['X',
                  '0', '1', '2', '3',
                  '4', '5', '6', '7',
                  '8', '9', 'A', 'B',
                  'C', 'D', 'E', 'F']
    elif order == 5:
        labels = [c for (c, _) in _order5_isomorphisms]
    else:
        labels = ['X', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    if COUNT == 0:
        print("No Solution")
    draw_sudoku(zero_rows, solution, order, labels)

# pylint: disable=invalid-name
_order_indices = {c : v for c, v in _order_isomorphism}
# pylint: disable=invalid-name
_order_chars = {v : c for c, v in _order_isomorphism}
# pylint: disable=invalid-name
_order4_indices = {c : v for c, v in _order4_isomorphism}
# pylint: disable=invalid-name
_order5_indices = {c : v for c, v in _order5_isomorphisms}

def _get_indices(order: int):
    if order == 4:
        return _order4_indices
    elif order == 5:
        return _order5_indices
    else:
        return _order_indices

def _dot_rows_to_zero_rows(dot_rows: List[str]) -> List[List[int]]:
    """
Transforms a \'dot based\' representation of a Sudoku puzzle
into a 'zero based' representation.

To understand this, consider the following 4 x 4 Sudoku puzzle that
would look somthing like the following

                +--------+
                |1  | 4  |
                |   |   3|
                +--------+
                |2  |    |
                |  1|   4|
                +--------+

The dot based representation represents the blank cells with the
period character '.'. The puzzle is represented as a
list of strings. The list contains order^2 strings and
each string has order^2 characters thus the value of each
of the order^4 cells is specified.
The following character sets represent allowable (non blank)
cell values for different Sudoku orders:

(order = 2) ['1', '2', '3', '4']

(order = 3) ['1', '2', '3', '4', '5', '6', '7', '8', '9']

(order = 4) ['0', '1', '2', '3',
             '4', '5', '6', '7',
             '8', '9', 'A', 'B',
             'C', 'D', 'E', 'F']

The zero based representation is a list of rows where each row
is a list of integers where zero represents an empty cell while
the numbers 1 .. order^2 represent specified initial cell values.
The dot- and zero-based representations of the Sudoku puzzle
above are given here

    dot_based = ['1.4.', '...3', '2...', '.1.4']

    zero_based = [
        [1, 0, 4, 0],
        [0, 0, 0, 3],
        [2, 0, 0, 0],
        [0, 1, 0, 4]
    ]
    """
    import math
    order = int(math.sqrt(len(dot_rows)))
    assert order*order == len(dot_rows)
    for row in dot_rows:
        assert len(row) == order*order
    indices = _get_indices(order)
    return [[indices[x] for x in dot_row] for dot_row in dot_rows]

def solve_dot_rows(dot_rows: List[str]) -> None:
    'Solve Sudoku puzzle represented as a dot-based string'
    zero_rows = _dot_rows_to_zero_rows(dot_rows=dot_rows)
    solve_zero_rows(zero_rows)

@click.command()
@click.option("--input", type=str, help='path to input yaml file', prompt=True)
@click.option("--puzzle", type=int, help='zero based puzzle number', prompt=True)
def main(input: str, puzzle: int) -> None:
    'Loads puzzles from a YAML file and solve the puzzle of your choice'
    import yaml
    with open(input, 'r') as fobj:
        ans = yaml.load(fobj)
    try:
        dot_rows = ans[puzzle]['dot_rows']
        solve_dot_rows(dot_rows=dot_rows)
    except KeyError:
        zero_rows = ans[puzzle]['zero_rows']
        solve_zero_rows(zero_rows=zero_rows)

if __name__ == '__main__':
    # main() # pylint: disable=no-value-for-parameter
    main()
