<template>
    <div>
        <MapDisplayWithLegend :map="map" :aisles="appData.aisles" :editable="false" :showTooltips="true" :size="size"></MapDisplayWithLegend>
        <div class="form-inline justify-content-end">
            <label for="zoom-map" class="mr-1">{{ getText("Zoom:") }}</label>
            <select id="zoom-map" class="form-control" v-model="size">
                <option value="small">S</option>
                <option value="regular">M</option>
                <option value="large">L</option>
            </select>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop, Vue} from "vue-property-decorator";
import {AppDataMSD, StoreMap} from "@/components/store-map/storemap-defs";

@Component
export default class MapStaticDisplayApp extends Vue {
    @Prop() private appData!: AppDataMSD;
    private map: StoreMap = new StoreMap(null, 0, 0, []);
    private size: string = "regular";

    mounted() {
        this.map = StoreMap.fromDTOs(this.appData.map, this.appData.tiles);
    }
}
</script>

<style scoped>

</style>
