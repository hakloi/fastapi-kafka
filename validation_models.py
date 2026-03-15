from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, Optional
from datetime import date, time
from enum import Enum

class SessionType(str, Enum):
    REGULAR = "REGULAR"
    THREE_D = "THREE_D"
    IMAX = "IMAX"

CinemaType = Annotated[str, Field(min_length=1)]
MovieType = Annotated[str, Field(min_length=1)]
HallType = Annotated[int, Field(gt=0)]
VersionType = Annotated[int, Field(ge=0)]

class CinemaCreate(BaseModel):
    date: date
    time: time
    cinema: CinemaType
    movie: MovieType
    hall_number: HallType
    type: SessionType

class CinemaUpdate(BaseModel):
    version: VersionType
    date: Optional[date] = None
    time: Optional[time] = None
    cinema: Optional[CinemaType] = None
    movie: Optional[MovieType] = None
    hall_number: Optional[HallType] = None
    type: Optional[SessionType] = None

class CinemaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cinema_id: str
    date: date
    time: time
    cinema: str
    movie: str
    hall_number: int
    type: SessionType
