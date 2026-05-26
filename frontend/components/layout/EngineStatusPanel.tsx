"use client";

import { useI18n } from "@/i18n/LanguageProvider";
import { engineStatusItems } from "@/lib/navigation";

type Props = {
  collapsed: boolean;
};

export default function EngineStatusPanel({
  collapsed,
}: Props) {
  const { t } = useI18n();

  if (collapsed) {
    return (
      <div className="sidebar-footer">
        <div
          className="engine-status-dot"
          style={{ margin: "0 auto" }}
          title={t("engine_all_active")}
        />
      </div>
    );
  }

  return (
    <div className="sidebar-footer">
      <div className="engine-status-panel">
        <div className="engine-status-title">
          {t("engine_status_title")}
        </div>

        {engineStatusItems.map((engine) => (
          <div
            key={engine.nameKey}
            className="engine-status-row"
          >
            <span>{t(engine.nameKey)}</span>
            <span
              className="engine-status-dot"
              title={t("engine_active")}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
