/**
 * Layout constants mirrored in styles/theme.css + styles/typography.css.
 * Prefer CSS variables in components; use this for JS layout math only.
 */
export const designTokens = {
  spacing: {
    0: 0,
    1: 4,
    2: 8,
    3: 12,
    4: 16,
    5: 20,
    6: 24,
  },
  sectionGap: 12,
  pageGap: 16,
  cardPadding: 16,
  cardPaddingLg: 20,
  radius: {
    sm: 6,
    md: 8,
    lg: 10,
    xl: 12,
  },
  containerMax: 1440,
  sidebarWidth: 240,
  sidebarWidthCollapsed: 64,
  topbarHeight: 56,
  kpiHeight: 88,
  kpiMinHeight: 96,
  tableRowHeight: 44,
  tableCellPaddingY: 10,
  tableCellPaddingX: 14,
  /** Persian-first scale (fa); en uses smaller values in typography.css */
  typography: {
    fa: {
      xs: 12,
      sm: 14,
      md: 15,
      pageTitle: 23,
      sectionTitle: 15,
      metric: 28,
      lineHeightBody: 1.8,
      lineHeightCompact: 1.6,
    },
    en: {
      xs: 11,
      sm: 13,
      md: 14,
      pageTitle: 22,
      sectionTitle: 14,
      metric: 28,
      lineHeightBody: 1.55,
      lineHeightCompact: 1.45,
    },
  },
} as const;
