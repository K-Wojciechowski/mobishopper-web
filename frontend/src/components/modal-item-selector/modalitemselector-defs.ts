export class ModalItem {
    public id: number = -1;
    public name: string = "";
    public details_url: string = "";
    public photo: string | null = null;
    public extras: string[] = [];

    constructor(id: number, name: string, details_url: string, photo: string | null = null, extras: string[] = []) {
        this.id = id;
        this.name = name;
        this.photo = photo;
        this.details_url = details_url;
        this.extras = extras;
    }
}

export class ModalItemContainer {
    public items: ModalItem[] = [];
    public page: number = 1;
    public num_pages: number = 1;
}

export async function getModalItems(endpoint: string, page: number, query: string): Promise<ModalItemContainer> {
    const url = new URL(endpoint, document.location.toString());
    url.searchParams.set("q", query);
    url.searchParams.set("page", page.toString());
    const req = await fetch(url.toString(), {credentials: "same-origin"});
    return req.json();
}

export interface AppDataMIS extends AppData {
    misApiEndpoint: string;
    misTitle: string;
    misItemName: string;
    misModalId: string;
    misInputName: string;
    misRequired: boolean;
    misExtraFieldNames: string[];
    misMultipleSelection: boolean;
    misInitialSelection: ModalItem[];
}
