from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import DailyWorkOrder

# =========================
# Database Connection
# =========================

DATABASE_URL = "postgresql://postgres:Mahshid88@localhost:5433/betavanx_db"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

session = Session()


# =========================
# Create Work Order
# =========================

new_work_order = DailyWorkOrder(

    project_id=1,

    task_id=101,

    assigned_to="Concrete Team A",

    planned_qty=20,

    unit="m3",

    priority="High",

    status="Open",

    created_by="Sina"
)


# =========================
# Save To Database
# =========================

session.add(new_work_order)

session.commit()

print("✅ Work Order Inserted")