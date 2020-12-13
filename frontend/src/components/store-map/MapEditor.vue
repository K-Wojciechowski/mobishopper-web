<template>
    <div>
        <MapDisplayWithLegend class="mb-2" :map="map" :aisles="aisles" :size="size"
                              :editable="true" :showTooltips="true" ref="display"></MapDisplayWithLegend>

        <MessageDisplay ref="messages"></MessageDisplay>

        <div class="card-box card-box-bottom">
            <div class="form-inline justify-content-center">
                <div class="d-flex flex-column">
                    <label for="valid-at-field">{{ getText("Changes in effect after:" )}}</label>

                    <div class="input-group date">
                        <input type="text" name="date_started" class="form-control"
                               :placeholder="getText('Valid from')" title=""
                               v-model="validAt" id="valid-at-field"
                               dp_config="{&quot;id&quot;: &quot;dp_1&quot;, &quot;picker_type&quot;:
&quot;DATETIME&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true,
&quot;showClear&quot;: false, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;YYYY-MM-DD HH:mm:ss&quot;}}">
                        <div class="input-group-addon input-group-append" data-target="#datetimepicker1"
                             data-toggle="datetimepickerv">
                            <div class="input-group-text"><i class="glyphicon glyphicon-calendar"></i></div>
                        </div>
                    </div>
                </div>

                <div class="d-flex flex-column ml-2">
                    <label for="zoom-map">{{ getText("Zoom:") }}</label>
                    <select id="zoom-map" class="form-control" v-model="size">
                        <option value="small">S</option>
                        <option value="regular">M</option>
                        <option value="large">L</option>
                    </select>
                </div>

                <div class="d-flex flex-column ml-2">
                    <label for="resizew">{{ getText("Resize the map:") }}</label>
                    <div class="d-flex flex-row">
                        <input type="number" class="form-control" style="width:5rem"
                               id="resizew" v-model.number="resizeW">
                        <label for="resizeh">×</label>
                        <input type="number" class="form-control" style="width:5rem"
                               id="resizeh" v-model.number="resizeH">
                        <button type="button" class="btn btn-outline-warning ml-2"
                                @click="resizeMap">{{ getText("Resize") }}</button>
                    </div>
                </div>

                <div class="vertical-divider ml-3 pl-3 d-flex align-items-center">
                    <button type="button" class="btn btn-lg btn-success" @click="saveChanges()">
                        <IconBox icon="check" size="16" :text="getText('Save')"></IconBox>
                    </button>
                </div>
            </div>
        </div>

        <div class="alert alert-secondary mt-1" v-if="showLoading > 0">
            <IconBox size="16" icon="hourglass-split" :text="getText('Loading…')"></IconBox>
        </div>
    </div>
</template>

<script lang="ts">
import {
    Component,
    Prop,
    Vue,
    Watch,
} from "vue-property-decorator";
import {
    AppDataSME,
    MapTile,
    StoreMap,
    TileType,
    MapTileRow,
    saveMap, MapSaveResponse,
} from "@/components/store-map/storemap-defs";
import {AisleStructureEntry} from "@/defs/map-locations-defs";
import MapDisplayWithLegend from "@/components/store-map/MapDisplayWithLegend.vue";
import dayjs from "dayjs";
import {DATE_FORMAT} from "@/defs/constants";
import MessageDisplay from "@/components/common/MessageDisplay.vue";
import {tileToMapTileDTOWithColor} from "@/components/store-map/tile-legend-coloring";

@Component
export default class MapEditor extends Vue {
    @Prop() private appData!: AppDataSME;
    private aisles: AisleStructureEntry[] = [];
    private size: string = "regular";
    private validAt: string = "";
    private map: StoreMap = new StoreMap(null, 0, 0, []);
    private resizeW: number = 0;
    private resizeH: number = 0;
    private showLoading: number = 0;

    mounted() {
        this.aisles = this.appData.aisles;
        if (this.appData.map === null) {
            const tiles: MapTile[] = [];
            for (let x = 0; x < this.appData.defaultSize; x += 1) {
                for (let y = 0; y < this.appData.defaultSize; y += 1) {
                    tiles.push(new MapTile(null, x, y, TileType.SPACE, null));
                }
            }
            this.map = new StoreMap(null, this.appData.defaultSize, this.appData.defaultSize, tiles);
        } else {
            this.map = StoreMap.fromDTOs(this.appData.map, this.appData.tiles);
        }

        this.resizeW = this.map.width;
        this.resizeH = this.map.height;
        this.validAt = dayjs().format(DATE_FORMAT);
        // Bridge between Vue and bootstrap-datepicker
        // eslint-disable-next-line
        $("#valid-at-field").on("dp.change", (e: any) => {
            this.validAt = e.date.format(DATE_FORMAT);
        });
    }

    get display(): MapDisplayWithLegend {
        // @ts-ignore This is always a reference to MapDisplayWithLegend
        return this.$refs.display;
    }

    get messages(): MessageDisplay {
        // @ts-ignore This is always a reference to MessageDisplay
        return this.$refs.messages;
    }

    private async saveChanges() {
        this.showLoading += 1;
        this.messages.clearMessages();
        const mapDTO = this.map.toMapDTO();
        const tilesDTOs = this.map.tiles.map((mt) => tileToMapTileDTOWithColor(mt, this.display.colors));
        let response: MapSaveResponse;
        try {
            response = await saveMap(this.appData.saveEndpoint, mapDTO, tilesDTOs, this.validAt);
        } catch (e) {
            this.messages.setError(gettext("Unable to save the map!"));
            return;
        } finally {
            this.showLoading -= 1;
        }
        if (response.success) {
            this.messages.setSuccessFlash(response.message);
        } else if (response.warning) {
            this.messages.setWarningFlash(response.message);
        } else {
            this.messages.setError(response.message);
        }
        if (response.map !== null) {
            this.map = StoreMap.fromDTOs(response.map, response.tiles);
        }
    }

    @Watch("aisles")
    private updateColorsInLegend() {
        this.display.updateColors(this.aisles);
    }

    private updateRows() {
        // @ts-ignore This is always a reference to MapDisplayWithLegend
        this.display.updateRows();
    }

    private getRows(): MapTileRow[] {
        // @ts-ignore This is always a reference to MapDisplayWithLegend
        return this.display.getRows();
    }

    private resizeMap() {
        const rows: MapTileRow[] = this.getRows();
        this.map.tiles = [];
        for (let x = 0; x < this.resizeW; x += 1) {
            for (let y = 0; y < this.resizeH; y += 1) {
                let newTile: MapTile;
                let oldTile: MapTile | undefined;
                const row: MapTileRow | undefined = rows[y];
                if (row !== undefined) {
                    oldTile = row.tiles[x];
                }
                if (oldTile === undefined) {
                    newTile = new MapTile(null, x, y, TileType.SPACE, null);
                } else {
                    newTile = new MapTile(oldTile.id, x, y, oldTile.tileType, oldTile.subaisle);
                }
                this.map.tiles.push(newTile);
            }
        }
        this.map.height = this.resizeH;
        this.map.width = this.resizeW;
        this.updateRows();
    }
}
</script>

<style scoped>

</style>
