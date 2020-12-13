<template>
    <span v-html="getValidityText()"></span>
</template>

<script lang="ts">
    import {Component, Prop, Vue} from "vue-property-decorator";
    import dayjs from "dayjs";
    import {DATE_FORMAT} from "@/defs/constants";

    @Component
    export default class ValidityText extends Vue {
        @Prop() private started!: string | dayjs.Dayjs | null;

        @Prop() private ended!: string | dayjs.Dayjs | null;

        startedDate(): dayjs.Dayjs | null {
            if (typeof this.started === "string") {
                return dayjs(this.started);
            }
            return this.started;
        }

        endedDate(): dayjs.Dayjs | null {
            if (typeof this.ended === "string") {
                return dayjs(this.ended);
            }
            return this.ended;
        }

        getValidityText(): string {
            const start = this.startedDate();
            const end = this.endedDate();
            if (start == null && end == null) {
                return gettext("indefinitely");
            }
            let out = "";
            if (start != null) {
                out += gettext("from {date}").replace("{date}", start.format(DATE_FORMAT));
            }
            if (start != null && end != null) {
                out += "<br>";
            }
            if (end != null) {
                out += gettext("until {date}").replace("{date}", end.format(DATE_FORMAT));
            }
            return out;
        }
    }
</script>
