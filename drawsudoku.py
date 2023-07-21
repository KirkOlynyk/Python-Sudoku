"""
For drawing the solution to a Sudoku puzzle
"""

import yaml
from graphics import GraphicsError, Point, Rectangle, Text, Point, Line, color_rgb, GraphWin

# globals #

cell_width = 48
cell_height = 48
left_margin = 2 * cell_width
right_margin = 2 * cell_width
upper_margin = 2 * cell_height
lower_margin = 2 * cell_height

def get_cell_center(i_row, i_col):
    x = left_margin + (i_col + 0.5) * cell_width  # pylint: disable=invalid-name
    y = upper_margin + (i_row + 0.5) * cell_height # pylint: disable=invalid-name
    return Point(x, y)

def get_cell_rectangle(i_row, i_col):
    ptCenter = get_cell_center(i_row, i_col)
    ptA = ptCenter.clone()
    ptB = ptCenter.clone()
    ptA.move(-0.5 * cell_width, -0.5 * cell_height)
    ptB.move(+0.5 * cell_width, +0.5 * cell_height)
    return Rectangle(ptA, ptB)

def draw_sudoku(puzzle, solution, order, labels): # pylint: disable=too-many-locals
    'draws a solved Sudoku puzzle'
    n_rows = order * order
    n_cols = n_rows
    thick = 4
    grid_width = n_rows * cell_width
    grid_height = n_rows * cell_height
    window_width = left_margin + grid_width + right_margin
    window_height = upper_margin + grid_height + lower_margin

    win = GraphWin("Sudoku", window_width, window_height)

    def LabelCell(i_row, i_col, label, color=None):
        text = Text(get_cell_center(i_row, i_col), label)
        text.setSize(cell_height//2)
        if color is not None:
            text.setTextColor(color)
        text.draw(win)

    def draw_horizontal_grid_lines():
        for i_row in range(n_rows + 1):
            x0 = left_margin
            y0 = upper_margin + i_row * cell_height
            pt0 = Point(x0, y0)
            pt1 = Point(x0 + grid_width, y0)
            line = Line(pt0, pt1)
            if i_row % order == 0:
                line.setWidth(thick)
            else:
                line.setWidth(0)
            line.draw(win)
    
    def draw_vertical_grid_lines():
        for i_col in range(n_cols + 1):
            x0 = left_margin + i_col * cell_height
            y0 = upper_margin
            pt0 = Point(x0, y0)
            pt1 = Point(x0, y0 + grid_height)
            line = Line(pt0, pt1)
            if i_col % order == 0:
                line.setWidth(thick)
            else:
                line.setWidth(0)
            line.draw(win)

    def draw_grid():
        draw_horizontal_grid_lines()
        draw_vertical_grid_lines()

    def draw_light_cell(i_row, i_col, i_val):
        LabelCell(i_row, i_col, labels[i_val])

    def draw_dark_cell(i_row, i_col, i_val):
        rect = get_cell_rectangle(i_row, i_col)
        gray = 128
        color = color_rgb(gray, gray, gray)
        rect.setFill(color)
        rect.draw(win)
        LabelCell(i_row, i_col, labels[i_val], 'white')

    def draw_numbers(numbers, draw_cell):
        for i_row, row in enumerate(numbers):
            for i_col, i_val in enumerate(row):
                if i_val == 0:
                    continue
                draw_cell(i_row, i_col, i_val)

    def draw_puzzle_numbers():
        draw_numbers(puzzle, draw_light_cell)

    def draw_solution_numbers():
        draw_numbers(solution, draw_dark_cell)

    def close_window_on_mouse_click():
        x = window_width/2
        y = window_height - cell_height
        msg = "Click on window to close"
        Text(Point(x, y), msg).draw(win)
        _ = win.getMouse()
        win.close()

    try:
        draw_puzzle_numbers()
        draw_solution_numbers()
        draw_grid()
        close_window_on_mouse_click()
    except GraphicsError:
        # Catch the error when the window is closed
        pass

    # click on the window to close it
def test():
    'Shows how this works'
    path = 'input3.yaml'
    with open(path, 'r') as fobj:
        ans = yaml.load(fobj)
    order1 = ans['order']
    puzzle1 = ans['puzzle']
    with open('solution.yaml', 'r') as fobj:
        ans = yaml.load(fobj)
    solution1 = ans['solution']
    if order1 == 4:
        labels = ['X', 
                  '0', '1', '2', '3',
                  '4', '5', '6', '7',
                  '8', '9', 'A', 'B',
                  'C', 'D', 'E', 'F']
    else:
        labels = ['X', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    draw_sudoku(puzzle1, solution1, order1, labels)

if __name__ == '__main__':
    test()
