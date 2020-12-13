<template>
    <div>
        <div v-if="showText(item.standardMetaField)">
            <input type="text" v-model="item.value" class="form-control" :placeholder="getPlaceholder()"
                   @change="item.updateText()">
        </div>
        <div v-if="showBool(item.standardMetaField)">
            <label><input type="radio" v-model="item.value" value="1" class="mr-1"
                          @change="item.updateText()"> {{ getText("yes") }}</label>
            <label class="ml-3"><input type="radio" v-model="item.value" value="0" class="mr-1"
                          @change="item.updateText()"> {{ getText("no") }}</label>
        </div>
        <div class="input-group" v-if="showUnits(item.standardMetaField)">
            <input type="text" v-model="item.value" class="form-control" :placeholder="getPlaceholder()"
                   @change="item.updateText()">
            <select v-model="item.units" @change="item.updateText()" class="form-control">
                <option value="">---------</option>
                <option v-for="unit in item.standardMetaField.expected_units_names" :key="unit" :value="unit">{{ unit }}
                </option>
            </select>
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
    InternalMetaValue,
    EXPECTED_UNITS_CHECK,
    StandardMetaField,
} from "@/components/extra-metadata-editor/extrametadataeditor-defs";

@Component
export default class ExtraMetadataEditorInput extends Vue {
    @Prop() private item!: InternalMetaValue;

    showText(smf: StandardMetaField | null): boolean {
        return smf === null || EXPECTED_UNITS_CHECK.TEXT(smf.expected_units, smf.expected_units_names);
    }

    showBool(smf: StandardMetaField | null): boolean {
        return smf !== null && EXPECTED_UNITS_CHECK.BOOL(smf.expected_units);
    }

    showUnits(smf: StandardMetaField | null): boolean {
        return smf != null && EXPECTED_UNITS_CHECK.SELECT_UNIT(smf.expected_units, smf.expected_units_names);
    }

    getPlaceholder(): string {
        if (this.item.name === "---------") {
            return gettext("Select or type a property name…");
        }
        return this.item.name;
    }
}
</script>
