import enum
import uuid
from datetime import date, time

from sqlalchemy import String, Integer, Date, Time, Enum, Boolean, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SessionType(enum.Enum):
    REGULAR = "REGULAR"
    THREE_D = "THREE_D"
    IMAX = "IMAX"


class BookingStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Cinema(Base):
    __tablename__ = "cinema"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date: Mapped[date] = mapped_column(Date)
    time: Mapped[time] = mapped_column(Time)
    cinema: Mapped[str] = mapped_column(String)
    movie: Mapped[str] = mapped_column(String)
    hall_number: Mapped[int] = mapped_column(Integer)
    type: Mapped[SessionType] = mapped_column(Enum(SessionType))


class Seat(Base):
    __tablename__ = "seat"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hall_number: Mapped[int] = mapped_column(Integer)
    seat_number: Mapped[int] = mapped_column(Integer)
    is_reserved: Mapped[bool] = mapped_column(Boolean, default=False)


class Booking(Base):
    __tablename__ = "booking"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cinema_id: Mapped[str] = mapped_column(String(36))
    hall_number: Mapped[int] = mapped_column(Integer)
    seat_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PENDING)


class Outbox(Base):
    __tablename__ = "outbox"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    topic: Mapped[str] = mapped_column(String)
    key: Mapped[str] = mapped_column(String(36))
    payload: Mapped[str] = mapped_column(Text)
    sent: Mapped[bool] = mapped_column(Boolean, default=False)


class ProcessedEvent(Base):
    __tablename__ = "processed_event"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
