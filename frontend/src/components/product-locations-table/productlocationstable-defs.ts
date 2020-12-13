import {
AisleStructureEntry, CategoryStructureEntry, Subaisle, Subcategory,
} from "@/defs/map-locations-defs";
import {MapDTO, MapTile, MapTileDTO} from "@/components/store-map/storemap-defs";
import {getIsoDate} from "@/defs/date-handling";
import dayjs from "dayjs";

export interface AppDataPLT {
    getEndpoint: string;
    updateEndpoint: string;
    groupsEndpoint: string;
    defaultPageSize: number;
    initialView: string;
    categoryStructure: CategoryStructureEntry[];
}

export enum ProductLocationFilter {
    ALL = "all",
    AUTO = "auto",
    MANUAL = "manual",
    MISSING = "missing"
}

export interface ProductToLocate {
    id: number;
    name: string;
    vendor: string;
    vendor_details_url: string;
    date_started: string;
    date_ended: string;
    details_url: string;
    subcategory: Subcategory;
    location: ProductLocation | null;
}

export class ProductLocation {
    public id: number | null = null;
    public tile: MapTileDTO | MapTile | null = null;
    public subaisle: Subaisle | null = null;
    public is_auto: boolean = false;
    public date_started: string;
    public date_ended: string;

    constructor(id: number | null, tile: MapTileDTO | MapTile | null, subaisle: Subaisle | null,
                is_auto: boolean, date_started: string, date_ended: string) {
        this.id = id;
        this.tile = tile;
        this.subaisle = subaisle;
        this.is_auto = is_auto;
        this.date_started = date_started;
        this.date_ended = date_ended;
    }
}

export class ProductLocationChange {
    public product: ProductToLocate;
    public tile: MapTile | MapTileDTO | null = null;
    public subaisle: Subaisle | null = null;
    public start_tile: MapTile | MapTileDTO | null = null;
    public start_subaisle: Subaisle | null = null;
    public revert_auto: boolean = false;
    public delete_location: boolean = false;

    constructor(product: ProductToLocate, tile: MapTile | MapTileDTO | null = null, subaisle: Subaisle | null = null,
                start_tile: MapTile | MapTileDTO | null = null, start_subaisle: Subaisle | null = null,
                revert_auto: boolean = false, delete_location: boolean = false) {
        this.product = product;
        this.tile = tile;
        this.subaisle = subaisle;
        this.start_tile = start_tile;
        this.start_subaisle = start_subaisle;
        this.revert_auto = revert_auto;
        this.delete_location = delete_location;
    }

    public prepareForUpload(): ProductLocationChange {
        const product = {...this.product, location: null};
        let {tile} = this;
        if (this.tile !== null && "tileType" in this.tile) {
            tile = MapTileDTO.fromMapTile(this.tile);
        }
        return new ProductLocationChange(product, tile, this.subaisle, null, null, this.revert_auto,
                                         this.delete_location);
    }

    public static fromProduct(product: ProductToLocate): ProductLocationChange {
        const tile = product.location?.tile;
        const subaisle = product.location?.subaisle;
        return new ProductLocationChange(product, tile, subaisle, tile, subaisle);
    }

    public hasChanges(): boolean {
        return this.hasValueChanges() || this.hasExtrasChanges();
    }

    public hasValueChanges(): boolean {
        return this.tile?.id !== this.start_tile?.id || this.subaisle?.id !== this.start_subaisle?.id;
    }

    public hasExtrasChanges(): boolean {
        return this.revert_auto || this.delete_location;
    }
}

export class ProductLocationsTableItem {
    public product: ProductToLocate;
    public change: ProductLocationChange;

    constructor(product: ProductToLocate, change: ProductLocationChange) {
        this.product = product;
        this.change = change;
    }
}

export interface ProductLocationGetResponse {
    products: ProductToLocate[];
    page: number;
    totalPages: number;
    filter: ProductLocationFilter;
}

export interface ProductGroupsGetResponse {
    map: MapDTO;
    tiles: MapTileDTO[];
    categoryStructure: CategoryStructureEntry[];
    aisleStructure: AisleStructureEntry[];
    subaisles: Subaisle[];
}

export interface ProductLocationChangeDescription {
    date: string;
    changes: ProductLocationChange[];
}

export interface ProductLocationChangeResponse {
    success: boolean;
    message: string;
    warning: boolean;
}

export async function getProducts(endpoint: string, filter: ProductLocationFilter, name: string,
                                  vendor: string, subcategory: number, validAt: string | dayjs.Dayjs,
                                  pageNumber: number, pageSize: number): Promise<ProductLocationGetResponse> {
    const url: URL = new URL(endpoint, document.location.toString());
    if (name.trim().length > 0) {
        url.searchParams.set("q", name.trim());
    }
    if (vendor.trim().length > 0) {
        url.searchParams.set("vendor", vendor.trim());
    }
    if (subcategory > 0) {
        url.searchParams.set("subcategory", subcategory.toString());
    }
    url.searchParams.set("validAt", getIsoDate(validAt));
    url.searchParams.set("page", pageNumber.toString());
    url.searchParams.set("page_size", pageSize.toString());
    url.searchParams.set("filter", filter);

    const req = await fetch(url.toString(), {credentials: "same-origin"});
    return req.json();
}

export async function getProductGroups(endpoint: string,
                                       validAt: string | dayjs.Dayjs): Promise<ProductGroupsGetResponse> {
    const url: URL = new URL(endpoint, document.location.toString());
    url.searchParams.set("validAt", getIsoDate(validAt));
    const req = await fetch(url.toString(), {credentials: "same-origin"});
    return req.json();
}

export async function saveChanges(endpoint: string, changes: ProductLocationChange[],
                                  date: string | dayjs.Dayjs): Promise<ProductLocationChangeResponse> {
    const data: ProductLocationChangeDescription = {changes, date: getIsoDate(date)};
    const body = JSON.stringify(data);
    const csrftoken = (document.querySelector("[name=csrfmiddlewaretoken]") as HTMLInputElement).value;
    const headers = new Headers();
    headers.set("X-CSRFToken", csrftoken);
    const req = await fetch(endpoint, {
        credentials: "same-origin",
        method: "POST",
        body,
        headers,
    });
    return req.json();
}

export const FILTER_OPTIONS: [ProductLocationFilter, string][] = [
    [ProductLocationFilter.ALL, gettext("Show all")],
    [ProductLocationFilter.AUTO, gettext("Auto-assigned")],
    [ProductLocationFilter.MANUAL, gettext("Manually assigned")],
    [ProductLocationFilter.MISSING, gettext("Missing location")],
];
