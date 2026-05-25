"""Operational validation thresholds — tunable heuristics, not ML."""

MAX_MANPOWER_PER_REPORT = 20
MAX_EQUIPMENT_HOURS_PER_SHIFT = 16
MAX_QUANTITY_SPIKE_RATIO = 2.5
MIN_PROGRESS_WITHOUT_DELAY = 5
MAX_OVERTIME_HOURS = 6
TRUST_THRESHOLD = 60
DUPLICATE_QTY_TOLERANCE = 0.01

# Unit-agnostic quantity ceilings per report (foundation defaults)
MAX_DAILY_QUANTITY = 5000
