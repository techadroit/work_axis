import type {PaletteColor, PaletteColorOptions} from "@mui/material";

declare module '@mui/material/styles' {

    interface Palette {
        brand: PaletteColor;
        nav_bg: PaletteColor;
        primary_nav_options: PaletteColor;
        secondary_nav_options: PaletteColor;
        primary_nav_options_selected: PaletteColor;
        secondary_nav_options_selected: PaletteColor;
        primary_bg: PaletteColor;
        secondary_bg: PaletteColor;
    }

    interface PaletteOptions {
        brand: PaletteColorOptions;
        nav_bg: PaletteColorOptions;
        primary_nav_options: PaletteColorOptions;
        secondary_nav_options: PaletteColorOptions;
        primary_nav_options_selected: PaletteColorOptions;
        secondary_nav_options_selected: PaletteColorOptions;
        primary_bg: PaletteColorOptions;
        secondary_bg: PaletteColorOptions;
    }
}

declare module '@mui/material/Button' {
    interface ButtonPropsColorOverrides {
        primary_nav_options: true;
        secondary_nav_options: true;
        primary_nav_options_selected: true;
        secondary_nav_options_selected: true;
        primary_bg: true;
        secondary_bg: true;
    }
}

declare module '@mui/material/AppBar' {
    interface AppBarPropsColorOverrides {
        nav_bg: true;
    }
}