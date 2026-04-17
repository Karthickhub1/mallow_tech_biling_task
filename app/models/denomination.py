from sqlalchemy import Column, Integer

from app.core.database import Base


class Denomination(Base):
    __tablename__ = "denominations"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer, unique=True, nullable=False)
    count = Column(Integer, nullable=False, default=0)
