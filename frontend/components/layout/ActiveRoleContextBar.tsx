"use client";

import { useI18n } from "@/i18n/LanguageProvider";
import {
  ROLE_MODE_MESSAGE_KEYS,
  ROLE_TITLE_MESSAGE_KEYS,
} from "@/lib/auth/active-role-display";
import { useActiveRole } from "@/lib/context/ActiveRoleContext";

export default function ActiveRoleContextBar() {
  const { t } = useI18n();
  const { activeRole, signedInRole, isSimulated, hydrated, exitRole } =
    useActiveRole();

  if (!hydrated) {
    return (
      <div
        className="active-role-context active-role-context--loading"
        aria-busy="true"
        aria-label={t("role_context_region_label")}
      >
        <span className="active-role-context__loading">{t("role_context_loading")}</span>
      </div>
    );
  }

  if (!activeRole) {
    return (
      <div
        className="active-role-context active-role-context--unknown"
        role="region"
        aria-label={t("role_context_region_label")}
      >
        <span className="active-role-context__label">{t("role_context_label")}</span>
        <span className="active-role-context__mode">{t("role_context_unknown")}</span>
      </div>
    );
  }

  const modeKey = ROLE_MODE_MESSAGE_KEYS[activeRole];
  const titleKey = ROLE_TITLE_MESSAGE_KEYS[activeRole];

  return (
    <div
      className={`active-role-context ${
        isSimulated ? "active-role-context--simulated" : "active-role-context--native"
      }`}
      role="region"
      aria-label={t("role_context_region_label")}
    >
      <div className="active-role-context__identity">
        <span className="active-role-context__eyebrow">{t("role_context_label")}</span>
        <span className="active-role-context__title">{t(titleKey)}</span>
        <span className="active-role-context__mode">{t(modeKey)}</span>
        {isSimulated && signedInRole && (
          <span className="active-role-context__signed-in">
            {t("role_context_signed_in_as")} {t(ROLE_TITLE_MESSAGE_KEYS[signedInRole])}
          </span>
        )}
      </div>

      <span
        className={`active-role-context__badge ${
          isSimulated
            ? "active-role-context__badge--simulated"
            : "active-role-context__badge--native"
        }`}
      >
        {isSimulated ? t("role_context_badge_simulated") : t("role_context_badge_native")}
      </span>

      {isSimulated && (
        <button
          type="button"
          className="active-role-context__exit"
          onClick={exitRole}
          title={t("role_context_exit_hint")}
        >
          {t("role_context_exit")}
        </button>
      )}
    </div>
  );
}
