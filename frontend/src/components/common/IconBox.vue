<template>
    <div class="iconbox">
        <svg class="bi" :width="size" :height="size" fill="currentColor">
            <use v-bind:xlink:href="iconHref()"/>
        </svg>
        {{text}}
    </div>
</template>

<script lang="ts">
    import {Component, Prop, Vue} from "vue-property-decorator";

    @Component
    export default class IconBox extends Vue {
        @Prop() private icon!: string;

        @Prop() private size!: number;

        @Prop() private text!: string;

        iconHref(): string {
            return `/static/bootstrap-icons.svg#${this.icon}`;
        }
    }
</script>
