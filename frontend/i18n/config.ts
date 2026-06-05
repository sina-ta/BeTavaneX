import { enCommon } from "@/i18n/en/common";
import { faCommon } from "@/i18n/fa/common";

export const supportedLocales = ["en", "fa"] as const;

export type Locale = (typeof supportedLocales)[number];
export type Direction = "ltr" | "rtl";
export type CommonMessageKey = keyof typeof enCommon;

export const defaultLocale: Locale = "fa";
export const localeStorageKey = "betavanx.locale";

export const localeDirections: Record<Locale, Direction> = {
  en: "ltr",
  fa: "rtl",
};

export const messages: Record<
  Locale,
  Record<CommonMessageKey, string>
> = {
  en: enCommon,
  fa: faCommon,
};
