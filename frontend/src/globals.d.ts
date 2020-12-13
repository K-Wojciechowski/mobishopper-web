declare interface AppData {
    THIS_APP: string;
    APP_TAG: string;
}

declare let VUE_APPS: AppData[];
declare function gettext(text: string): string;
