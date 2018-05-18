import {sprintf} from 'sprintf-js'
export declare type BCASTER = (bcaster: number[]) => void

export class Link {
    left: Link;
    right: Link;
    up: Link;
    down: Link;
    // id: number;
    // static next_id : number = 0 // for debugging
    // static links : Link[] = []  // for debugging

    constructor() {
        this.left = this
        this.right = this
        this.up = this
        this.down = this
        // this.id = Link.next_id  // for debugging
        // Link.links.push(this)   // for debugging
        // Link.next_id += 1
    }

    insert_left(other: Link) : void {
        other.left = this.left
        other.right = this
        this.left.right = other
        this.left = other
    }

    insert_above(other: Link) : void {
        other.down = this
        other.up = this.up
        this.up.down = other
        this.up = other
    }

    iter_down(f: (Link) => void): void {
        let link = this.down
        while (link != this) {
            f(link)
            link = link.down
        }
    }

    iter_up(f: (Link) => void): void {
        let link = this.up
        while (link != this) {
            f(link)
            link = link.up
        }
    }

    iter_right(f: (Link) => void): void {
        let link = this.right
        while (link != this) {
            f(link)
            link = link.right
        }
    }

    iter_left(f: (Link) => void): void {
        let link = this.left
        while (link != this) {
            f(link)
            link = link.left
        }
    }
}

export class Bit extends Link {
    column: Column
    constructor(column:Column) {
        super()
        this.column = column
    }

    // repr() : string {
    //     let fmt = "%4d    B   %4d  %4d  %4d  %4d  %4d     *"
    //     return sprintf(fmt, this.id, this.left.id, this.right.id,
    //                         this.up.id, this.down.id, this.column.id)
    // }
    
}

export class Column extends Link {
    index: number
    size: number

    constructor(index: number) {
        super()
        this.index = index
        this.size = 0
    }

    cover(): void {
        this.right.left = this.left
        this.left.right = this.right
        this.iter_down(
            colLink => {
                colLink.iter_right(
                    rowLink => {
                        rowLink.down.up = rowLink.up;
                        rowLink.up.down = rowLink.down;
                        ((<Bit>rowLink).column).size -= 1
                    }
                )
            }
        )
    }

    uncover(): void {
        this.iter_up(
            colLink => {
                colLink.iter_left(
                    rowLink => {
                        let bit = <Bit>rowLink
                        bit.column.size += 1
                        bit.up.down = bit.down.up = bit
                    }
                )
            }
        )
        this.right.left = this
        this.left.right = this
    }

    // repr() : string {
    //     let fmt = "%4d    C   %4d  %4d  %4d  %4d  %4d  %4d"
    //     return sprintf(fmt, this.id, this.left.id, this.right.id,
    //                    this.up.id, this.down.id, this.index, this.size)
    // }
    
}

export class Root extends Link {
    readonly MAX_OHS_COUNT = 100000

    constructor(column_count: number, set_bits: number[][]) {
        super()
        let columns: Column[] = []
        for (let index = 0; index < column_count; index++) {
            let column = new Column(index)
            this.insert_left(column)
            columns.push(column)
        }
        for (let row of set_bits) {
            let bit0:Bit = null
            for (let i of row) {
                let column = columns[i]
                let bit = new Bit(column)
                column.insert_above(bit)
                column.size += 1
                if (bit0) 
                    bit0.insert_left(bit)
                else 
                    bit0 = bit
            }
        }
    }

    private choose(): Column {
        let smallest_size = 1000000
        let ans: Column = null
        let link = this.right
        while (link != this) {
            let column = <Column>link
            if (column.size < smallest_size) {
                ans = column
                smallest_size = column.size
            }
            link = link.right
        }
        return ans
    }

    private static bcast_column_names(bits: Bit[], bcaster: BCASTER): void {
        for (let bit0 of bits) {
            let ans = [bit0.column.index]
            bit0.iter_right(link => {ans.push((<Bit>link).column.index)})
            bcaster(ans)
        }
    }

    private privateSearch(k: number, ohs: Bit[], bcaster: BCASTER): void {
        if (this.right == this) {
            Root.bcast_column_names(ohs.slice(0,k), bcaster)
            return
        }
        let column = this.choose()
        column.cover()

        column.iter_down(
            link0 => {
                ohs[k] = <Bit>link0
                link0.iter_right(
                    link1 => {
                        (<Bit>link1).column.cover()
                    }
                )
                this.privateSearch(k + 1, ohs, bcaster)
                let bit2 = ohs[k]
                column = bit2.column
                bit2.iter_left(
                    link2 => {
                        (<Bit>link2).column.uncover()
                    }
                )
            }
        )
        column.uncover()
    }

    search(bcaster: BCASTER): void {
        let ohs:Bit[] = new Array(this.MAX_OHS_COUNT)
        this.privateSearch(0, ohs, bcaster)
    }

    iter_columns(f: (Column) => void): void {
        let column = this.right
        while (column != this) {
            f(column)
            column = column.right
        }
    }

    // repr() : string {
    //     let fmt = "%4d    R   %4d  %4d  %4d  %4d     *     *"
    //     return sprintf(fmt, this.id, this.left.id, this.right.id,
    //                         this.up.id, this.down.id)
    // }
    
}
