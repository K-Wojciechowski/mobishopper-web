import {AisleStructureEntry, Subaisle} from "@/defs/map-locations-defs";
import {
    getTileTypeName,
    MapTile,
    MapTileDTO,
    TileType,
} from "@/components/store-map/storemap-defs";
import uniqolor from "uniqolor";

export enum LegendEntryType {
    SECTION_HEADER,
    AISLE,
    SUBAISLE,
    SPECIAL_TILE
}

export enum ColorKey {
    UNKNOWN = -1,
    ENTRANCE = -2,
    EXIT = -3,
    ENTRANCE_EXIT = -4,
    REGISTER = -5,
    PRODUCT = -6,
    SUBAISLE = -7,
    BLOCK = -8,
    SPACE = 0
}

export class ColorSpec {
    color: string;
    isLight: boolean;

    constructor(color: string, isLight: boolean) {
        this.color = color;
        this.isLight = isLight;
    }
}

export class LegendEntry {
    title: string;
    key: string;
    color: ColorSpec | null = null;
    id: number | null = null;
    type: LegendEntryType;
    tileType: TileType | null = null;
    subaisle: Subaisle | null = null;
    canActivate: boolean = true;

    constructor(
        title: string, key: string, color: ColorSpec | null, id: number | null, type: LegendEntryType,
        tileType: TileType | null = null, subaisle: Subaisle | null = null, canActivate: boolean = true,
    ) {
        this.title = title;
        this.key = key;
        this.color = color;
        this.id = id;
        this.type = type;
        this.tileType = tileType;
        this.subaisle = subaisle;
        this.canActivate = canActivate;
    }
}

export function tileTypeToColor(tileType: TileType): ColorKey {
    switch (tileType) {
        case TileType.ENTRANCE:
            return ColorKey.ENTRANCE;
        case TileType.EXIT:
            return ColorKey.EXIT;
        case TileType.ENTRANCE_EXIT:
            return ColorKey.ENTRANCE_EXIT;
        case TileType.REGISTER:
            return ColorKey.REGISTER;
        case TileType.PRODUCT:
            return ColorKey.PRODUCT;
        case TileType.SUBAISLE:
            return ColorKey.SUBAISLE;
        case TileType.SPACE:
            return ColorKey.SPACE;
        case TileType.BLOCK:
            return ColorKey.BLOCK;
        default:
            return ColorKey.UNKNOWN;
    }
}

export const BASIC_COLORSPECS: Map<ColorKey, ColorSpec> = new Map();
BASIC_COLORSPECS.set(ColorKey.ENTRANCE, new ColorSpec("#3BF5C0", true));
BASIC_COLORSPECS.set(ColorKey.EXIT, new ColorSpec("#68DE2A", true));
BASIC_COLORSPECS.set(ColorKey.ENTRANCE_EXIT, new ColorSpec("#74F52F", true));
BASIC_COLORSPECS.set(ColorKey.REGISTER, new ColorSpec("#2A66DE", true));
BASIC_COLORSPECS.set(ColorKey.PRODUCT, new ColorSpec("#AF30FF", true));
BASIC_COLORSPECS.set(ColorKey.SPACE, new ColorSpec("#E9ECEF", true));
BASIC_COLORSPECS.set(ColorKey.SUBAISLE, new ColorSpec("#495057", false)); // Unusual condition
BASIC_COLORSPECS.set(ColorKey.BLOCK, new ColorSpec("#000000", false));
BASIC_COLORSPECS.set(ColorKey.UNKNOWN, new ColorSpec("#495057", false));

export function buildColorMap(aisles: AisleStructureEntry[]): Map<number, ColorSpec> {
    const colors = new Map();
    BASIC_COLORSPECS.forEach((v, k) => colors.set(k, v));
    aisles.forEach((aisle) => {
        aisle.subaisles.forEach((sa) => {
            colors.set(sa.id, uniqolor(sa.id + sa.name, {format: "hex"}));
        });
    });
    return colors;
}

export function buildLegend(aisles: AisleStructureEntry[], colors: Map<number, ColorSpec>): LegendEntry[] {
    const legend: LegendEntry[] = [];
    if (aisles.length > 0) {
        legend.push(new LegendEntry(gettext("Aisles"), "h1", null, null,
            LegendEntryType.SECTION_HEADER));
    }
    aisles.forEach((aisle) => {
        legend.push(new LegendEntry(aisle.name, `a${aisle.id}`, null, aisle.id,
            LegendEntryType.AISLE));
        aisle.subaisles.forEach((sa) => {
            legend.push(new LegendEntry(sa.name, `sa${sa.id}`, colors.get(sa.id) || null, sa.id,
                LegendEntryType.SUBAISLE, TileType.SUBAISLE, sa));
        });
    });
    legend.push(new LegendEntry(gettext("Special tiles"), "h2", null, null,
        LegendEntryType.SECTION_HEADER));

    function legendEntryFromTileType(tileType: TileType): LegendEntry {
        const text = getTileTypeName(tileType);
        const key = tileTypeToColor(tileType);
        return new LegendEntry(text, text, colors.get(key) || null, null, LegendEntryType.SPECIAL_TILE, tileType);
    }

    legend.push(legendEntryFromTileType(TileType.ENTRANCE));
    legend.push(legendEntryFromTileType(TileType.EXIT));
    legend.push(legendEntryFromTileType(TileType.ENTRANCE_EXIT));
    legend.push(legendEntryFromTileType(TileType.REGISTER));
    legend.push(legendEntryFromTileType(TileType.PRODUCT));
    legend.push(legendEntryFromTileType(TileType.SPACE));
    legend.push(legendEntryFromTileType(TileType.BLOCK));

    return legend;
}

export function getColorForTile(colors: Map<number, ColorSpec>, tile: MapTile): ColorSpec {
    let color: ColorSpec | undefined;
    if (tile.subaisle !== null) {
        color = colors.get(tile.subaisle.id);
    } else {
        color = colors.get(tileTypeToColor(tile.tileType));
    }
    if (color === undefined) {
        color = colors.get(ColorKey.UNKNOWN);
    }
    if (color === undefined) {
        throw new Error("Invalid color map");
    }
    return color;
}

export function getColorCSS(colorSpec: ColorSpec): string {
    const foregroundColor = colorSpec.isLight ? "black" : "white";
    return `background-color:${colorSpec.color};color:${foregroundColor}`;
}

export function getColorCSSForTile(colors: Map<number, ColorSpec>, tile: MapTile): string {
    return getColorCSS(getColorForTile(colors, tile));
}

export function tileToMapTileDTOWithColor(mt: MapTile, colors: Map<number, ColorSpec> | null): MapTileDTO {
    let color: string;
    let isLight: boolean;
    if (colors === null) {
        color = "#ff0000";
        isLight = true;
    } else {
        ({color, isLight} = getColorForTile(colors, mt));
    }
    return new MapTileDTO(mt.id, mt.x, mt.y, mt.tileType, mt.subaisle, color, isLight);
}
