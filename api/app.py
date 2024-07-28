from fastapi import FastAPI
from sqlalchemy import create_engine, text, inspect
from models.models import Base
from api.v1.routers import router as api_router

# Update this with your actual database URL
DATABASE_URL = "mysql+pymysql://ollama:3e4Qv5uo2Cg31zC1@127.0.0.1:3307/cosmic_catalyst"

engine = create_engine(DATABASE_URL)

def drop_constraints():
    inspector = inspect(engine)
    with engine.connect() as connection:
        for table_name in inspector.get_table_names():
            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                fk_name = fk['name']
                connection.execute(text(f"ALTER TABLE {table_name} DROP FOREIGN KEY {fk_name}"))

def drop_tables():
    Base.metadata.drop_all(bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def create_app(init_db=True):
    app = FastAPI()

    # Include API routers
    app.include_router(api_router, prefix="/v1")

    @app.get("/")
    def read_root():
        return {"message": "Welcome to the API!"}

    if init_db:
        # Create database tables
        create_tables()

    return app

app = create_app()

def create_test_app():
    # Drop constraints, drop tables, and recreate tables for a clean test environment
    drop_constraints()
    drop_tables()
    create_tables()
    return create_app(init_db=False)
