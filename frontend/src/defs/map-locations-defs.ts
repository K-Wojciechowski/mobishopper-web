export interface Aisle {
    id: number;
    name: string;
    code: string;
    description: string;
    date_started: string;
    date_ended: string;
}

export interface Subaisle {
    id: number;
    name: string;
    code: string;
    display_code: string;
    description: string;
    visible: boolean;
    parent: Aisle;
    subcategories: Subcategory[];
}

export interface Category {
    id: number;
    name: string;
    description: string;
    visible: string;
}

export interface Subcategory {
    id: number;
    name: string;
    description: string;
    visible: boolean;
    parent: Category;
}

export interface SubcategoryStructureEntry {
    id: number;
    name: string;
}

export interface CategoryStructureEntry {
    id: number;
    name: string;
    subcategories: SubcategoryStructureEntry[];
}

export interface AisleStructureEntry {
    id: number;
    display_code: string;
    name: string;
    subaisles: Subaisle[];
}
