<template>
    <table class="store-map-legend">
        <tr v-if="editable" class="store-map-legend-item" :class="{'active': isActive(null)}">
            <td class="store-map-legend-tile store-map-legend-tile-cursor" @click="activateEntry(null)"></td>
            <td class="store-map-legend-title" @click="activateEntry(null)">{{ getText("Cursor (no changes)") }}</td>
        </tr>
        <tbody v-for="entry in entries" :key="entry.key">
            <tr class="store-map-legend-item" :class="{'active': isActive(entry)}">
            <td class="store-map-legend-tile" v-if="isSubaisle(entry) || isSpecialTile(entry)"
                @click="activateEntry(entry)" :style="getColorCSSForEntry(entry)"></td>
            <td class="store-map-legend-tile-blank" v-else-if="!isSectionHeader(entry) && !isAisle(entry)"></td>
            <td v-if="isSectionHeader(entry)" class="h5" colspan="2">{{ entry.title }}</td>
            <td v-else-if="isAisle(entry)" class="h6" colspan="2">{{ entry.title }}</td>
            <td v-else @click="activateEntry(entry)" class="store-map-legend-title">{{ entry.title }}</td>
            </tr>
            <tr v-if="isAisle(entry) || isSectionHeader(entry)"></tr>
        </tbody>
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
    buildLegend,
    ColorSpec,
    getColorCSS,
    LegendEntry,
    LegendEntryType,
} from "@/components/store-map/tile-legend-coloring";
import {AisleStructureEntry} from "@/defs/map-locations-defs";

// noinspection JSMethodCanBeStatic
@Component
export default class MapLegend extends Vue {
    @Prop() private aisles!: AisleStructureEntry[];
    @Prop() private colors!: Map<number, ColorSpec>;
    @Prop() private editable!: boolean;
    private activeEntry: LegendEntry | null = null;
    private entries: LegendEntry[] = [];

    mounted() {
        this.updateEntries();
    }

    @Watch("aisles")
    @Watch("colors")
    private updateEntries() {
        this.entries = buildLegend(this.aisles, this.colors);
    }

    private getColorCSSForEntry(entry: LegendEntry): string {
        return entry.color === null ? "" : getColorCSS(entry.color);
    }

    private isSectionHeader(entry: LegendEntry): boolean {
        return entry.type === LegendEntryType.SECTION_HEADER;
    }

    private isAisle(entry: LegendEntry): boolean {
        return entry.type === LegendEntryType.AISLE;
    }

    private isSubaisle(entry: LegendEntry): boolean {
        return entry.type === LegendEntryType.SUBAISLE;
    }

    private isSpecialTile(entry: LegendEntry): boolean {
        return entry.type === LegendEntryType.SPECIAL_TILE;
    }

    private isActive(entry: LegendEntry | null): boolean {
        return this.editable && entry?.key === this.activeEntry?.key;
    }

    private activateEntry(entry: LegendEntry | null) {
        if (entry === undefined || (entry !== null && !entry.canActivate)) return;
        this.activeEntry = entry;
        this.$emit("activateEntry", entry);
    }
}
</script>

<style scoped>

</style>
