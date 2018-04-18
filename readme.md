# Solving Sudoku puzzles in Python

To solve the Sudoku puzzle I convert the puzzle to an exact cover
problem and then solve that with 
[Knuth's Dancing Links algorithm](https://arxiv.org/abs/cs/0011047).

To demonstrate how it works just type
```
python .\sudoku.py --input .\input.yaml --puzzle 0
```

To see how Sudoku puzzles are represented look at the examples in input.yaml.