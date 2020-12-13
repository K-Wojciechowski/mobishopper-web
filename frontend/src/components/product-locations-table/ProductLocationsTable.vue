<template>
    <div>
        <div class="collapse pb-2" id="store-map">
            <div class="card">
                <div class="card-body" v-if="storeMap !== null">
                    <h5 class="card-title">{{ getText("Store map") }}</h5>
                    <MapDisplayWithLegend
                        :map="storeMap" :aisles="aisleStructure"
                        :editable="false" :showTooltips="true" size="regular"
                        @tileClicked="setTileFromClick"></MapDisplayWithLegend>
                </div>
                <div class="card-body" v-else>
                    <p>{{ getText("No map is available for this store at the selected validity time.") }}</p>
                </div>
            </div>
        </div>
        <div class="card-box card-box-top">
            <form class="form-inline align-content-center flex-column" action="" method="GET">
                <div class="d-flex">
                    <div class="btn-group mr-2" role="group" :aria-label="getText('Filters')">
                        <button type="button" v-for="theFilter in FILTER_OPTIONS_" :key="theFilter[0]"
                                class="btn btn-outline-primary" :class="{'active': filter === theFilter[0]}"
                                @click="filter = theFilter[0]">{{ theFilter[1] }}</button>
                    </div>
                </div>
                <div class="d-flex mt-2">
                    <div>
                        <input class="form-control mr-2" :placeholder="getText('Name')" id="name-search"
                               v-model="nameSearch">
                        <input class="form-control mr-2" :placeholder="getText('Vendor')" id="vendor-search"
                               v-model="vendorSearch">
                        <select class="form-control mr-2" id="subcategory-search" v-model="subcategorySearch">
                            <option value="0">{{getText( "Select subcategory") }}</option>
                            <optgroup v-for="cat in categoryStructure" :key="cat.id" :label="cat.name">
                                <option v-for="sc in cat.subcategories" :key="sc.id"
                                        :value="sc.id">{{ sc.name }}</option>
                            </optgroup>
                        </select></div>
                    <div class="vertical-divider ml-3 pl-3">
                        <label for="items-per-page" class="mr-2 d-inline">{{ getText("Items per page:") }}</label>
                        <select class="form-control mr-2" id="items-per-page" v-model.number="itemsPerPage">
                            <option :value="10">10</option>
                            <option :value="30">30</option>
                            <option :value="50">50</option>
                        </select>
                        <button class="btn btn-primary" type="button" data-toggle="collapse" data-target="#store-map"
                                aria-expanded="false" aria-controls="store-map">
                            {{ getText("Show/hide store map") }}
                        </button>
                    </div>
                </div>
            </form>
        </div>

        <table class="table table-hover table-vam">
            <tr>
                <th style="width: 15%">{{ getText("Product") }}</th>
                <th style="width: 15%">{{ getText("Vendor") }}</th>
                <th style="width: 15%">{{ getText("Validity") }}</th>
                <th style="width: 15%">{{ getText("Subaisle") }}</th>
                <th style="width: 15%">{{ getText("Tile") }}</th>
                <th style="width: 15%">{{ getText("Actions") }}</th>
            </tr>
            <ProductLocationsTableRow
                v-for="item in items" :key="item.product.id" :product="item.product"
                :change="item.change" :aisleStructure="aisleStructure" :tileList="tileList"
                @startPicking="startPickingFromMap"
                :isPicking="pickingFor !== null && pickingFor.product.id === item.product.id"
            ></ProductLocationsTableRow>
        </table>
        <div v-if="showLoading === 0 && initialized && items.length === 0">
            <p class="lead">{{ getText("No results found." )}}</p></div>

        <MessageDisplay ref="messages"></MessageDisplay>

        <Pagination :currentPage="page" :maxPages="totalPages" @back="goBack"
                    @forward="goForward"></Pagination>

        <div class="card-box card-box-bottom">
            <div class="form-inline justify-content-center">
                <label for="valid-at-field">{{ getText("Changes in effect after:" )}}</label>

                <div class="input-group date">
                    <input type="text" name="date_started" class="form-control ml-2"
                           :placeholder="getText('Valid from')" title="" v-model="validAt" id="valid-at-field"
                           dp_config="{&quot;id&quot;: &quot;dp_1&quot;, &quot;picker_type&quot;:
&quot;DATETIME&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true,
&quot;showClear&quot;: false, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;YYYY-MM-DD HH:mm:ss&quot;}}">
                    <div class="input-group-addon input-group-append" data-target="#datetimepicker1"
                         data-toggle="datetimepickerv">
                        <div class="input-group-text"><i class="glyphicon glyphicon-calendar"></i></div>
                    </div>
                </div>

                <div class="vertical-divider ml-3 pl-3">
                    <button type="button" class="btn btn-lg btn-success" @click="saveChanges()">
                        <IconBox icon="check" size="16" :text="getText('Save')"></IconBox>
                        <span v-if="changeCount() > 0">&nbsp; ({{ changeCount() }})</span>
                    </button>

                    <button type="button" class="btn btn-lg btn-outline-warning ml-1" @click="clearChanges()">
                        <IconBox icon="x-square" size="16" :text="getText('Undo all')"></IconBox></button>
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
    AppDataPLT,
    getProductGroups,
    getProducts,
    ProductGroupsGetResponse,
    ProductLocationChange,
    ProductLocationChangeResponse,
    ProductLocationGetResponse,
    ProductLocationFilter,
    ProductLocationsTableItem,
    ProductToLocate,
    saveChanges,
    FILTER_OPTIONS,
} from "@/components/product-locations-table/productlocationstable-defs";
import dayjs from "dayjs";
import {
    CategoryStructureEntry,
    AisleStructureEntry,
    Subaisle,
} from "@/defs/map-locations-defs";
import {DATE_FORMAT} from "@/defs/constants";
import {MapTile, StoreMap} from "@/components/store-map/storemap-defs";
import MessageDisplay from "@/components/common/MessageDisplay.vue";

@Component
export default class ProductLocationsTable extends Vue {
    @Prop() private appData!: AppDataPLT;
    private items: ProductLocationsTableItem[] = [];
    private aisleStructure: AisleStructureEntry[] = [];
    private categoryStructure: CategoryStructureEntry[] = [];
    private subaisleList: Subaisle[] = [];
    private tileList: MapTile[] = [];
    private filter: ProductLocationFilter = ProductLocationFilter.ALL;
    private changes: ProductLocationChange[] = [];
    private changesById: Map<number, ProductLocationChange> = new Map();
    private validAt: string = "";
    private nameSearch: string = "";
    private vendorSearch: string = "";
    private subcategorySearch: number = 0;
    private page: number = 1;
    private totalPages: number = 1;
    private itemsPerPage: number = 10;
    private showLoading: number = 0;
    private storeMap: StoreMap | null = null;
    private initialized: boolean = false;
    private FILTER_OPTIONS_: [ProductLocationFilter, string][] = FILTER_OPTIONS; // copy for Vue template
    private pickingFor: ProductLocationChange | null = null;

    async mounted() {
        this.filter = this.appData.initialView as ProductLocationFilter;
        this.itemsPerPage = this.appData.defaultPageSize;
        this.categoryStructure = this.appData.categoryStructure;
        this.validAt = dayjs().format(DATE_FORMAT);
        this.initialized = true;
        // Bridge between Vue and bootstrap-datepicker
        // eslint-disable-next-line
        $("#valid-at-field").on("dp.change", (e: any) => {
            this.validAt = e.date.format(DATE_FORMAT);
        });
        await this.updateList(true);
        await this.updateGroups();
    }

    get messages(): MessageDisplay {
        // @ts-ignore This is always a reference to MessageDisplay
        return this.$refs.messages;
    }

    @Watch("nameSearch")
    @Watch("vendorSearch")
    @Watch("subcategorySearch")
    @Watch("validAt")
    @Watch("filter")
    @Watch("page")
    @Watch("itemsPerPage")
    private async watcherUpdateList() {
        if (!this.initialized) return;
        await this.updateList();
    }

    @Watch("validAt")
    private async watcherUpdateGroups() {
        if (!this.initialized) return;
        await this.updateGroups();
    }

    private async updateList(allowSwitching: boolean = false) {
        if (this.showLoading === 0) {
            this.messages.clearMessages();
        }
        this.showLoading += 1;
        let response: ProductLocationGetResponse;
        try {
            response = await getProducts(
                this.appData.getEndpoint, this.filter, this.nameSearch, this.vendorSearch, this.subcategorySearch,
                this.validAt, this.page, this.itemsPerPage,
            );
        } catch (e) {
            this.messages.setError(gettext("Unable to get product data!"));
            return;
        } finally {
            this.showLoading -= 1;
        }
        if (this.filter !== response.filter) {
            if (allowSwitching) {
                this.filter = response.filter;
            } else {
                this.items = [];
                this.page = 1;
                this.totalPages = 0;
                return;
            }
        }
        this.updateItems(response.products);
        this.page = response.page;
        this.totalPages = response.totalPages;
    }

    private async updateGroups() {
        if (this.showLoading === 0) {
            this.messages.clearMessages();
        }
        this.showLoading += 1;
        let response: ProductGroupsGetResponse;
        try {
            response = await getProductGroups(this.appData.groupsEndpoint, this.validAt);
        } catch (e) {
            this.showLoading -= 1;
            this.messages.setError(gettext("Unable to get groups list!"));
            return;
        }
        this.showLoading -= 1;
        this.aisleStructure = response.aisleStructure;
        this.subaisleList = response.subaisles;
        this.storeMap = StoreMap.fromDTOs(response.map, response.tiles);
        this.tileList = this.storeMap.tiles;
    }

    private async saveChanges() {
        this.messages.clearMessages();
        this.showLoading += 1;
        const filteredChanges = this.changes.filter((change) => change.hasChanges()).map(
            (change) => change.prepareForUpload(),
        );
        let response: ProductLocationChangeResponse;
        try {
            response = await saveChanges(
                this.appData.updateEndpoint, filteredChanges, this.validAt,
            );
        } catch (e) {
            this.showLoading -= 1;
            this.messages.appendError(gettext("Failed to save changes!"));
            return;
        }
        this.showLoading -= 1;
        if (response.success) {
            this.clearEverything();
            await this.updateList();
            this.messages.setSuccessFlash(response.message);
        } else if (response.warning) {
            this.clearEverything();
            await this.updateList();
            this.messages.setWarningFlash(response.message);
        } else {
            this.messages.setError(response.message);
        }
    }

    private updateItems(products: ProductToLocate[]) {
        this.items = [];
        products.forEach((product) => {
            if (product.location !== null && product.location.tile !== null && "tile_type" in product.location.tile) {
                product.location.tile = MapTile.fromDTO(product.location.tile);
            }

            let change = this.changesById.get(product.id);
            if (change === undefined) {
                change = ProductLocationChange.fromProduct(product);
                this.changes.push(change);
                this.changesById.set(product.id, change);
            }
            this.items.push(new ProductLocationsTableItem(product, change));
        });
    }

    private clearEverything() {
        this.changes = [];
        this.items = [];
        this.changesById.clear();
    }

    private clearChanges() {
        this.changes = [];
        this.items.forEach((item) => {
            item.change = ProductLocationChange.fromProduct(item.product);
            this.changes.push(item.change);
            this.changesById.set(item.product.id, item.change);
        });
    }

    private startPickingFromMap(change: ProductLocationChange) {
        if (change.product?.id === this.pickingFor?.product?.id) {
            this.pickingFor = null;
            return;
        }
        this.pickingFor = change;
        // @ts-ignore collapse added by Bootstrap
        $("#store-map").collapse("show");
    }

    private setTileFromClick(tile: MapTile) {
        if (this.pickingFor === null) return;
        this.pickingFor.tile = tile;
        this.pickingFor = null;
    }

    private changeCount() {
        return this.changes.filter((change) => change.hasChanges()).length;
    }

    private goBack() {
        if (this.page > 1) {
            this.page -= 1;
        }
    }

    private goForward() {
        if (this.page < this.totalPages) {
            this.page += 1;
        }
    }
}
</script>

<style scoped>

</style>
