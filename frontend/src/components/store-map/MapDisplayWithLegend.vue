<template>
    <div class="row">
        <div class="col-md-8"><MapDisplay ref="display"
            :map="map" :colors="colors" :editable="editable"
            :showTooltips="showTooltips" :size="size" @tileClicked="paintTile"></MapDisplay>
        </div>
        <div class="col-md-4">
            <MapLegend :aisles="aisles" :colors="colors" :editable="editable"
                       @activateEntry="activateEntry"></MapLegend>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop, Vue} from "vue-property-decorator";
import {
    MapTile,
    MapTileRow,
    StoreMap,
    TileType,
} from "@/components/store-map/storemap-defs";
import {AisleStructureEntry} from "@/defs/map-locations-defs";
import {
    buildColorMap,
    ColorSpec,
    LegendEntry,
    LegendEntryType,
} from "@/components/store-map/tile-legend-coloring";
import MapDisplay from "@/components/store-map/MapDisplay.vue";

@Component
export default class MapDisplayWithLegend extends Vue {
    @Prop() private map!: StoreMap;
    @Prop() private aisles!: AisleStructureEntry[];
    @Prop() private editable!: boolean;
    @Prop() private showTooltips!: boolean;
    @Prop({default: "regular"}) private size!: string;
    private activeEntry: LegendEntry | null = null;
    public colors: Map<number, ColorSpec> = new Map();

    mounted() {
        this.updateColors();
    }

    public getRows(): MapTileRow[] {
        // @ts-ignore This is always a reference to MapDisplay
        // eslint-disable-next-line prefer-destructuring
        const display: MapDisplay = this.$refs.display;
        return display.tileRows;
    }

    public updateRows() {
        // @ts-ignore This is always a reference to MapDisplay
        // eslint-disable-next-line prefer-destructuring
        const display: MapDisplay = this.$refs.display;
        display.updateRows();
    }

    public updateColors(aisles: AisleStructureEntry[] | null = null) {
        this.colors = buildColorMap(aisles || this.aisles);
    }

    private activateEntry(entry: LegendEntry | null) {
        this.activeEntry = entry;
    }

    private paintTile(tile: MapTile) {
        if (!this.editable) {
            this.$emit("tileClicked", tile); // bubble event only if not editable
        }
        if (this.activeEntry === null || !this.editable) {
            return;
        }
        if (this.activeEntry.type === LegendEntryType.SUBAISLE) {
            tile.tileType = TileType.SUBAISLE;
            tile.subaisle = this.activeEntry.subaisle;
        } else if (this.activeEntry.type === LegendEntryType.SPECIAL_TILE && this.activeEntry.tileType !== null) {
            tile.tileType = this.activeEntry.tileType;
            tile.subaisle = null;
        }
    }
}
</script>

<style scoped>

</style>
