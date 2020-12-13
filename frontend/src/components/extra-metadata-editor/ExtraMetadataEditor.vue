<template>
    <div>
        <input name="extra_metadata_raw" type="hidden" :value="outputExtraMetadata()" ref="outputFormField">
        <table class="table table-hover table-vam">
            <thead>
            <tr>
                <th width="45%">{{ getText("Field") }}</th>
                <th width="45%">{{ getText("Value") }}</th>
                <th width="10%">{{ getText("Actions") }}</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="item in itemList" :key="item.id">
                <td>
                    <span class="text-warning mr-1" v-if="item.slug === '' && appData.emeHighlightCustom">★</span>
                    {{ item.name }}</td>
                <td><ExtraMetadataEditorInput :item="item"></ExtraMetadataEditorInput></td>
                <td><TabItemDelete :item="item.id" @delete="deleteItem"></TabItemDelete></td>
            </tr>
            <tr>
                <td>
                    <select class="extra-metadata-new-select">
                        <option value="">---------</option>
                    </select>
                </td>
                <td><ExtraMetadataEditorInput :item="newItem"></ExtraMetadataEditorInput></td>
                <td><button type="button" class="btn btn-sm btn-success" @click="addItem" :disabled="!canAddItem()">
                    <IconBox icon="plus" :text="getText('Add')" size="12"></IconBox></button></td>
            </tr>
            </tbody>
        </table>

            <div class="text-center" v-if="showLoading">
                <IconBox :text="getText('Loading…' )" icon="hourglass-split" size="16"></IconBox>
            </div>
            <div class="text-danger" v-if="showValidationError">
                <IconBox :text="getValidationErrorText()" icon="x-circle-fill" size="16"></IconBox>
            </div>
        </div>
</template>

<script lang="ts">
import {
    Component,
    Prop,
    Vue,
} from "vue-property-decorator";
import {
    AppDataEME,
    getStandardFields,
    InternalMetaValue,
    MetaValue,
    StandardMetaField,
    StandardMetaFieldContainer,
} from "@/components/extra-metadata-editor/extrametadataeditor-defs";

@Component
export default class ExtraMetadataEditor extends Vue {
    @Prop() private appData!: AppDataEME;
    private showLoading = false;
    private showValidationError = false;
    private requiredFieldsMissing: string[] = [];
    private itemList: InternalMetaValue[] = [];
    private standardFields: StandardMetaFieldContainer = new StandardMetaFieldContainer();
    private standardFieldsMap: Map<string, StandardMetaField> = new Map<string, StandardMetaField>();
    private standardFieldSlugs: Set<string> = new Set<string>();
    private standardFieldsFromSubcategory: boolean = false;
    private subcategorySelect: HTMLSelectElement | null = null;
    private newItem: InternalMetaValue = new InternalMetaValue();
    private lastId = 0;

    private buildStandardFieldsMap() {
        this.standardFieldsMap = new Map<string, StandardMetaField>();
        this.standardFields.items.forEach((smf) => this.standardFieldsMap.set(smf.slug, smf));
    }

    private buildStandardFieldSlugs() {
        this.standardFieldSlugs = new Set<string>();
        this.standardFields.items.forEach((smf) => this.standardFieldSlugs.add(smf.slug));
    }

    private updateItemListWithStandardFields() {
        this.itemList.forEach((mv) => {
            mv.standardMetaField = this.getStandardMetaField(mv);
        });
    }

    private getStandardMetaField(mv: MetaValue) {
        const smf = this.standardFieldsMap.get(mv.slug);
        return smf === undefined ? null : smf;
    }

    mounted() {
        this.addHandlerToSubmit();
        this.itemList = this.appData.emeInitialData.map((mv, index) => InternalMetaValue.toInternal(mv, index, null));
        this.lastId = this.itemList.length - 1;
        if (this.appData.emeUseSubcategory) {
            this.subcategorySelect = document.querySelector<HTMLSelectElement>("select[name='subcategory']");
            if (this.subcategorySelect !== null) {
                this.getStandardFieldsData(this.subcategorySelect.value);
                this.subcategorySelect.addEventListener("change", () => {
                    if (this.subcategorySelect !== null) {
                        this.getStandardFieldsData(this.subcategorySelect.value);
                    }
                });
            } else {
                this.getStandardFieldsData(null);
            }
        } else {
            this.getStandardFieldsData(null);
        }
        const sel = $(".extra-metadata-new-select");
        // eslint-disable-next-line
        const self = this;
        // @ts-ignore Select2
        sel.select2({
            theme: "bootstrap4",
            width: "100%",
            tags: true,
        });
        // eslint-disable-next-line
        sel.on("select2:select", (ev: any) => {
            // @ts-ignore Select2
            // eslint-disable-next-line
            let data: any = sel.select2("data")[0];
            this.newItem.slug = this.standardFieldSlugs.has(data.id) ? data.id : "";
            this.newItem.name = data.text;
            this.newItem.units = "";
            this.newItem.standardMetaField = this.getStandardMetaField(this.newItem);
        });
    }

    getStandardFieldsData(theSubcategory: string | number | null) {
        this.showLoading = true;
        let subcategory = theSubcategory;
        if (typeof subcategory === "string") {
            subcategory = parseInt(subcategory, 10);
        }
        if (subcategory !== null && (subcategory <= 0 || Number.isNaN(subcategory))) {
            subcategory = null;
        }
        getStandardFields(this.appData.emeApiEndpoint, subcategory).then((smfc) => {
            this.showLoading = false;
            this.standardFields = smfc;
            this.standardFieldsFromSubcategory = theSubcategory !== null;
            this.updateSelect2();
            this.buildStandardFieldsMap();
            this.buildStandardFieldSlugs();
            this.updateItemListWithStandardFields();
        });
    }

    updateSelect2() {
        const sel = $(".extra-metadata-new-select");
        sel.html("").trigger("change");
        const blankOption = new Option("---------", "", false, false);
        sel.append(blankOption).trigger("change");
        const usedStandardFields = new Set(this.itemList.map((imv) => imv.slug));
        this.standardFields.items.forEach((smf) => {
            if (usedStandardFields.has(smf.slug)) return;
            const newOption = new Option(this.getNameWithReq(smf), smf.slug, false, false);
            sel.append(newOption).trigger("change");
        });
        sel.val(this.newItem.slug).trigger("change");
    }

    addItem() {
        if (!this.canAddItem()) return;
        this.newItem.id = this.lastId;
        if (this.newItem.slug !== "") {
            // Remove asterisk from name
            const newName = this.standardFieldsMap.get(this.newItem.slug)?.name;
            this.newItem.name = newName !== undefined ? newName : this.newItem.name;
        }
        this.lastId += 1;
        this.itemList.push(this.newItem);
        this.newItem = new InternalMetaValue();
        $(".extra-metadata-new-select").val("").trigger("change");
        this.updateSelect2();
    }

    canAddItem() {
        const eun = this.newItem.standardMetaField?.expected_units_names;
        if (eun !== undefined && eun.length > 0 && this.newItem.standardMetaField?.expected_units !== "_bool") {
            return this.newItem.units !== "" && this.newItem.value !== "";
        }
        return this.newItem.value !== "";
    }

    deleteItem(item: number) {
        this.itemList = this.itemList.filter((value) => value.id !== item);
        this.updateSelect2();
    }

    getNameWithReq(smf: StandardMetaField): string {
        let {name} = smf;
        if (smf.is_required) {
            name += " *";
        }
        return name;
    }

    outputExtraMetadata(): string {
        return JSON.stringify(this.itemList.map((imv) => imv.toGeneral()));
    }

    addHandlerToSubmit() {
        // @ts-ignore The type definitions don’t know it’s an input element
        const hiddenInput: HTMLInputElement = this.$refs.outputFormField;
        if (hiddenInput.form !== null) {
            hiddenInput.form.addEventListener("submit", this.validateForm);
        }
    }

    validateForm(ev: Event): boolean {
        let success = true;
        this.requiredFieldsMissing = [];
        if (this.standardFieldsFromSubcategory) {
            const standardItemSet = new Set(this.standardFields.items.map((smf) => smf.name));
            this.itemList.forEach((imf) => {
                standardItemSet.delete(imf.name);
            });
            if (standardItemSet.size > 0) {
                success = false;
                standardItemSet.forEach((name) => this.requiredFieldsMissing.push(name));
            }
        }
        this.showValidationError = !success;
        if (!success) {
            ev.preventDefault();
        }
        return success;
    }

    getValidationErrorText(): string {
        if (this.requiredFieldsMissing.length === 0) {
            return gettext("An unexpected validation error occurred.");
        }
        return gettext("The following required fields are missing: ") + this.requiredFieldsMissing.join(", ");
    }
}
</script>
