import { engineStatusItems } from "@/lib/navigation";

type Props = {
  collapsed: boolean;
};

export default function EngineStatusPanel({
  collapsed,
}: Props) {
  if (collapsed) {
    return (
      <div className="sidebar-footer">
        <div
          className="engine-status-dot"
          style={{ margin: "0 auto" }}
          title="All engines active"
        />
      </div>
    );
  }

  return (
    <div className="sidebar-footer">
      <div className="engine-status-panel">
        <div className="engine-status-title">Engine Status</div>

        {engineStatusItems.map((engine) => (
          <div key={engine.name} className="engine-status-row">
            <span>{engine.name}</span>
            <span className="engine-status-dot" title="Active" />
          </div>
        ))}
      </div>
    </div>
  );
}
