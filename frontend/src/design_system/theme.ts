import { alpha, createTheme } from '@mui/material/styles';
import { designTokens, fontSize, fontWeight, lineHeight, type AppColorMode } from './colors.ts';

export const createAppTheme = (mode: AppColorMode = 'light') => {
    const tokens = designTokens[mode];
    const appDesign = {
        mode,
        ...tokens,
        typographyScale: {
            micro:  { size: fontSize.micro,  weight: fontWeight.regular,  lineHeight: lineHeight.normal },
            xxs:    { size: fontSize.xxs,    weight: fontWeight.semibold, lineHeight: lineHeight.normal },
            xs:     { size: fontSize.xs,     weight: fontWeight.medium,   lineHeight: lineHeight.normal },
            sm:     { size: fontSize.sm,     weight: fontWeight.regular,  lineHeight: lineHeight.relaxed },
            md:     { size: fontSize.md,     weight: fontWeight.semibold, lineHeight: lineHeight.normal },
            base:   { size: fontSize.base,   weight: fontWeight.regular,  lineHeight: lineHeight.relaxed },
            lg:     { size: fontSize.lg,     weight: fontWeight.medium,   lineHeight: lineHeight.normal },
            xl:     { size: fontSize.xl,     weight: fontWeight.semibold, lineHeight: lineHeight.normal },
            '2xl':  { size: fontSize['2xl'], weight: fontWeight.semibold, lineHeight: lineHeight.tight },
            '3xl':  { size: fontSize['3xl'], weight: fontWeight.semibold, lineHeight: lineHeight.tight },
            '4xl':  { size: fontSize['4xl'], weight: fontWeight.bold,     lineHeight: lineHeight.tight },
            '5xl':  { size: fontSize['5xl'], weight: fontWeight.bold,     lineHeight: lineHeight.tight },
        },
    };

    const theme = createTheme({
        shape: {
            borderRadius: tokens.radius.md,
        },
        spacing: 8,
        typography: {
            // Base family — Inter for all variants
            fontFamily: tokens.typography.bodyFamily,

            // ── Display / Headings ──────────────────────────────────
            // h1  → 5xl  36px  bold(700)     tight(1.2)
            h1: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize['5xl'],
                fontWeight: fontWeight.bold,
                lineHeight: lineHeight.tight,
                letterSpacing: '-0.02em',
            },
            // h2  → 4xl  25px  bold(700)     tight(1.2)
            h2: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize['4xl'],
                fontWeight: fontWeight.bold,
                lineHeight: lineHeight.tight,
                letterSpacing: '-0.015em',
            },
            // h3  → 3xl  20px  semibold(600) tight(1.2)
            h3: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize['3xl'],
                fontWeight: fontWeight.semibold,
                lineHeight: lineHeight.tight,
                letterSpacing: '-0.01em',
            },
            // h4  → 2xl  18px  semibold(600) tight(1.2)
            h4: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize['2xl'],
                fontWeight: fontWeight.semibold,
                lineHeight: lineHeight.tight,
            },
            // h5  → xl   16px  semibold(600) normal(1.5)
            h5: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.xl,
                fontWeight: fontWeight.semibold,
                lineHeight: lineHeight.normal,
            },
            // h6  → lg   15px  semibold(600) normal(1.5)
            h6: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.lg,
                fontWeight: fontWeight.semibold,
                lineHeight: lineHeight.normal,
            },

            // ── Body ────────────────────────────────────────────────
            // body1 → base  14px  regular(400)  relaxed(1.6)
            body1: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.base,
                fontWeight: fontWeight.regular,
                lineHeight: lineHeight.relaxed,
            },
            // body2 → sm    12px  regular(400)  relaxed(1.6)
            body2: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.sm,
                fontWeight: fontWeight.regular,
                lineHeight: lineHeight.relaxed,
            },

            // ── UI Text ─────────────────────────────────────────────
            // subtitle1 → lg    15px  medium(500)   normal(1.5)
            subtitle1: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.lg,
                fontWeight: fontWeight.medium,
                lineHeight: lineHeight.normal,
            },
            // subtitle2 → base  14px  medium(500)   normal(1.5)
            subtitle2: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.base,
                fontWeight: fontWeight.medium,
                lineHeight: lineHeight.normal,
            },
            // button → md  13px  semibold(600)  normal(1.5)
            button: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.md,
                fontWeight: fontWeight.semibold,
                lineHeight: lineHeight.normal,
                textTransform: 'none',
            },
            // caption → xs  11px  medium(500)  normal(1.5)
            caption: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.xs,
                fontWeight: fontWeight.medium,
                lineHeight: lineHeight.normal,
            },
            // overline → xxs  10px  semibold(600)  normal(1.5)
            overline: {
                fontFamily: tokens.typography.bodyFamily,
                fontSize: fontSize.xxs,
                fontWeight: fontWeight.semibold,
                lineHeight: lineHeight.normal,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
            },
        },
        palette: {
            mode,
            brand: {
                main: tokens.accent.primary,
                light: alpha(tokens.accent.primary, 0.82),
                dark: tokens.accent.primaryActive,
                contrastText: tokens.text.inverse,
            },
            nav_bg: {
                main: tokens.background.sidebar,
                light: tokens.background.sidebar,
                dark: tokens.background.canvas,
                contrastText: tokens.text.primary,
            },
            primary_nav_options: {
                main: tokens.text.secondary,
                light: tokens.text.secondary,
                dark: tokens.text.secondary,
                contrastText: tokens.text.primary,
            },
            secondary_nav_options: {
                main: tokens.accent.primary,
                light: tokens.accent.primary,
                dark: tokens.accent.primaryHover,
                contrastText: tokens.text.inverse,
            },
            primary_nav_options_selected: {
                main: tokens.accent.primary,
                light: tokens.accent.primary,
                dark: tokens.accent.primaryHover,
                contrastText: tokens.text.inverse,
            },
            secondary_nav_options_selected: {
                main: tokens.accent.secondary,
                light: tokens.accent.secondary,
                dark: tokens.accent.secondaryHover,
                contrastText: tokens.text.inverse,
            },
            primary: {
                main: tokens.accent.primary,
                light: tokens.accent.primaryHover,
                dark: tokens.accent.primaryActive,
                contrastText: tokens.text.inverse,
            },
            secondary: {
                main: tokens.accent.secondary,
                light: alpha(tokens.accent.secondary, 0.84),
                dark: tokens.accent.secondaryHover,
                contrastText: tokens.text.inverse,
            },
            primary_bg: {
                main: tokens.background.canvas,
                light: tokens.background.canvas,
                dark: tokens.background.elevated,
                contrastText: tokens.text.primary,
            },
            secondary_bg: {
                main: tokens.background.app,
                light: tokens.surface.secondary,
                dark: tokens.surface.secondary,
                contrastText: tokens.text.primary,
            },
            background: {
                default: tokens.background.app,
                paper: tokens.surface.primary,
            },
            text: {
                primary: tokens.text.primary,
                secondary: tokens.text.secondary,
                disabled: tokens.text.muted,
            },
            divider: tokens.border.subtle,
            error: {
                main: tokens.status.error,
            },
            warning: {
                main: tokens.status.warning,
            },
            success: {
                main: tokens.status.success,
            },
            info: {
                main: tokens.status.info,
            },
        },
        components: {
            MuiCssBaseline: {
                styleOverrides: {
                    ':root': {
                        colorScheme: mode,
                        '--app-bg': tokens.background.app,
                        '--app-canvas': tokens.background.canvas,
                        '--app-sidebar': tokens.background.sidebar,
                        '--surface-primary': tokens.surface.primary,
                        '--surface-secondary': tokens.surface.secondary,
                        '--surface-tertiary': tokens.surface.tertiary,
                        '--accent-primary': tokens.accent.primary,
                        '--accent-primary-hover': tokens.accent.primaryHover,
                        '--accent-secondary': tokens.accent.secondary,
                        '--text-primary': tokens.text.primary,
                        '--text-secondary': tokens.text.secondary,
                        '--text-muted': tokens.text.muted,
                        '--border-subtle': tokens.border.subtle,
                        '--border-strong': tokens.border.strong,
                        '--status-success': tokens.status.success,
                        '--status-error': tokens.status.error,
                        '--status-warning': tokens.status.warning,
                        '--shadow-soft': tokens.shadow.soft,
                        '--shadow-medium': tokens.shadow.medium,
                        '--input-bg': tokens.surface.tertiary,
                        '--input-border': tokens.border.subtle,
                        '--input-placeholder': tokens.text.muted,
                        '--radius-sm': `${tokens.radius.sm}px`,
                        '--radius-md': `${tokens.radius.md}px`,
                        '--radius-lg': `${tokens.radius.lg}px`,
                        // ── Font token CSS vars ──
                        '--font-family': tokens.typography.bodyFamily,
                        '--font-size-micro': fontSize.micro,
                        '--font-size-xxs':   fontSize.xxs,
                        '--font-size-xs':    fontSize.xs,
                        '--font-size-sm':    fontSize.sm,
                        '--font-size-md':    fontSize.md,
                        '--font-size-base':  fontSize.base,
                        '--font-size-lg':    fontSize.lg,
                        '--font-size-xl':    fontSize.xl,
                        '--font-size-2xl':   fontSize['2xl'],
                        '--font-size-3xl':   fontSize['3xl'],
                        '--font-size-4xl':   fontSize['4xl'],
                        '--font-size-5xl':   fontSize['5xl'],
                        '--font-weight-regular':  String(fontWeight.regular),
                        '--font-weight-medium':   String(fontWeight.medium),
                        '--font-weight-semibold': String(fontWeight.semibold),
                        '--font-weight-bold':     String(fontWeight.bold),
                        '--line-height-tight':    String(lineHeight.tight),
                        '--line-height-normal':   String(lineHeight.normal),
                        '--line-height-relaxed':  String(lineHeight.relaxed),
                    },
                    'html, body, #root': {
                        minHeight: '100%',
                        backgroundColor: tokens.background.app,
                    },
                    body: {
                        background: tokens.background.app,
                        color: tokens.text.primary,
                    },
                    '::selection': {
                        backgroundColor: alpha(tokens.accent.primary, 0.28),
                        color: tokens.text.primary,
                    },
                },
            },
        },
    });

    Object.assign(theme, { appDesign });

    return theme;
};

const app_theme = createAppTheme('light');

export default app_theme;
