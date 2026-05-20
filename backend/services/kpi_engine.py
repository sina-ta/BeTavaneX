def calculate_kpis(work_order, reports):

    actual_qty = sum(
        r.actual_qty for r in reports
    )

    raw_progress = (
        actual_qty / work_order.planned_qty
    ) * 100

    progress_percent = min(raw_progress, 100)

    planned_progress = 50

    cpi = progress_percent / 100

    spi = progress_percent / planned_progress

    raw_score = (
        (cpi * 40) +
        (spi * 40) +
        (progress_percent * 0.2)
    )

    final_score = min(raw_score, 100)

    risk_score = 100 - final_score

    return {

        "progress_percent": progress_percent,

        "planned_progress": planned_progress,

        "cpi": cpi,

        "spi": spi,

        "final_score": final_score,

        "risk_score": risk_score
    }