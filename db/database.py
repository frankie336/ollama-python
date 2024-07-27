from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Update the DATABASE_URL to point to your Docker container's MySQL instance
DATABASE_URL = "mysql+pymysql://ollama:3e4Qv5uo2Cg31zC1@db:3307/cosmic_catalyst"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
