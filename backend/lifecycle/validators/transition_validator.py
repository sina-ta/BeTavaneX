from backend.lifecycle.transitions.state_transitions import (
    can_transition_task,
    can_transition_work_order,
)


def validate_task_transition(
    from_state: str,
    to_state: str,
) -> dict:
    if from_state == to_state:
        return {
            "valid": True,
            "message": "Already in target state",
        }

    if can_transition_task(from_state, to_state):
        return {
            "valid": True,
            "message": f"Transition {from_state} → {to_state} allowed",
        }

    return {
        "valid": False,
        "message": (
            f"Invalid transition: {from_state} → {to_state}"
        ),
    }


def validate_work_order_transition(
    from_state: str,
    to_state: str,
) -> dict:
    if from_state == to_state:
        return {
            "valid": True,
            "message": "Already in target state",
        }

    if can_transition_work_order(from_state, to_state):
        return {
            "valid": True,
            "message": f"Transition {from_state} → {to_state} allowed",
        }

    return {
        "valid": False,
        "message": (
            f"Invalid transition: {from_state} → {to_state}"
        ),
    }
