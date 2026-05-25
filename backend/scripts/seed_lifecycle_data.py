"""Initialize lifecycle records for existing work orders."""

from backend.database import SessionLocal, engine

from backend.models.main_models import Base

import backend.lifecycle.models  # noqa: F401

from backend.models import DailyWorkOrder

from backend.lifecycle.repositories.lifecycle_repository import (
    LifecycleRepository,
)


def seed():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    try:
        repo = LifecycleRepository(session)
        work_orders = session.query(DailyWorkOrder).all()

        for work_order in work_orders:
            wo_lc = repo.ensure_work_order_lifecycle(work_order)
            task_lc = repo.ensure_task_lifecycle(
                work_order.task_id,
                work_order.id,
                initial_state="in_progress"
                if (work_order.status or "").lower() == "active"
                else "assigned",
            )

            repo.add_timeline_event(
                entity_type="task",
                entity_id=work_order.task_id,
                task_id=work_order.task_id,
                work_order_id=work_order.id,
                event_type="state_transition",
                title="Lifecycle initialized",
                description=(
                    f"Task state: {task_lc.current_state}, "
                    f"Work order state: {wo_lc.current_state}"
                ),
                recorded_by="system",
            )

        repo.commit()
        print(f"Lifecycle initialized for {len(work_orders)} work orders.")

    finally:
        session.close()


if __name__ == "__main__":
    seed()
