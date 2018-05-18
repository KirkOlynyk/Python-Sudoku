"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
var Link = /** @class */ (function () {
    // id: number;
    // static next_id : number = 0 // for debugging
    // static links : Link[] = []  // for debugging
    function Link() {
        this.left = this;
        this.right = this;
        this.up = this;
        this.down = this;
        // this.id = Link.next_id  // for debugging
        // Link.links.push(this)   // for debugging
        // Link.next_id += 1
    }
    Link.prototype.insert_left = function (other) {
        other.left = this.left;
        other.right = this;
        this.left.right = other;
        this.left = other;
    };
    Link.prototype.insert_above = function (other) {
        other.down = this;
        other.up = this.up;
        this.up.down = other;
        this.up = other;
    };
    Link.prototype.iter_down = function (f) {
        var link = this.down;
        while (link != this) {
            f(link);
            link = link.down;
        }
    };
    Link.prototype.iter_up = function (f) {
        var link = this.up;
        while (link != this) {
            f(link);
            link = link.up;
        }
    };
    Link.prototype.iter_right = function (f) {
        var link = this.right;
        while (link != this) {
            f(link);
            link = link.right;
        }
    };
    Link.prototype.iter_left = function (f) {
        var link = this.left;
        while (link != this) {
            f(link);
            link = link.left;
        }
    };
    return Link;
}());
exports.Link = Link;
var Bit = /** @class */ (function (_super) {
    __extends(Bit, _super);
    function Bit(column) {
        var _this = _super.call(this) || this;
        _this.column = column;
        return _this;
    }
    return Bit;
}(Link));
exports.Bit = Bit;
var Column = /** @class */ (function (_super) {
    __extends(Column, _super);
    function Column(index) {
        var _this = _super.call(this) || this;
        _this.index = index;
        _this.size = 0;
        return _this;
    }
    Column.prototype.cover = function () {
        this.right.left = this.left;
        this.left.right = this.right;
        this.iter_down(function (colLink) {
            colLink.iter_right(function (rowLink) {
                rowLink.down.up = rowLink.up;
                rowLink.up.down = rowLink.down;
                (rowLink.column).size -= 1;
            });
        });
    };
    Column.prototype.uncover = function () {
        this.iter_up(function (colLink) {
            colLink.iter_left(function (rowLink) {
                var bit = rowLink;
                bit.column.size += 1;
                bit.up.down = bit.down.up = bit;
            });
        });
        this.right.left = this;
        this.left.right = this;
    };
    return Column;
}(Link));
exports.Column = Column;
var Root = /** @class */ (function (_super) {
    __extends(Root, _super);
    function Root(column_count, set_bits) {
        var _this = _super.call(this) || this;
        _this.MAX_OHS_COUNT = 100000;
        var columns = [];
        for (var index = 0; index < column_count; index++) {
            var column = new Column(index);
            _this.insert_left(column);
            columns.push(column);
        }
        for (var _i = 0, set_bits_1 = set_bits; _i < set_bits_1.length; _i++) {
            var row = set_bits_1[_i];
            var bit0 = null;
            for (var _a = 0, row_1 = row; _a < row_1.length; _a++) {
                var i = row_1[_a];
                var column = columns[i];
                var bit = new Bit(column);
                column.insert_above(bit);
                column.size += 1;
                if (bit0)
                    bit0.insert_left(bit);
                else
                    bit0 = bit;
            }
        }
        return _this;
    }
    Root.prototype.choose = function () {
        var smallest_size = 1000000;
        var ans = null;
        var link = this.right;
        while (link != this) {
            var column = link;
            if (column.size < smallest_size) {
                ans = column;
                smallest_size = column.size;
            }
            link = link.right;
        }
        return ans;
    };
    Root.bcast_column_names = function (bits, bcaster) {
        var _loop_1 = function (bit0) {
            var ans = [bit0.column.index];
            bit0.iter_right(function (link) { ans.push(link.column.index); });
            bcaster(ans);
        };
        for (var _i = 0, bits_1 = bits; _i < bits_1.length; _i++) {
            var bit0 = bits_1[_i];
            _loop_1(bit0);
        }
    };
    Root.prototype.privateSearch = function (k, ohs, bcaster) {
        var _this = this;
        if (this.right == this) {
            Root.bcast_column_names(ohs.slice(0, k), bcaster);
            return;
        }
        var column = this.choose();
        column.cover();
        column.iter_down(function (link0) {
            ohs[k] = link0;
            link0.iter_right(function (link1) {
                link1.column.cover();
            });
            _this.privateSearch(k + 1, ohs, bcaster);
            var bit2 = ohs[k];
            column = bit2.column;
            bit2.iter_left(function (link2) {
                link2.column.uncover();
            });
        });
        column.uncover();
    };
    Root.prototype.search = function (bcaster) {
        var ohs = new Array(this.MAX_OHS_COUNT);
        this.privateSearch(0, ohs, bcaster);
    };
    Root.prototype.iter_columns = function (f) {
        var column = this.right;
        while (column != this) {
            f(column);
            column = column.right;
        }
    };
    return Root;
}(Link));
exports.Root = Root;
