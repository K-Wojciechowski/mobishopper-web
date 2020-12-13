export class LocalPermissionEntry {
    public id: number;
    public name: string;
    public can_manage_products: boolean;
    public can_manage_maps: boolean;
    public can_manage_deals: boolean;
    public can_manage_employees: boolean;
    public can_view_statistics: boolean;

    constructor() {
        this.id = -1;
        this.name = "";
        this.can_manage_products = false;
        this.can_manage_maps = false;
        this.can_manage_deals = false;
        this.can_manage_employees = false;
        this.can_view_statistics = false;
    }
}

export interface AppDataLPT extends AppData {
    lpTableTitles: Array<Array<string>>;
    lpEntries: LocalPermissionEntry[];
}

export interface Store {
    id: number;
    name: string;
    city: string;
    region_code: string;
}

export async function getStores(): Promise<Array<Store>> {
    const req = await fetch("/api/stores/");
    return req.json();
}
