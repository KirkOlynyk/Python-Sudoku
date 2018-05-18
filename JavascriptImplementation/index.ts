import * as DLX from './dlx'

const column_count = 7
const setBits = [
    [2, 4, 5],
    [0, 3, 6],
    [1, 2, 5],
    [0, 3],
    [1, 6],
    [3, 4, 6]
]
let root = new DLX.Root(column_count, setBits)
root.search(indexes => { console.log(indexes.sort()) })
