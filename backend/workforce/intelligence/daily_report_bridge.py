from backend.models import DailyReport, DailyWorkOrder


def summarize_daily_report_contribution(
    worker_id: int,
    reports: list[DailyReport],
    work_orders: list[DailyWorkOrder],
) -> dict:
    """Bridge daily operational reports to workforce intelligence."""
    related_reports = [
        report
        for report in reports
        if report.reported_by
        and str(worker_id) in report.reported_by
    ]

    if not related_reports:
        return {
            "report_count": 0,
            "total_actual_qty": 0,
            "total_manpower_logged": 0,
            "delay_events": 0,
            "source": "daily_report",
        }

    delay_events = len([
        report
        for report in related_reports
        if report.delay_reason
        and report.delay_reason.strip()
    ])

    work_order_map = {
        order.id: order for order in work_orders
    }

    linked_tasks = {
        work_order_map[report.work_order_id].task_id
        for report in related_reports
        if report.work_order_id in work_order_map
    }

    return {
        "report_count": len(related_reports),
        "total_actual_qty": round(
            sum(report.actual_qty or 0 for report in related_reports),
            2,
        ),
        "total_manpower_logged": sum(
            report.manpower_count or 0 for report in related_reports
        ),
        "delay_events": delay_events,
        "linked_task_ids": sorted(linked_tasks),
        "source": "daily_report",
    }
