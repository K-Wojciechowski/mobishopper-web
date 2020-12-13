<template>
    <div class="modal fade" :id="modalId" tabindex="-1" role="dialog" :aria-labelledby="modalId + 'Label'"
         aria-hidden="true">
        <div :class="'modal-dialog ' + sizeClass" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" :id="modalId + 'Label'">{{ title }}</h5>
                    <button type="button" class="close" data-dismiss="modal" :aria-label="getText('Close')">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <slot></slot>
                </div>
                <div class="modal-footer" v-if="showFooter">
                    <slot name="footer">
                        <button type="button" class="btn btn-primary"
                                @click="handleAccept()">{{ getText("OK") }}</button>
                        <button type="button" class="btn btn-secondary"
                                data-dismiss="modal">{{ getText("Cancel") }}</button>
                    </slot>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import {Component, Prop, Vue} from "vue-property-decorator";

@Component
export default class ModalBox extends Vue {
    @Prop() private modalId!: string;
    @Prop() private title!: string;
    @Prop({default: ""}) private sizeClass!: string;
    @Prop({default: true}) private showFooter!: boolean;

    closeButtonText(): string {
        return gettext("Close");
    }

    handleAccept() {
        this.$emit("modalAccept", this.modalId);
    }
}
</script>
