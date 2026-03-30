from fastapi import FastAPI, HTTPException
from database import SessionLocal
from database_model import Cinema
from validation_models import CinemaOut

app = FastAPI()


def _to_out(c: Cinema) -> dict:
    return {
        "cinema_id": c.id,
        "date": c.date,
        "time": c.time,
        "cinema": c.cinema,
        "movie": c.movie,
        "hall_number": c.hall_number,
        "type": c.type,
    }


@app.get("/api/cinemas/", response_model=list[CinemaOut])
def get_all_cinemas():
    with SessionLocal() as session:
        return [_to_out(c) for c in session.query(Cinema).all()]


@app.get("/api/cinemas/{start}/{limit}", response_model=list[CinemaOut])
def get_all_cinemas_scroll(start: int, limit: int):
    with SessionLocal() as session:
        cinemas = session.query(Cinema).offset(start).limit(limit).all()
        return [_to_out(c) for c in cinemas]


@app.get("/api/cinemas/{cinema_id}", response_model=CinemaOut)
def get_cinema_by_id(cinema_id: str):
    with SessionLocal() as session:
        cinema = session.query(Cinema).filter(Cinema.id == cinema_id).first()
        if not cinema:
            raise HTTPException(status_code=404, detail="Session not found")
        return _to_out(cinema)
