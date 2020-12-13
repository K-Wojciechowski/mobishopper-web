<template>
    <div>
        <span v-if="selected.length !== 0" class="mr-1 comma-separated-links">
            <a v-for="item in selected" :key="item.id" :href="item.details_url" target="_blank">{{ item.name }}</a>
        </span>
        <input class="invisible-input" :required="true" value="" v-if="showBlankRequiredField()">
        <input v-for="item in selected" :key="item.id" :name="appData.misInputName" type="hidden" :value="item.id">
        <ModalLauncher :modalId="appData.misModalId" :id="'id_' + appData.misInputName"
                       className="btn btn-outline-primary">{{ getText("Select…") }}</ModalLauncher>
        <ModalBox :modalId="appData.misModalId" sizeClass="modal-lg" :title="appData.misTitle"
                  :showFooter="appData.misMultipleSelection" @modalAccept="handleAccept">
            <label class="sr-only" :for="appData.misModalId + 'Search'">{{ getText("Search") }}</label>
            <input class="form-control" type="search"
                   :id="appData.misModalId + 'Search'" v-model="searchQuery" :placeholder="getText('Search')">

            <table class="table table-hover table-vam">
                <thead>
                <tr>
                    <th>{{ getText("Select") }}</th>
                    <th>{{ appData.misItemName }}</th>
                    <th v-for="item in appData.misExtraFieldNames" :key="item">{{ item }}</th>
                    <th>{{ getText("Actions") }}</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="item in itemList" :key="item.id">
                    <td><button type="button" v-bind:class="{btn: true,
                                'btn-success': !appData.misMultipleSelection || isSelected(item),
                                'btn-outline-success': appData.misMultipleSelection && !isSelected(item)}"
                                @click="handleSelectDeselect(item)">{{ getText("Select") }}</button></td>
                    <td><img v-if="item.photo != null" :src="item.photo"
                             class="mis-image" :alt="item.name"> {{ item.name }}</td>
                    <td v-for="extra in item.extras" :key="extra">{{ extra }}</td>
                    <td><a :href="item.details_url" target="_blank"
                           class="btn btn-outline-info">{{ getText("Details") }}</a></td>
                </tr>
                </tbody>
            </table>

            <Pagination :currentPage="itemPage" :maxPages="maxPages" @back="goBack"
                        @forward="goForward"></Pagination>

            <div class="text-center" v-if="!showLoading && itemList.length === 0">
                {{ getText("No results found.") }}
            </div>
            <div class="text-center" v-if="showLoading">
                <IconBox :text="getText('Loading…' )" icon="hourglass-split" size="16"></IconBox>
            </div>
        </ModalBox>
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
    AppDataMIS,
    ModalItem,
    getModalItems,
} from "@/components/modal-item-selector/modalitemselector-defs";
import _ from "lodash";

@Component
export default class ModalItemSelector extends Vue {
    @Prop() private appData!: AppDataMIS;
    private showLoading = true;
    private itemList: ModalItem[] = [];
    private searchQuery = "";
    private itemPage = 1;
    private maxPages = 1;
    private selected: ModalItem[] = [];
    private newSelection: ModalItem[] = [];
    private selectionsCopied: boolean = false;
    private jQueryModal!: JQuery;

    mounted() {
        if (!this.selectionsCopied) {
            this.selected = this.appData.misInitialSelection;
            this.selectionsCopied = true;
        }
        this.jQueryModal = jQuery(`#${this.appData.misModalId}`);
        this.jQueryModal.on("show.bs.modal", () => {
            this.newSelection = this.selected;
            this.itemPage = 1;
            this.searchQuery = "";
            this.loadData();
        });
    }

    @Watch("searchQuery")
    @Watch("itemPage")
    private loadData() {
        this.showLoading = true;
        getModalItems(this.appData.misApiEndpoint, this.itemPage, this.searchQuery).then((dataContainer) => {
                this.itemList = dataContainer.items;
                this.maxPages = dataContainer.num_pages;
                this.itemPage = dataContainer.page;
                this.showLoading = false;
                // @ts-ignore: Modal added by Bootstrap
                this.jQueryModal.modal("handleUpdate");
            });
    }

    private goBack() {
        if (this.itemPage > 1) {
            this.itemPage -= 1;
        }
    }

    private goForward() {
        if (this.itemPage < this.maxPages) {
            this.itemPage += 1;
        }
    }

    private handleAccept() {
        this.selected = this.newSelection;
        // @ts-ignore: Modal added by Bootstrap
        this.jQueryModal.modal("hide");
    }

    private isSelected(item: ModalItem): boolean {
        return this.newSelection.find((i) => i.id === item.id) !== undefined;
    }

    private showBlankRequiredField() {
        return this.appData.misRequired && this.selected.length === 0;
    }

    private handleSelectDeselect(item: ModalItem) {
        if (!this.appData.misMultipleSelection) {
            this.selected = [item];
            // @ts-ignore: Modal added by Bootstrap
            this.jQueryModal.modal("hide");
        } else if (this.isSelected(item)) {
            this.newSelection = this.newSelection.filter((i) => i.id !== item.id);
        } else {
            this.newSelection.push(item);
        }
    }
}
</script>
