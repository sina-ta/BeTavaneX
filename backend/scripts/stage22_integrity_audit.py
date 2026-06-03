#!/usr/bin/env python3
"""Stage 22: document FK delete rules and repository delete policy."""

from __future__ import annotations

RULES = [
    ("projects", "RESTRICT children", "Cannot delete project with operational data"),
    ("project_memberships", "CASCADE on project", "Membership rows removed with project"),
    ("work_orders", "RESTRICT daily_reports", "Reports block orphan WO removal"),
    ("workflow_steps", "RESTRICT approvals/blockers", "Governance data protected"),
    ("work_order_workflow_steps", "CASCADE both sides", "Assignment junction only deletable row"),
    ("boq_mappings", "allowed repository delete", "Execution correction only"),
]


def main() -> int:
    print("Stage 22 integrity audit — ON DELETE / delete policy")
    for table, rule, note in RULES:
        print(f"  {table}: {rule} — {note}")
    print("Repository delete guard: WorkOrderWorkflowStep, BOQMapping only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
