<template>
    <tr
        :class="{'table-info': change.hasValueChanges(), 'table-warning': change.hasExtrasChanges()}">
        <td><a :href="product.details_url" target="_blank">{{ product.name }}</a></td>
        <td><a :href="product.vendor_details_url" target="_blank">{{ product.vendor }}</a></td>
        <td><ValidityText :started="product.date_started" :ended="product.date_ended"></ValidityText></td>
        <td v-if="!change.hasExtrasChanges()">
            <select class="form-control" v-model="change.subaisle">
                <option :value="null">---------</option>
                <optgroup v-for="aisle in aisleStructure" :key="aisle.id" :label="aisle.name">
                    <option v-for="subaisle in aisle.subaisles" :key="subaisle.id"
                            :value="subaisle">{{ subaisle.name }}</option>
                </optgroup>
            </select>
        </td>
        <td v-if="!change.hasExtrasChanges()">
            <div class="input-group">
                <select class="form-control" v-model="change.tile">
                    <option :value="null">---------</option>
                    <option v-for="tile in tileList" :key="tile.id"
                            :value="tile">{{ tile.letterCoordsWithText }}</option>
                </select>
                <div class="input-group-append">
                    <button
                        type="button" class="btn btn-sm" style="padding:0"
                        :class="{'btn-outline-dark': !isPicking, 'btn-dark': isPicking}"
                        :title="getText('Pick from map')" @click="startPicking()">
                        <IconBox :size="12" text="" icon="cursor-fill"></IconBox>
                    </button>
                </div>
            </div>
        </td>
        <td v-if="change.hasExtrasChanges()" colspan="2">
            <span v-if="change.revert_auto">{{ getText("Location will revert to auto") }}</span>
            <span v-if="change.delete_location">{{ getText("Location will be deleted") }}</span>
        </td>
        <td>
            <button type="button" class="btn btn-sm btn-warning mr-1"
                    v-if="change.hasChanges()"
                    @click="undoChanges()">
                <IconBox :size="12" :text="getText('Undo')" icon="x-square"></IconBox></button>
            <div class="dropdown d-inline-block">
                <button type="button" class="btn btn-sm btn-secondary dropdown-toggle"
                        :id="'plt-extras-' + product.id" data-toggle="dropdown"
                        aria-haspopup="true" aria-expanded="false">
                    <IconBox :size="12" :text="getText('Special')" icon="gear-fill"></IconBox>
                </button>
                <div class="dropdown-menu" :aria-labelledby="'plt-extras-' + product.id">
                    <a class="dropdown-item" href="#"
                       @click="revertAuto()">{{ getText("Revert to auto location") }}</a>
                    <a class="dropdown-item" href="#"
                       @click="deleteLocation()">{{ getText("Delete location") }}</a>
                </div>
            </div>
        </td>
    </tr>
</template>

<script lang="ts">
import {
    Component,
    Prop,
    Vue,
} from "vue-property-decorator";
import {
    ProductLocationChange,
    ProductToLocate,
} from "@/components/product-locations-table/productlocationstable-defs";
import {AisleStructureEntry} from "@/defs/map-locations-defs";
import {MapTile} from "@/components/store-map/storemap-defs";

@Component
export default class ProductLocationsTableRow extends Vue {
    @Prop() private product!: ProductToLocate;
    @Prop() private change!: ProductLocationChange;
    @Prop() private aisleStructure!: AisleStructureEntry[];
    @Prop() private tileList!: MapTile[];
    @Prop() private isPicking!: boolean;

    private undoChanges() {
        this.change.subaisle = this.change.start_subaisle;
        this.change.tile = this.change.start_tile;
        this.change.revert_auto = false;
        this.change.delete_location = false;
    }

    private revertAuto() {
        this.undoChanges();
        this.change.revert_auto = true;
    }

    private deleteLocation() {
        this.undoChanges();
        this.change.delete_location = true;
    }

    private startPicking() {
        this.$emit("startPicking", this.change);
    }
}
</script>

<style scoped>

</style>
