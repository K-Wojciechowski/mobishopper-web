<template>
    <button type="button" class="btn btn-sm btn-danger" v-on:click="$emit('delete', item)">
        <IconBox icon="trash" size="12" :text="theText()"></IconBox>
    </button>
</template>

<script lang="ts">
    import {Component, Prop, Vue} from "vue-property-decorator";

    @Component
    export default class TabItemDelete extends Vue {
        @Prop() private item!: (string|number);

        theText(): string {
            return gettext("Delete");
        }
    }
</script>
