import enum
import uuid
from datetime import date, time

from sqlalchemy import String, Integer, Date, Time, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class SessionType(enum.Enum):
    REGULAR = "REGULAR"
    THREE_D = "THREE_D"
    IMAX = "IMAX"

class Cinema(Base):
    __tablename__ = "cinema"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date: Mapped[date] = mapped_column(Date)
    time: Mapped[time] = mapped_column(Time)
    cinema: Mapped[str] = mapped_column(String)
    movie: Mapped[str] = mapped_column(String)
    hall_number: Mapped[int] = mapped_column(Integer)
    type: Mapped[SessionType] = mapped_column(Enum(SessionType))
