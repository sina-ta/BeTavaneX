"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  defaultLocale,
  localeDirections,
  localeStorageKey,
  messages,
  type CommonMessageKey,
  type Direction,
  type Locale,
} from "@/i18n/config";

type LanguageContextValue = {
  locale: Locale;
  direction: Direction;
  setLocale: (locale: Locale) => void;
  t: (key: CommonMessageKey) => string;
};

const LanguageContext =
  createContext<LanguageContextValue | null>(null);

function getInitialLocale(): Locale {
  if (typeof window === "undefined") {
    return defaultLocale;
  }

  const storedLocale = window.localStorage.getItem(
    localeStorageKey
  );

  if (storedLocale === "fa" || storedLocale === "en") {
    return storedLocale;
  }

  const browserLocale = window.navigator.language.toLowerCase();
  if (browserLocale.startsWith("fa")) {
    return "fa";
  }

  return defaultLocale;
}

export function LanguageProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [locale, setLocale] = useState<Locale>(defaultLocale);

  useEffect(() => {
    setLocale(getInitialLocale());
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(localeStorageKey, locale);
    }

    const direction = localeDirections[locale];
    document.documentElement.lang = locale;
    document.documentElement.dir = direction;
    document.body.dataset.locale = locale;
  }, [locale]);

  const t = useCallback(
    (key: CommonMessageKey) =>
      messages[locale][key] ?? messages.en[key] ?? key,
    [locale]
  );

  const value = useMemo(
    () => ({
      locale,
      direction: localeDirections[locale],
      setLocale,
      t,
    }),
    [locale, t]
  );

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(LanguageContext);

  if (!context) {
    throw new Error(
      "useI18n must be used within LanguageProvider"
    );
  }

  return context;
}
