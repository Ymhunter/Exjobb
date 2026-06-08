from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://waiter:password@localhost:5432/waiter_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Menu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    menu_type = Column(String, default="General")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_intent = Column(String)
    order_text = Column(Text)
    status = Column(String, default="pending")

def init_db():
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE menu ADD COLUMN IF NOT EXISTS menu_type VARCHAR;"))
            conn.commit()
        except Exception as e:
            print(f"Migration error: {e}")
