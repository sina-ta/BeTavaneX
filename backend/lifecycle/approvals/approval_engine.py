from backend.lifecycle.utils.enums import ApprovalStatus


APPROVAL_CHAINS: dict[str, list[str]] = {
    "daily_report": ["Supervisor", "Senior Field Validator"],
    "work_order": ["Supervisor", "Project Manager"],
    "task_completion": [
        "Supervisor",
        "Senior Field Validator",
        "Operations Manager",
    ],
    "validation": ["Senior Field Validator"],
    "escalation": ["Operations Manager", "Project Manager"],
}


def get_approval_chain(entity_type: str) -> list[str]:
    return APPROVAL_CHAINS.get(entity_type, ["Supervisor"])


def build_approval_requests(
    entity_type: str,
    entity_id: int,
    requested_by: str,
) -> list[dict]:
    chain = get_approval_chain(entity_type)

    return [
        {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "approval_chain_level": index + 1,
            "required_role": role,
            "status": ApprovalStatus.PENDING.value,
            "requested_by": requested_by,
        }
        for index, role in enumerate(chain)
    ]


def can_approve_at_level(
    approvals: list,
    role: str,
) -> bool:
    pending = sorted(
        [a for a in approvals if a.status == ApprovalStatus.PENDING.value],
        key=lambda item: item.approval_chain_level,
    )

    if not pending:
        return False

    return pending[0].required_role == role
