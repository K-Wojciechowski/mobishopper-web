export class MetaValue {
    public slug: string = "";
    public name: string = "";
    public value: string = "";
    public units: string = "";
    public text: string = "";

    constructor(slug: string, name: string, value: string, units: string, text: string) {
        this.slug = slug;
        this.name = name;
        this.value = value;
        this.units = units;
        this.text = text;
    }
}

export class InternalMetaValue extends MetaValue {
    public id: number = 0;
    public standardMetaField: StandardMetaField | null = null;

    constructor(slug: string = "", name: string = "", value: string = "", units: string = "", text: string = "",
                id: number = -1, standardMetaField: StandardMetaField | null = null) {
        super(slug, name, value, units, text);
        this.id = id;
        this.standardMetaField = standardMetaField;
    }

    public static toInternal(mv: MetaValue, newId: number,
                             standardMetaField: StandardMetaField | null = null): InternalMetaValue {
        return new InternalMetaValue(mv.slug, mv.name, mv.value, mv.units, mv.text, newId, standardMetaField);
    }

    public toGeneral(): MetaValue {
        const slug = this.slug.startsWith("__") ? "" : this.slug;
        return new MetaValue(slug, this.name, this.value, this.units, this.text);
    }

    public updateText() {
        if (this.standardMetaField?.expected_units === "_str" || this.standardMetaField?.expected_units === "_number") {
            this.text = this.value;
        } else if (this.standardMetaField?.expected_units === "_bool") {
            this.text = this.value === "1" ? gettext("yes") : gettext("no");
        } else if (this.units !== "") {
            this.text = `${this.value} ${this.units}`;
        } else {
            this.text = this.value;
        }
    }
}

export class StandardMetaField {
    public slug: string = "";
    public name: string = "";
    public expected_units: string = "";
    public expected_units_names: string[] = [];
    public is_required: boolean = false;
    public is_recommended: boolean = false;
}

export class StandardMetaFieldContainer {
    public items: StandardMetaField[] = [];
    public subcategory: number | null = null;

    constructor(items: StandardMetaField[] = [], subcategory: number | null = null) {
        this.items = items;
        this.subcategory = subcategory;
    }
}

export async function getStandardFields(url: string, subcategory: number | null): Promise<StandardMetaFieldContainer> {
    let theUrl = url;
    if (subcategory !== null) {
        theUrl += `${subcategory}/`;
    }
    const req = await fetch(theUrl, {credentials: "same-origin"});
    return req.json();
}

export interface AppDataEME extends AppData {
    emeApiEndpoint: string;
    emeUseSubcategory: boolean;
    emeHighlightCustom: boolean;
    emeInitialData: MetaValue[];
}

export const EXPECTED_UNITS = {
    NUMBER: "_number",
    STR: "_str",
    BOOL: "_bool",
    USER: "_user",
    WEIGHT: "weight",
    VOLUME: "volume",
    AREA: "area",
    SIZE: "size",
};

export const EXPECTED_UNITS_CHECK = {
    TEXT: (val: string | null, names: string[]) => (
        val === "_number" || val === "_str" || (val === "_user" && names.length === 0)),
    BOOL: (val: string | null) => val === "_bool",
    SELECT_UNIT: (val: string | null, names: string[]) => (
        (val === "_user" && names.length !== 0) || (val !== null && !val.startsWith("_"))),
};
