"use client";

import { useEffect, useState } from "react";

import ActiveRoleContextBar from "@/components/layout/ActiveRoleContextBar";
import { initialsFromUsername } from "@/lib/auth/active-role-display";
import { getAuthUsername } from "@/lib/auth/session";
import { useI18n } from "@/i18n/LanguageProvider";

export default function Topbar() {
  const { locale, setLocale, t } = useI18n();
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    setUsername(getAuthUsername());
  }, []);

  return (
    <header className="topbar">
      <div className="topbar-brand">
        <div className="logo-circle">B</div>
        <div>
          <div className="topbar-brand-title">{t("app_name")}</div>
          <div className="topbar-brand-subtitle">{t("brand_subtitle")}</div>
        </div>
      </div>

      <div className="topbar-center">
        <div className="topbar-search-wrap">
          <input
            type="search"
            className="topbar-search"
            placeholder={t("topbar_search_placeholder")}
            aria-label={t("topbar_search_placeholder")}
          />
          <span className="topbar-search-hint" aria-hidden>
            {t("topbar_search_shortcut")}
          </span>
        </div>
      </div>

      <div className="topbar-right">
        <div className="language-switcher">
          <button
            type="button"
            className={`language-switcher-btn ${
              locale === "en" ? "language-switcher-btn--active" : ""
            }`}
            onClick={() => setLocale("en")}
          >
            {t("language_en")}
          </button>
          <button
            type="button"
            className={`language-switcher-btn ${
              locale === "fa" ? "language-switcher-btn--active" : ""
            }`}
            onClick={() => setLocale("fa")}
          >
            {t("language_fa")}
          </button>
        </div>

        <ActiveRoleContextBar />

        <div
          className="topbar-user"
          title={`${username ?? t("topbar_operator_manager")} — ${t("profile_role_switch_placeholder")}`}
          aria-label={`${username ?? t("topbar_operator_manager")}. ${t("profile_role_switch_placeholder")}`}
        >
          <div className="topbar-avatar">{initialsFromUsername(username)}</div>
          <span className="topbar-user-name">
            {username ?? t("topbar_operator_manager")}
          </span>
        </div>
      </div>
    </header>
  );
}
