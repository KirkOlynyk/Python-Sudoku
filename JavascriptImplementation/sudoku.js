"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var fs = require("fs");
var dlx = require("./dlx");
var sprintf_js_1 = require("sprintf-js");
require("process");
var argparse = require("argparse");
function get_dict(symbols) {
    if (symbols == null)
        return null;
    var ans = {};
    for (var i = 0; i < symbols.length; i++)
        ans[symbols[i]] = i;
    return ans;
}
var alphabets = [
    null,
    null,
    ".1234",
    ".123456789",
    ".0123456789ABCDEF",
    ".ABCDEFGHIJKLMNOPQRSTUVWXY",
    ".0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
];
var dicts = alphabets.map(get_dict);
function get_zero_row(dict, dot_row) {
    var ans = [];
    for (var _i = 0, dot_row_1 = dot_row; _i < dot_row_1.length; _i++) {
        var ch = dot_row_1[_i];
        ans.push(dict[ch]);
    }
    return ans;
}
var Sudoku = /** @class */ (function () {
    function Sudoku(order) {
        this.N = order;
        this.N2 = order * order;
        this.N4 = this.N2 * this.N2;
        this.M = 4 * this.N4;
        this.N6 = this.N2 * this.N4;
    }
    Sudoku.prototype.get_iBox = function (iR, iC) {
        return Math.floor(iC / this.N) + this.N * Math.floor(iR / this.N);
    };
    Sudoku.prototype.get_bit_column_row_ex = function (iV, iR, iC) {
        var iB = this.get_iBox(iR, iC);
        var jE = iC + this.N2 * iR;
        var jR = iV + this.N2 * (iR + this.N2 * 1);
        var jC = iV + this.N2 * (iC + this.N2 * 2);
        var jB = iV + this.N2 * (iB + this.N2 * 3);
        return [jE, jR, jC, jB];
    };
    Sudoku.prototype.get_ivrc = function (iX) {
        var iR = Math.floor(iX / this.N4);
        var rem = iX - this.N4 * iR;
        var iC = Math.floor(rem / this.N2);
        var iV = rem - this.N2 * iC;
        return [iV, iR, iC];
    };
    Sudoku.prototype.get_bit_column_row = function (iX) {
        var ivrc = this.get_ivrc(iX);
        return this.get_bit_column_row_ex(ivrc[0], ivrc[1], ivrc[2]);
    };
    Sudoku.prototype.get_set_bits = function () {
        var ans = new Array(this.N6);
        for (var iX = 0; iX < this.N6; iX++)
            ans[iX] = this.get_bit_column_row(iX);
        return ans;
    };
    return Sudoku;
}());
function set_initial_state(root, zero_rows, sudoku) {
    for (var iR = 0; iR < zero_rows.length; iR++) {
        var row = zero_rows[iR];
        for (var iC = 0; iC < row.length; iC++) {
            var iV = row[iC] - 1;
            if (iV < 0)
                continue;
            var column_indices = sudoku.get_bit_column_row_ex(iV, iR, iC);
            var _loop_1 = function (column_index) {
                root.iter_columns(function (column) {
                    if (column.index == column_index) {
                        column.cover();
                    }
                });
            };
            for (var _i = 0, column_indices_1 = column_indices; _i < column_indices_1.length; _i++) {
                var column_index = column_indices_1[_i];
                _loop_1(column_index);
            }
        }
    }
}
function checkZeroMatrix(zeroMatrix) {
    var N2 = zeroMatrix.length;
    var N = Math.sqrt(N2);
    console.assert(N2 == N * N, "Not and exact square");
    for (var _i = 0, zeroMatrix_1 = zeroMatrix; _i < zeroMatrix_1.length; _i++) {
        var row = zeroMatrix_1[_i];
        console.assert(row.length == N2, "invalid row length");
    }
    checkRows();
    checkCols();
    checkBoxes();
    function checkRows() {
        for (var iR = 0; iR < N2; iR++)
            checkRow(iR);
        function checkRow(iR) {
            var counts = new Array(N2 + 1).fill(0);
            for (var iC = 0; iC < N2; iC++) {
                var iV = zeroMatrix[iR][iC];
                counts[iV] += 1;
            }
            for (var iV = 1; iV < N2; iV++)
                console.assert(counts[iV] <= 1, sprintf_js_1.sprintf("row %d", iR));
        }
    }
    function checkCols() {
        for (var iC = 0; iC < N2; iC++)
            checkCol(iC);
        function checkCol(iC) {
            var counts = new Array(N2 + 1).fill(0);
            for (var iR = 0; iR < N2; iR++) {
                var iV = zeroMatrix[iR][iC];
                counts[iV] += 1;
            }
            for (var iV = 1; iV < N2; iV++)
                console.assert(counts[iV] <= 1, sprintf_js_1.sprintf("col %d", iC));
        }
    }
    function checkBoxes() {
        for (var iB = 0; iB < N2; iB++)
            checkBox(iB);
        function checkBox(iB) {
            var counts = new Array(N2 + 1).fill(0);
            var qR = Math.floor(iB / N);
            var qC = iB - N * qR;
            for (var iR = N * qR; iR < N * (qR + 1); iR++)
                for (var iC = N * qC; iC < N * (qC + 1); iC++)
                    counts[zeroMatrix[iR][iC]] += 1;
            for (var iV = 1; iV < N2; iV++)
                console.assert(counts[iV] <= 1, sprintf_js_1.sprintf("box %d", iB));
        }
    }
}
function process_json_string(json_string, puzzle) {
    var puzzles = JSON.parse(json_string);
    var dot_rows = puzzles[puzzle]['dot_rows'];
    if (puzzles[puzzle]['comments']) {
        for (var _i = 0, _a = puzzles[puzzle]['comments']; _i < _a.length; _i++) {
            var comment = _a[_i];
            console.log(comment);
        }
    }
    var order = Math.floor(Math.sqrt(dot_rows.length));
    var dict = dicts[order];
    var alphabet = alphabets[order];
    var zero_rows = getZeroRowArray();
    checkZeroMatrix(zero_rows);
    var sudoku = new Sudoku(order);
    var set_bits = sudoku.get_set_bits();
    var root = new dlx.Root(sudoku.M, set_bits);
    set_initial_state(root, zero_rows, sudoku);
    var solution = getEmptySolution();
    root.search(bcaster);
    unionZeroRowsToSolution();
    printSolution();
    function getZeroRowArray() {
        var zero_rows = [];
        for (var _i = 0, dot_rows_1 = dot_rows; _i < dot_rows_1.length; _i++) {
            var dot_row = dot_rows_1[_i];
            zero_rows.push(get_zero_row(dict, dot_row));
        }
        return zero_rows;
    }
    function getEmptySolution() {
        var solution = new Array(sudoku.N2);
        for (var i = 0; i < sudoku.N2; i++) {
            solution[i] = new Array(sudoku.N2);
            for (var j = 0; j < sudoku.N2; j++)
                solution[i][j] = 0;
        }
        return solution;
    }
    function bcaster(indices) {
        indices.sort(function (a, b) { return a - b; });
        var jE = indices[0];
        var jR = indices[1];
        var iR = Math.floor(jE / sudoku.N2);
        var iC = jE - sudoku.N2 * iR;
        var iV = jR - sudoku.N2 * (iR + sudoku.N2);
        solution[iR][iC] = iV + 1;
    }
    function printSolution() {
        for (var _i = 0, solution_1 = solution; _i < solution_1.length; _i++) {
            var row = solution_1[_i];
            var row1 = row.map(function (x) { return alphabet[x]; });
            console.log(row1.join(""));
        }
    }
    function unionZeroRowsToSolution() {
        for (var iR = 0; iR < sudoku.N2; iR++) {
            for (var iC = 0; iC < sudoku.N2; iC++) {
                var iV = zero_rows[iR][iC];
                if (iV != 0)
                    solution[iR][iC] = iV;
            }
        }
    }
}
function main1(path, puzzle) {
    fs.readFile(path, 'utf8', function (err, data) {
        if (err)
            console.log(err);
        else
            process_json_string(data, puzzle);
    });
}
function main() {
    var parser = new argparse.ArgumentParser({ version: '0.0.1', addHelp: true, description: 'Sudoku solver' });
    parser.addArgument(['-path', '--path'], { help: 'path input.json' });
    parser.addArgument(['-puzzle', '--puzzle'], { help: 'puzzle 0' });
    var args = parser.parseArgs();
    main1(args.path, Number(args.puzzle));
}
main();
