<template>
    <table class="store-map" :class="'store-map-' + this.size">
        <thead>
        <tr>
            <th></th>
            <th v-for="(n, i) in map.width" :key="i">{{ getColumnLetter(i) }}</th>
        </tr>
        </thead>
        <tr v-for="(row, index) in tileRows" :key="row.y">
            <th>{{ index + 1 }}</th>
            <td v-for="tile in row.tiles" :key="tile.x" :title="showTooltips ? getTitle(tile) : null"
                 @click="registerClick(tile)" :style="getColorCSS(colors, tile)">{{ tile.key }}</td>
        </tr>
    </table>
</template>

<script lang="ts">
import {
    Component,
    Prop,
    Vue,
    Watch,
} from "vue-property-decorator";
import {
    columnLetter,
    getTileTypeName,
    MapTile,
    MapTileRow, sortedMapTiles,
    StoreMap,
} from "@/components/store-map/storemap-defs";
import {
    ColorSpec,
    getColorCSSForTile,
} from "@/components/store-map/tile-legend-coloring";

@Component
export default class MapDisplay extends Vue {
    @Prop() private map!: StoreMap;
    @Prop() private colors!: Map<number, ColorSpec>;
    @Prop() private editable!: boolean;
    @Prop() private showTooltips!: boolean;
    @Prop({default: "regular"}) private size!: string;
    public tileRows: MapTileRow[] = [];

    mounted() {
        this.updateRows();
    }

    @Watch("map")
    public updateRows() {
        this.tileRows = [];
        for (let i = 0; i < this.map.height; i += 1) {
            this.tileRows.push(new MapTileRow(i));
        }
        const sortedTiles = sortedMapTiles(this.map.tiles);
        sortedTiles.forEach((tile: MapTile) => this.tileRows[tile.y].tiles.push(tile));
    }

    private getTitle(tile: MapTile) {
        let desc;
        if (tile.subaisle !== null) {
            desc = tile.subaisle.name;
            if (tile.subaisle.display_code) {
                desc += ` (${tile.subaisle.display_code})`;
            }
        } else {
            desc = getTileTypeName(tile.tileType);
        }
        return `${tile.letterCoords}: ${desc}`;
    }

    private registerClick(tile: MapTile) {
        this.$emit("tileClicked", tile);
    }

    // noinspection JSMethodCanBeStatic
    private getColumnLetter(x: number): string {
        return columnLetter(x);
    }

    // noinspection JSMethodCanBeStatic
    private getColorCSS(colors: Map<number, ColorSpec>, tile: MapTile): string {
        if (this.colors.size > 0) {
            return getColorCSSForTile(colors, tile);
        }
        return "background-color:gray";
    }
}
</script>

<style scoped>

</style>
