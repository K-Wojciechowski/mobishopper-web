import Vue from "vue";

import IconBox from "@/components/common/IconBox.vue";
import MessageDisplay from "@/components/common/MessageDisplay.vue";
import ModalLauncher from "@/components/common/ModalLauncher.vue";
import ModalBox from "@/components/common/ModalBox.vue";
import Pagination from "@/components/common/Pagination.vue";
import TabItemDelete from "@/components/common/TabItemDelete.vue";
import ValidityText from "@/components/common/ValidityText.vue";

import ExtraMetadataEditorInput from "@/components/extra-metadata-editor/ExtraMetadataEditorInput.vue";
import ProductLocationsTableRow from "@/components/product-locations-table/ProductLocationsTableRow.vue";
import MapDisplay from "@/components/store-map/MapDisplay.vue";
import MapLegend from "@/components/store-map/MapLegend.vue";
import MapDisplayWithLegend from "@/components/store-map/MapDisplayWithLegend.vue";

import LocalPermissionTable from "@/components/local-permission-table/LocalPermissionTable.vue";
import ModalItemSelector from "@/components/modal-item-selector/ModalItemSelector.vue";
import ExtraMetadataEditor from "@/components/extra-metadata-editor/ExtraMetadataEditor.vue";
import ProductLocationsTable from "@/components/product-locations-table/ProductLocationsTable.vue";
import MapStaticDisplayApp from "@/components/store-map/MapStaticDisplayApp.vue";
import MapEditor from "@/components/store-map/MapEditor.vue";

// Common
Vue.component("IconBox", IconBox);
Vue.component("MessageDisplay", MessageDisplay);
Vue.component("ModalLauncher", ModalLauncher);
Vue.component("ModalBox", ModalBox);
Vue.component("Pagination", Pagination);
Vue.component("TabItemDelete", TabItemDelete);
Vue.component("ValidityText", ValidityText);

// Subcomponents
Vue.component("ExtraMetadataEditorInput", ExtraMetadataEditorInput);
Vue.component("ProductLocationsTableRow", ProductLocationsTableRow);
Vue.component("MapDisplay", MapDisplay);
Vue.component("MapLegend", MapLegend);
Vue.component("MapDisplayWithLegend", MapDisplayWithLegend);

// Apps
Vue.component("LocalPermissionTable", LocalPermissionTable);
Vue.component("ModalItemSelector", ModalItemSelector);
Vue.component("ExtraMetadataEditor", ExtraMetadataEditor);
Vue.component("ProductLocationsTable", ProductLocationsTable);
Vue.component("MapStaticDisplayApp", MapStaticDisplayApp);
Vue.component("MapEditor", MapEditor);

Vue.config.productionTip = false;

Vue.mixin({
    methods: {
        getText(text: string): string {
            return gettext(text);
        },
    },
});

VUE_APPS.forEach((appData) => {
    // eslint-disable-next-line
    let appClass: any;
    if (appData.THIS_APP === "users-edit-local-permissions") {
        appClass = LocalPermissionTable;
    } else if (appData.THIS_APP === "modal-item-selector") {
        appClass = ModalItemSelector;
    } else if (appData.THIS_APP === "extra-metadata-editor") {
        appClass = ExtraMetadataEditor;
    } else if (appData.THIS_APP === "product-locations-table") {
        appClass = ProductLocationsTable;
    } else if (appData.THIS_APP === "map-static-display") {
        appClass = MapStaticDisplayApp;
    } else if (appData.THIS_APP === "map-editor") {
        appClass = MapEditor;
    }


    // eslint-disable-next-line
    new Vue({
        el: appData.APP_TAG,
        data: appData,
        render: (h) => h(appClass, {props: {appData}}),
    });
});
