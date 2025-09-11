from database import session, engine, Base
from sqlalchemy import text
import crud

# Create tables
Base.metadata.create_all(bind=engine)

def init_db():
    db = session()
    # Create roles if they don't exist
    if not crud.get_role_by_name(db, "user"):
        crud.create_role(db, "user", "Regular user")

    if not crud.get_role_by_name(db, "admin"):
        crud.create_role(db, "admin", "Administrator")

    db.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
