export type AppColorMode = 'light' | 'dark';

type DesignTokens = {
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
        secondaryActive: string;
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
};

const sharedTypography = {
    headingFamily: 'Inter, system-ui, sans-serif',
    bodyFamily: 'Inter, system-ui, sans-serif',
    monoFamily: '"IBM Plex Mono", "SFMono-Regular", Consolas, monospace',
};

/** Design token font-size scale (from chatllm token export) */
export const fontSize = {
    micro: '8px',
    xxs:   '10px',
    xs:    '11px',
    sm:    '12px',
    md:    '13px',
    base:  '14px',
    lg:    '15px',
    xl:    '16px',
    '2xl': '18px',
    '3xl': '20px',
    '4xl': '25px',
    '5xl': '36px',
} as const;

/** Design token font-weight scale */
export const fontWeight = {
    regular:  400,
    medium:   500,
    semibold: 600,
    bold:     700,
} as const;

/** Design token line-height scale */
export const lineHeight = {
    tight:   1.2,
    normal:  1.5,
    relaxed: 1.6,
} as const;

const lightTokens: DesignTokens = {
    background: {
        app: '#F3F6FA',
        canvas: '#FFFFFF',
        sidebar: '#F7F9FC',
        elevated: '#FFFFFF',
        overlay: 'rgba(255, 255, 255, 0.88)',
    },
    surface: {
        primary: '#FFFFFF',
        secondary: '#F1F4F9',
        tertiary: '#F8FAFC',
        accent: '#EFF6FF',
    },
    accent: {
        primary: '#0d9488',
        primaryHover: '#14b8a6',
        primaryActive: '#0f766e', // darker teal — used for split-button toggle side
        secondary: '#f59e0b',
        secondaryHover: '#D99A25',
        secondaryActive: '#d97706', // dark amber — used for agent mode split-button toggle
    },
    text: {
        primary: '#0F172A',
        secondary: '#64748B',
        muted: '#94A3B8',
        inverse: '#F8FAFC',
    },
    border: {
        subtle: '#E2E8F0',
        strong: '#CBD5E1',
        accent: '#94A3B8',
    },
    status: {
        success: '#22C55E',
        error: '#EF4444',
        warning: '#D19A1E',
        info: '#3B82F6',
    },
    shadow: {
        soft: '0 10px 30px rgba(15, 23, 42, 0.06)',
        medium: '0 16px 44px rgba(15, 23, 42, 0.10)',
        strong: '0 22px 64px rgba(15, 23, 42, 0.14)',
    },
    radius: {
        sm: 12,
        md: 18,
        lg: 24,
        pill: 999,
    },
    typography: sharedTypography,
};

const darkTokens: DesignTokens = {
    background: {
        app: '#060B18',
        canvas: '#0A1224',
        sidebar: '#0B1326',
        elevated: '#111B33',
        overlay: 'rgba(6, 11, 24, 0.9)',
    },
    surface: {
        primary: '#111B33',
        secondary: '#16233F',
        tertiary: '#101A31',
        accent: '#1A2743',
    },
    accent: {
        primary: '#6E7BFF',
        primaryHover: '#5F6DEA',
        primaryActive: '#4A55C0', // darker indigo — used for split-button toggle side
        secondary: '#C89A2B',
        secondaryHover: '#AF841D',
        secondaryActive: '#9A7520', // dark amber — used for agent mode split-button toggle
    },
    text: {
        primary: '#EAF0FF',
        secondary: '#9AA8C1',
        muted: '#73839F',
        inverse: '#060B18',
    },
    border: {
        subtle: '#24324F',
        strong: '#314261',
        accent: '#42567A',
    },
    status: {
        success: '#34D399',
        error: '#F87171',
        warning: '#D6A93C',
        info: '#6E7BFF',
    },
    shadow: {
        soft: '0 12px 34px rgba(2, 6, 23, 0.45)',
        medium: '0 18px 50px rgba(2, 6, 23, 0.62)',
        strong: '0 26px 80px rgba(2, 6, 23, 0.72)',
    },
    radius: {
        sm: 12,
        md: 18,
        lg: 24,
        pill: 999,
    },
    typography: sharedTypography,
};

const designTokens: Record<AppColorMode, DesignTokens> = {
    light: lightTokens,
    dark: darkTokens,
};

const primary_color = lightTokens.accent.primary;
const primary_bg_color = lightTokens.background.canvas;
const secondary_color = lightTokens.surface.secondary;
const secondary_bg_color = lightTokens.background.app;

const nav_bg_color = lightTokens.background.sidebar;
const secondary_nav_color = lightTokens.accent.primary;
const primary_nav_color = lightTokens.text.secondary;
const primary_nav_selected_color = lightTokens.accent.primary;
const secondary_nav_selected_color = lightTokens.accent.primary;

const product_card_bg = lightTokens.surface.primary;
const discount_badge_color = lightTokens.status.error;
const product_hover_shadow = 'rgba(15, 23, 42, 0.10)';

export {
    designTokens,
    primary_color,
    primary_nav_color,
    secondary_color,
    secondary_bg_color,
    secondary_nav_color,
    primary_bg_color,
    nav_bg_color,
    primary_nav_selected_color,
    secondary_nav_selected_color,
    product_card_bg,
    discount_badge_color,
    product_hover_shadow
};
