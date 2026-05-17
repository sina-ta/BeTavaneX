def interpret_project(cpi, spi, final_score, risk_score):

    # =========================
    # Schedule Status
    # =========================

    if spi < 0.8:

        schedule_status = (
            "Project progress is significantly behind schedule"
        )

    elif spi < 1:

        schedule_status = (
            "Project progress is slightly behind schedule"
        )

    elif 0.95 <= spi <= 1.05:

        schedule_status = (
            "Project is progressing as planned"
        )

    else:

        schedule_status = (
            "Project is progressing faster than planned"
        )

    # =========================
    # Cost Status
    # =========================

    if cpi < 0.8:

        cost_status = (
            "Costs are increasing faster than expected"
        )

    elif cpi < 1:

        cost_status = (
            "Project costs are slightly above target"
        )

    elif cpi == 1:

        cost_status = (
            "Project costs are under control"
        )

    else:

        cost_status = (
            "Project spending efficiency is good"
        )

    # =========================
    # Alert Engine
    # =========================

    if final_score < 60:

        alert = "🔴 Critical"

    elif final_score < 80:

        alert = "🟡 Warning"

    else:

        alert = "🟢 Good"

    # =========================
    # Risk Level
    # =========================

    if risk_score > 60:

        risk_level = "🔴 High Risk"

    elif risk_score > 30:

        risk_level = "🟡 Medium Risk"

    else:

        risk_level = "🟢 Low Risk"

    return {

        "schedule_status": schedule_status,

        "cost_status": cost_status,

        "alert": alert,

        "risk_level": risk_level,
    }


def generate_recommendation(cpi, spi):

    if spi < 1 and cpi >= 1:

        return {
            "title": "Schedule Delay",
            "action": "Increase manpower",
            "severity": "warning"
        }

    elif spi < 1 and cpi < 1:

        return {
            "title": "Critical Risk",
            "action": "Review workforce and costs",
            "severity": "critical"
        }

    elif spi >= 1 and cpi < 1:

        return {
            "title": "Cost Overrun",
            "action": "Reduce unnecessary costs",
            "severity": "warning"
        }

    else:

        return {
            "title": "Project Stable",
            "action": "Maintain current performance",
            "severity": "good"
        }