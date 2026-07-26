from tripcare_api.database import Base, SessionLocal, engine
from tripcare_api.seed import seed_demo_data

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_demo_data(db)
print("TripCare demo data is ready")
