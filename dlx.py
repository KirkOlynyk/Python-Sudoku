'''
dlx.py

A Python implementation of Donald Knuth\'s Dancing Links algorithm.
This is a debug version with methods added for debugging.

Reference:

Donald E. Knuth: https://arxiv.org/abs/cs/0011047

'''

from typing import Any, List, Iterator, Callable, cast
COLUMN_NAME = Any
BROADCASTER = Callable[[Iterator[List[COLUMN_NAME]]], None]
MAX_OHS_COUNT = 1000

class Link(object): # pylint: disable=too-many-instance-attributes
    'doubly linked node object'
    def __init__(self) -> None:
        self.left = self
        self.right = self
        self.up = self          # pylint: disable=invalid-name
        self.down = self

    def insert_left(self, other) -> None:
        'insert other object to the left of this one'
        other.left = self.left
        other.right = self
        self.left.right = other
        self.left = other

    def insert_above(self, other) -> None:
        'insert the other object above this one'
        other.down = self
        other.up = self.up
        self.up.down = other
        self.up = other # pylint: disable=invalid-name

class Column(Link):
    'Column class'
    def __init__(self, name: COLUMN_NAME) -> None:
        Link.__init__(self)
        self.name = name
        self.size = 0

    def cover(self) -> None:
        '''
    removes column from the header list and removes all rows in the column\'s
    own list from other column lists they are in
        '''
        self.right.left = self.left
        self.left.right = self.right
        for bit0 in self.get_bits_down():
            for bit in bit0.get_other_bits_right():
                bit.down.up = bit.up
                bit.up.down = bit.down
                bit.column.size -= 1

    def uncover(self) -> None:
        'inverse of cover'
        for bit0 in self.get_bits_up():
            for bit in bit0.get_other_bits_left():
                bit.column.size += 1
                bit.up.down = bit
                bit.down.up = bit
        self.right.left = self
        self.left.right = self

    def get_bits_down(self):
        'iterate over all the bits in a column going downward'
        bit = self.down
        while bit != self:
            yield cast(Bit, bit)
            bit = bit.down

    def get_bits_up(self):
        'iterate over all the bits in a column going upward'
        bit = self.up
        while bit != self:
            yield cast(Bit, bit)
            bit = bit.up

class Bit(Link):
    'Set Bit class'
    def __init__(self, col: Column) -> None:
        Link.__init__(self)
        self.column = col

    def get_other_bits_right(self):
        'iterate over all the other bits in the row going right'
        bit = self.right
        while bit != self:
            yield cast(Bit, bit)
            bit = bit.right

    def get_other_bits_left(self):
        'iterate over all the other bits in the row going left'
        bit = self.left
        while bit != self:
            yield cast(Bit, bit)
            bit = bit.left

class Root(Link):
    'Root class -- implementing the Dancing Links algorithm'
    def __init__(self,
                 column_names: List[COLUMN_NAME],
                 set_bits: List[List[int]]) -> None:
        '''
    Argmuents:

        column_names:

            a list of objects that the caller uses as an identifier
            for the column of the dancing links matrix. When the
            function \'search\' is called the callback function is
            passed a column object and the caller can then retrieve
            the column name. The width of the dancing links matrix
            is equal to the length of the column names list

        set_bits:

            a list of lists of integers. The length of \'set_bits\'
            is equal to the number of rows in the dancing links
            matrix. Each member of set_bits is a list of occupied
            columns of the corresponding row in the dancing links
            matrix. Consider the following dancing links matrix:

                    0 1 2 3 4 5 6
                  +---------------+
                0 | 0 0 1 0 1 1 0 |
                1 | 1 0 0 1 0 0 1 |
                2 | 0 1 1 0 0 1 0 |
                3 | 1 0 0 1 0 0 0 |
                4 | 0 1 0 0 0 0 1 |
                5 | 0 0 0 1 1 0 1 |
                  +---------------+

            Since there are 6 rows in the dancing links matrix, the set_bits
            representation of this will have 6 rows, where each row
            is a list of the columns that are occupied with a bit, thus the
            set_bits represetation of this dancing links matrix is

            set_bits = [[2,4,5],[0,3,6],[1,2,5],[0,3],[1,6],[3,4,6]]
        '''
        Link.__init__(self)
        columns = []
        for column_name in column_names:
            column = Column(name=column_name)
            self.insert_left(column)
            columns.append(column)
        for row in set_bits:
            bit0 = None
            for i in row:
                column = columns[i]
                bit = Bit(column)
                column.insert_above(bit)
                column.size += 1
                if bit0 is None:
                    bit0 = bit
                else:
                    bit0.insert_left(bit)

    def _choose(self) -> Column:
        # returns the column with the least number of 1's
        smallest_size = 100000000
        ans = None
        column = self.right # type: Column
        while column != self:
            if column.size < smallest_size: # pylint: disable=no-member
                ans = column
                smallest_size = column.size # pylint: disable=no-member
            column = cast(Column, column.right)
        return ans

    def _search(self,
                k: int,
                ohs: List[Bit],
                bcaster: BROADCASTER
               ) -> None:
        # invokes the dancing links search algorithm
        if self.right == self:
            bcaster(_get_column_name_lists(ohs[:k]))
            return
        column = self._choose()
        column.cover()
        for bit_0 in column.get_bits_down():
            ohs[k] = bit_0
            for bit_1 in bit_0.get_other_bits_right():
                bit_1.column.cover()
            self._search(k + 1, ohs, bcaster)
            bit_2 = ohs[k]
            column = bit_2.column
            for bit_3 in bit_2.get_other_bits_left():
                bit_3.column.uncover()
        column.uncover()

    def search(self, bcaster: BROADCASTER) -> None:
        'searches for the solutions of the exact cover problem'
        self._search(0, [None]*MAX_OHS_COUNT, bcaster)

    def get_columns(self) -> Iterator[Column]:
        'iterate the columns of the dlx graph'
        column = self.right
        while column != self:
            yield cast(Column, column)
            column = column.right

def _get_column_name_lists(bits: List[Bit]) -> Iterator[List[COLUMN_NAME]]:
    for bit0 in bits:
        ans = [bit0.column.name]
        for bit1 in bit0.get_other_bits_right():
            ans.append(bit1.column.name)
        yield ans
