"use client";

import { usePathname } from "next/navigation";

import { useI18n } from "@/i18n/LanguageProvider";
import { getPageTitleFromPath } from "@/lib/navigation";

export default function Topbar() {
  const pathname = usePathname();
  const { locale, setLocale, t } = useI18n();
  const pageTitleKey = getPageTitleFromPath(pathname);

  return (
    <header className="topbar">
      <div className="topbar-left">
        <span className="topbar-breadcrumb">
          {t("topbar_breadcrumb")}
        </span>
        <h1 className="topbar-title">{t(pageTitleKey)}</h1>
      </div>

      <div className="topbar-center">
        <input
          type="search"
          className="topbar-search"
          placeholder={t("topbar_search_placeholder")}
          aria-label={t("topbar_search_placeholder")}
        />
      </div>

      <div className="topbar-right">
        <div className="language-switcher">
          <button
            type="button"
            className={`language-switcher-btn ${
              locale === "en"
                ? "language-switcher-btn--active"
                : ""
            }`}
            onClick={() => setLocale("en")}
          >
            {t("language_en")}
          </button>
          <button
            type="button"
            className={`language-switcher-btn ${
              locale === "fa"
                ? "language-switcher-btn--active"
                : ""
            }`}
            onClick={() => setLocale("fa")}
          >
            {t("language_fa")}
          </button>
        </div>
        <span className="topbar-chip">
          {t("topbar_project_label")}
        </span>
        <span className="topbar-chip">{t("topbar_today")}</span>
        <button
          type="button"
          className="topbar-icon-btn"
          aria-label={t("topbar_notifications")}
        >
          🔔
        </button>
        <div
          className="topbar-avatar"
          title={t("topbar_operator")}
        >
          OP
        </div>
      </div>
    </header>
  );
}
