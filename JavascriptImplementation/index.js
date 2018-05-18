"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DLX = require("./dlx");
var column_count = 7;
var setBits = [
    [2, 4, 5],
    [0, 3, 6],
    [1, 2, 5],
    [0, 3],
    [1, 6],
    [3, 4, 6]
];
var root = new DLX.Root(column_count, setBits);
root.search(function (indexes) { console.log(indexes.sort()); });
