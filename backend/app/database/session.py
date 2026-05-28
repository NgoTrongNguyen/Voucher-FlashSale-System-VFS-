# Quản lý kết nối SQLAlchemy tới PostgreSQL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.config import settings

# SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo = settings.DB_ECHO,
    pool_size = 5,
    max_overflow = 10,
    pool_pre_ping = True,
)

# Session factory
SessionLocal = sessionmaker(
    bind = engine,
    autocommit = False,
    autoflush = False,
)

# Dependency để lấy session trong FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Uses: 
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helpers functions
def init_db():
    from app.database.models import Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    from app.database.models import Base
    Base.metadata.drop_all(bind=engine)

def get_session() -> Session:
    return SessionLocal()