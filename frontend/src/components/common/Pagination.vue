<template>
    <nav :aria-label="getText('Page navigation')" class="ms-pagination" v-if="this.maxPages > 1">
        <ul class="pagination">
            <li class="page-item">
                <button type="button" class="page-link" @click="$emit('back')"
                        :aria-label="getText('Previous')" :disabled="!canGoBack()">
                    <span aria-hidden="true">&laquo;</span>
                    <span class="sr-only">{{ getText("Previous") }}</span>
                </button>
            </li>
            <li class="page-item"><span class="page-link">{{ this.currentPage }}/{{ this.maxPages }}</span></li>
            <li class="page-item">
                <button type="button" class="page-link" @click="$emit('forward')"
                        :aria-label="getText('Next')" :disabled="!canGoForward()">
                    <span aria-hidden="true">&raquo;</span>
                    <span class="sr-only">{{ getText("Next") }}</span>
                </button>
            </li>
        </ul>
    </nav>
</template>

<script lang="ts">
import {Component, Prop, Vue} from "vue-property-decorator";

@Component
export default class Pagination extends Vue {
    @Prop() private currentPage!: number;
    @Prop() private maxPages!: number;

    canGoBack(): boolean {
        return this.currentPage > 1;
    }

    canGoForward(): boolean {
        return this.currentPage < this.maxPages;
    }
}
</script>
