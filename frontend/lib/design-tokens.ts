/**
 * Design tokens mirrored in styles/theme.css (:root).
 * Use for JS layout (e.g. shell); prefer CSS variables in components.
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
  pageGap: 12,
  cardPadding: 12,
  cardPaddingLg: 14,
  radius: {
    sm: 6,
    md: 8,
    lg: 10,
  },
  containerMax: 1440,
  sidebarWidth: 220,
  sidebarWidthCollapsed: 56,
  kpiHeight: 88,
  kpiValueSize: 22,
  tableRowHeight: 40,
  tableCellPaddingY: 8,
  tableCellPaddingX: 12,
  typography: {
    xs: 11,
    sm: 12,
    md: 13,
    lg: 14,
    xl: 16,
    pageTitle: 18,
    sectionTitle: 13,
    metric: 22,
  },
} as const;
