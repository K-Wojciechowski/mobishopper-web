<template>
    <div id="local-permissions-table-container">
    <table class="table table-hover">
        <thead>
        <tr>
            <th v-for="headerData in headers()" :key="headerData[0]" :class="headerData[1]">{{ headerData[0] }}</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="entry in appData.lpEntries" :key="entry.store">
            <td>{{ entry.name }}</td>
            <td v-for="permKey in permKeys" :key="permKey" class="text-center">
            <input type="checkbox" v-model="entry[permKey]">
            </td>
            <td><TabItemDelete :item="entry.id" @delete="deleteItem"></TabItemDelete></td>
        </tr>
        <tr>
            <td>
                <select v-model="newEntryStore" class="w-100">
                    <optgroup :label="optGroupLabel">
                        <option v-for="store in filteredStoreList" :key="store.id" :value="store">
                            {{ store.name }}
                        </option>
                    </optgroup>
                </select>
            </td>
            <td v-for="permKey in permKeys" :key="permKey" class="text-center">
                <input type="checkbox" v-model="newEntry[permKey]">
            </td>
            <td class="text-left">
                <button type="button" class="btn btn-sm btn-success" @click="addNewItem"
                        :disabled="newEntryStore === null">
                    <IconBox icon="plus" size="12" :text="this.getText('Add')"></IconBox>
                </button>
            </td>
        </tr>
        </tbody>
    </table>
        <input type="hidden" name="local_permissions_json" :value="entriesAsJson">
    </div>
</template>

<script lang="ts">
import {Component, Prop, Vue} from "vue-property-decorator";
import {
    AppDataLPT,
    getStores,
    LocalPermissionEntry,
    Store,
} from "@/components/local-permission-table/localpermissiontable-defs";

@Component
    export default class LocalPermissionTable extends Vue {
        @Prop() private appData!: AppDataLPT;
        private storeList: Store[] = [];
        private newEntry: LocalPermissionEntry = new LocalPermissionEntry();
        private newEntryStore: Store | null = null;

        async mounted() {
            if (this.storeList.length === 0) {
                this.storeList = await getStores();
            }
        }

        get entriesAsJson(): string {
            return JSON.stringify(this.appData.lpEntries);
        }

        get filteredStoreList(): Array<Store> {
            const usedStoreIds = new Set(this.appData.lpEntries.map((lpe: LocalPermissionEntry) => lpe.id));
            return this.storeList.filter((store: Store) => !usedStoreIds.has(store.id));
        }

        get optGroupLabel(): string {
            return this.filteredStoreList.length === 0
                ? gettext("(Permissions added for all stores)")
                : gettext("Select store to add…");
        }

        headers(): string[][] {
            const permTitlesWithAlignment = this.appData.lpTableTitles.map(
                (x: Array<string>) => [x[1], "text-center"],
            );
            return [
                [gettext("Store"), "text-left"],
                ...permTitlesWithAlignment,
                [gettext("Actions"), "text-left"],
            ];
        }

        get permKeys(): Array<string> {
            return this.appData.lpTableTitles.flatMap((x: Array<string>) => x[0]);
        }

        addNewItem() {
            if (this.newEntryStore === null) return;
            this.newEntry.id = this.newEntryStore.id;
            this.newEntry.name = this.newEntryStore.name;
            this.appData.lpEntries.push(this.newEntry);
            this.newEntryStore = null;
            this.newEntry = new LocalPermissionEntry();
        }

        deleteItem(item: number) {
            this.appData.lpEntries = this.appData.lpEntries.filter((value) => value.id !== item);
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
