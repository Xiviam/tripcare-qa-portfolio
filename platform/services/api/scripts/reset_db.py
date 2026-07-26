from tripcare_api.database import Base, SessionLocal, engine
from tripcare_api.seed import seed_demo_data

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_demo_data(db)
print("TripCare database was reset and seeded")
