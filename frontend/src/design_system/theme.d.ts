import '@mui/material/styles';

declare module '@mui/material/styles' {
  interface AppTypographyScale {
    micro:  { size: string; weight: number; lineHeight: number };
    xxs:    { size: string; weight: number; lineHeight: number };
    xs:     { size: string; weight: number; lineHeight: number };
    sm:     { size: string; weight: number; lineHeight: number };
    md:     { size: string; weight: number; lineHeight: number };
    base:   { size: string; weight: number; lineHeight: number };
    lg:     { size: string; weight: number; lineHeight: number };
    xl:     { size: string; weight: number; lineHeight: number };
    '2xl':  { size: string; weight: number; lineHeight: number };
    '3xl':  { size: string; weight: number; lineHeight: number };
    '4xl':  { size: string; weight: number; lineHeight: number };
    '5xl':  { size: string; weight: number; lineHeight: number };
  }

  interface AppDesignTokens {
    mode: 'light' | 'dark';
    background: {
      app: string;
      canvas: string;
      sidebar: string;
      elevated: string;
      overlay: string;
    };
    surface: {
      primary: string;
      secondary: string;
      tertiary: string;
      accent: string;
    };
    accent: {
      primary: string;
      primaryHover: string;
      primaryActive: string;
      secondary: string;
      secondaryHover: string;
    };
    text: {
      primary: string;
      secondary: string;
      muted: string;
      inverse: string;
    };
    border: {
      subtle: string;
      strong: string;
      accent: string;
    };
    status: {
      success: string;
      error: string;
      warning: string;
      info: string;
    };
    shadow: {
      soft: string;
      medium: string;
      strong: string;
    };
    radius: {
      sm: number;
      md: number;
      lg: number;
      pill: number;
    };
    typography: {
      headingFamily: string;
      bodyFamily: string;
      monoFamily: string;
    };
    typographyScale: AppTypographyScale;
  }

  interface Palette {
    brand: Palette['primary'];
    nav_bg: Palette['primary'];
    primary_nav_options: Palette['primary'];
    secondary_nav_options: Palette['primary'];
    primary_nav_options_selected: Palette['primary'];
    secondary_nav_options_selected: Palette['primary'];
    primary_bg: Palette['primary'];
    secondary_bg: Palette['primary'];
  }

  interface PaletteOptions {
    brand?: PaletteOptions['primary'];
    nav_bg?: PaletteOptions['primary'];
    primary_nav_options?: PaletteOptions['primary'];
    secondary_nav_options?: PaletteOptions['primary'];
    primary_nav_options_selected?: PaletteOptions['primary'];
    secondary_nav_options_selected?: PaletteOptions['primary'];
    primary_bg?: PaletteOptions['primary'];
    secondary_bg?: PaletteOptions['primary'];
  }

  interface Theme {
    appDesign: AppDesignTokens;
  }

  interface ThemeOptions {
    appDesign?: AppDesignTokens;
  }
}

