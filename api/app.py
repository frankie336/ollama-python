from fastapi import FastAPI
from sqlalchemy import create_engine, text, inspect
from models.models import Base
from api.v1.routers import router as api_router
from services.loggin_service import LoggingUtility

# Initialize the logging utility
logging_utility = LoggingUtility()

# Update this with your actual database URL
DATABASE_URL = "mysql+pymysql://ollama:3e4Qv5uo2Cg31zC1@127.0.0.1:3307/cosmic_catalyst"

engine = create_engine(DATABASE_URL)

def drop_constraints():
    logging_utility.info("Dropping constraints")
    inspector = inspect(engine)
    with engine.connect() as connection:
        for table_name in inspector.get_table_names():
            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                fk_name = fk['name']
                logging_utility.info("Dropping foreign key %s from table %s", fk_name, table_name)
                connection.execute(text(f"ALTER TABLE {table_name} DROP FOREIGN KEY {fk_name}"))

def drop_tables():
    logging_utility.info("Dropping all tables")
    Base.metadata.drop_all(bind=engine)

def create_tables():
    logging_utility.info("Creating all tables")
    Base.metadata.create_all(bind=engine)

def create_app(init_db=True):
    logging_utility.info("Creating FastAPI app")
    app = FastAPI()

    # Include API routers
    app.include_router(api_router, prefix="/v1")

    @app.get("/")
    def read_root():
        logging_utility.info("Root endpoint accessed")
        return {"message": "Welcome to the API!"}

    if init_db:
        logging_utility.info("Initializing database")
        # Create database tables
        create_tables()

    return app

app = create_app()

def create_test_app():
    logging_utility.info("Creating test app")
    # Drop constraints, drop tables, and recreate tables for a clean test environment
    drop_constraints()
    drop_tables()
    create_tables()
    return create_app(init_db=False)
