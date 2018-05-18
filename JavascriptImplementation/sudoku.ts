import * as fs from 'fs'
import * as dlx from './dlx'
import {sprintf} from 'sprintf-js'
import 'process'
import * as argparse from 'argparse'

function get_dict(symbols: string){
    if (symbols == null)
        return null
    let ans = {}
    for (let i = 0; i < symbols.length; i++)
        ans[symbols[i]] = i
    return ans
}

let alphabets = [
    null, 
    null, 
    ".1234",
    ".123456789",
    ".0123456789ABCDEF",
    ".ABCDEFGHIJKLMNOPQRSTUVWXY",
    ".0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ]
let dicts = alphabets.map(get_dict)

function get_zero_row(dict: {}, dot_row: string): number[] {
    let ans = []
    for (let ch of dot_row)
        ans.push(dict[ch])
    return ans
}

class Sudoku {
    N: number
    N2: number
    N4: number
    M: number   // number of columns in the DLX matrix
    N6: number
    constructor(order: number) {
        this.N = order
        this.N2 = order * order
        this.N4 = this.N2 * this.N2
        this.M = 4 * this.N4
        this.N6 = this.N2 * this.N4
    }

    get_iBox(iR: number, iC: number): number {
        return  Math.floor(iC / this.N) + this.N * Math.floor(iR / this.N)
    }

    get_bit_column_row_ex(iV: number, iR: number, iC: number): number[] {
        let iB = this.get_iBox(iR, iC)
        let jE = iC + this.N2 * iR
        let jR = iV + this.N2 * (iR + this.N2 * 1)
        let jC = iV + this.N2 * (iC + this.N2 * 2)
        let jB = iV + this.N2 * (iB + this.N2 * 3)
        return [jE, jR, jC, jB]
    }

    get_ivrc(iX: number): number[] {
        let iR = Math.floor(iX / this.N4)
        let rem = iX - this.N4 * iR
        let iC = Math.floor(rem / this.N2)
        let iV = rem - this.N2 * iC
        return [iV, iR, iC]
    }

    get_bit_column_row(iX: number): number[] {
        let ivrc = this.get_ivrc(iX)
        return this.get_bit_column_row_ex(ivrc[0], ivrc[1], ivrc[2])
    }

    get_set_bits(): number[][] {
        let ans = new Array(this.N6)
        for (let iX = 0; iX < this.N6; iX++)
            ans[iX] = this.get_bit_column_row(iX)
        return ans
    }
}

function set_initial_state(root: dlx.Root,
                           zero_rows: number[][],
                           sudoku: Sudoku): void {
    for (let iR = 0; iR < zero_rows.length; iR++){
        let row = zero_rows[iR]
        for (let iC = 0; iC < row.length; iC++) {
            let iV = row[iC] - 1
            if (iV < 0)
                continue
            let column_indices = sudoku.get_bit_column_row_ex(iV, iR, iC)
            for (let column_index of column_indices) {
                root.iter_columns(
                    (column: dlx.Column) => {
                        if (column.index == column_index) {
                            column.cover()
                        }
                    }
                )
            }
        }
    }
}

function checkZeroMatrix(zeroMatrix: number[][]) {
    let N2: number = zeroMatrix.length
    let N = Math.sqrt(N2)
    console.assert(N2 == N*N, "Not and exact square")
    for (let row of zeroMatrix)
        console.assert(row.length == N2, "invalid row length")
    checkRows()
    checkCols()
    checkBoxes()

    function checkRows() {
        for (let iR = 0; iR < N2; iR++)
            checkRow(iR);

        function checkRow(iR: number) {
            let counts: number[] = new Array(N2+1).fill(0)
            for (let iC = 0; iC < N2; iC++) {
                let iV = zeroMatrix[iR][iC];
                counts[iV] += 1;
            }
            for (let iV = 1; iV < N2; iV++)
                console.assert(counts[iV] <= 1, sprintf("row %d", iR));
        }
    }
    function checkCols() {
        for (let iC = 0; iC < N2; iC++)
            checkCol(iC);

        function checkCol(iC: number) {
            let counts: number[] = new Array(N2+1).fill(0)
            for (let iR = 0; iR < N2; iR++) {
                let iV = zeroMatrix[iR][iC];
                counts[iV] += 1;
            }
            for (let iV = 1; iV < N2; iV++)
                console.assert(counts[iV] <= 1, sprintf("col %d", iC));
        }
    }
    function checkBoxes() {
        for (let iB = 0; iB < N2; iB++)
            checkBox(iB)

        function checkBox(iB: number) {
            let counts: number[] = new Array(N2+1).fill(0)
            let qR = Math.floor(iB / N)
            let qC = iB - N * qR
            for (let iR = N*qR; iR < N*(qR+1); iR++)
                for (let iC = N*qC; iC < N*(qC+1); iC++)
                    counts[zeroMatrix[iR][iC]] += 1
            for (let iV = 1; iV < N2; iV++)
                console.assert(counts[iV] <= 1, sprintf("box %d", iB));
        }
    }
}

function process_json_string(json_string: string, puzzle: number): void {
    let puzzles= JSON.parse(json_string)
    let dot_rows = puzzles[puzzle]['dot_rows']
    if (puzzles[puzzle]['comments']) {
        for (let comment of puzzles[puzzle]['comments'])
            console.log(comment)
    }
    let order = Math.floor(Math.sqrt(dot_rows.length))
    let dict = dicts[order]
    let alphabet = alphabets[order]
    let zero_rows = getZeroRowArray();
    checkZeroMatrix(zero_rows)
    let sudoku = new Sudoku(order)
    let set_bits = sudoku.get_set_bits()
    let root = new dlx.Root(sudoku.M, set_bits)
    set_initial_state(root, zero_rows, sudoku)
    let solution: number[][] = getEmptySolution();
    root.search(bcaster)
    unionZeroRowsToSolution();
    printSolution();

    function getZeroRowArray() {
        let zero_rows = [];
        for (let dot_row of dot_rows)
            zero_rows.push(get_zero_row(dict, dot_row));
        return zero_rows;
    }

    function getEmptySolution() {
        let solution: number[][] = new Array(sudoku.N2);
        for (let i = 0; i < sudoku.N2; i++) {
            solution[i] = new Array(sudoku.N2);
            for (let j = 0; j < sudoku.N2; j++)
                solution[i][j] = 0;
        }
        return solution;
    }

    function bcaster(indices: number[]) {
        indices.sort((a,b) => a - b)
        let jE = indices[0]
        let jR = indices[1]
        let iR = Math.floor(jE / sudoku.N2)
        let iC = jE - sudoku.N2 * iR
        let iV = jR - sudoku.N2 * (iR + sudoku.N2)
        solution[iR][iC] = iV + 1
    }

    function printSolution() {
        for (let row of solution) {
            let row1 = row.map(x => alphabet[x])
            console.log(row1.join(""));
        }
    }

    function unionZeroRowsToSolution() {
        for (let iR = 0; iR < sudoku.N2; iR++) {
            for (let iC = 0; iC < sudoku.N2; iC++) {
                let iV = zero_rows[iR][iC];
                if (iV != 0)
                    solution[iR][iC] = iV;
            }
        }
    }
}

function main1(path: string, puzzle: number) {
    fs.readFile(path, 'utf8', 
        function (err, data) {
            if (err)
                console.log(err)
            else
                process_json_string(data, puzzle)
        }
    )
}

function main() {
    let parser = new argparse.ArgumentParser({version: '0.0.1', addHelp:true, description: 'Sudoku solver'})
    parser.addArgument([ '-path', '--path'], { help: 'path input.json'})
    parser.addArgument(['-puzzle', '--puzzle'], { help: 'puzzle 0'})
    let args = parser.parseArgs();
    main1(args.path, Number(args.puzzle))
}

main()
