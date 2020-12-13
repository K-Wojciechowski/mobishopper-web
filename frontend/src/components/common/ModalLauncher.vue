<template>
<button type="button" :id="id" :class="className" data-toggle="modal" :data-target="'#' + modalId">
    <slot></slot>
</button>
</template>

<script lang="ts">
import {Component, Prop, Vue} from "vue-property-decorator";

@Component
export default class ModalLauncher extends Vue {
    @Prop() private className!: string;
    @Prop() private id!: string;
    @Prop() private modalId!: string;
}
</script>

<style scoped>

</style>
