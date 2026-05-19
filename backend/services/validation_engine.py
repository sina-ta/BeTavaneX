def validate_daily_report(report, work_order):

    validation_warnings = []

    # =========================
    # Rule 1
    # =========================

    if not work_order:

        validation_warnings.append(
            "⚠️ Invalid Work Order ID"
        )

    else:

        if report.actual_qty > work_order.planned_qty:

            validation_warnings.append(
                "⚠️ Actual quantity exceeds planned quantity"
            )

    # =========================
    # Rule 2
    # =========================

    if report.manpower_count > 20:

        validation_warnings.append(
            "⚠️ Suspicious manpower allocation"
        )

    # =========================
    # Rule 3
    # =========================

    if report.actual_qty < 5 and report.delay_reason == "None":

        validation_warnings.append(
            "⚠️ Low progress without delay reason"
        )

    return validation_warnings