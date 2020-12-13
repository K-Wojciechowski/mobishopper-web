<template>
    <div>
        <div class="alert alert-success" v-if="successMessage.length > 0">{{ successMessage }}</div>
        <div class="alert alert-warning" v-if="warningMessage.length > 0">{{ warningMessage }}</div>
        <div class="alert alert-danger" v-if="errorMessage.length > 0">{{ errorMessage }}</div>
    </div>
</template>

<script lang="ts">
import {Component, Vue} from "vue-property-decorator";

@Component
export default class MessageDisplay extends Vue {
    private successMessage: string = "";
    private warningMessage: string = "";
    private errorMessage: string = "";
    private successFlashTimeout: number | null = null;
    private warningFlashTimeout: number | null = null;

    public clearMessages() {
        this.successMessage = "";
        this.warningMessage = "";
        this.errorMessage = "";
        if (this.successFlashTimeout !== null) {
            clearTimeout(this.successFlashTimeout);
        }
        if (this.warningFlashTimeout !== null) {
            clearTimeout(this.warningFlashTimeout);
        }
        this.successFlashTimeout = null;
        this.warningFlashTimeout = null;
    }

    public setSuccessFlash(message: string) {
        this.successMessage = message;
        this.successFlashTimeout = setTimeout(() => {
            this.successMessage = "";
            this.successFlashTimeout = null;
        }, 5000);
    }

    public setWarningFlash(message: string) {
        this.warningMessage = message;
        this.warningFlashTimeout = setTimeout(() => {
            this.warningMessage = "";
            this.warningFlashTimeout = null;
        }, 5000);
    }

    public setError(message: string) {
        this.errorMessage = message;
    }

    public appendError(message: string) {
        this.errorMessage += message;
    }
}
</script>

<style scoped>

</style>
