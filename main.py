from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from cinema_es import CinemaEventSourcing, CinemasEventSourcing
from validation_models import CinemaOut, CinemaCreate, CinemaUpdate
import uuid

app = FastAPI()


@app.get("/")
def greet():
    return {"message": "Hello, World!"}

@app.post("/api/cinemas/", response_model=CinemaOut)
def create_cinema(val_cinema: CinemaCreate):

    cinema = CinemaEventSourcing(str(uuid.uuid4()), val_cinema.date,
                                 val_cinema.time, val_cinema.cinema,
                                 val_cinema.movie, val_cinema.hall_number,
                                 val_cinema.type)
    try:
        cinema.create()
    except:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    return {
        "cinema_id": cinema.get_id(),
        "date": cinema.get_date(),
        "time": cinema.get_time(),
        "cinema": cinema.get_cinema(),
        "movie": cinema.get_movie(),
        "hall_number": cinema.get_hall_number(),
        "type": cinema.get_type()
    }

@app.get("/api/cinemas/{start}/{limit}", response_model=list[CinemaOut])
def get_all_cinemas_scroll(start: int, limit: int):
    cinemas = CinemasEventSourcing.load()

    cinemas = [{
            "cinema_id": cinema.get_id(),
            "date": cinema.get_date(),
             "time": cinema.get_time(),
             "cinema": cinema.get_cinema(),
             "movie": cinema.get_movie(),
             "hall_number": cinema.get_hall_number(),
             "type": cinema.get_type()} for cinema in cinemas]

    return cinemas[start:limit + 1]

@app.get("/api/cinemas/", response_model=list[CinemaOut])
def get_all_cinemas():
    cinemas = CinemasEventSourcing.load()

    return [{"cinema_id": cinema.get_id(),
             "date": cinema.get_date(),
             "time": cinema.get_time(),
             "cinema": cinema.get_cinema(),
             "movie": cinema.get_movie(),
             "hall_number": cinema.get_hall_number(),
             "type": cinema.get_type()} for cinema in cinemas]

@app.patch("/api/cinemas/{cinema_id}")
def update_cinema(cinema_id: str, val_cinema: CinemaUpdate):
    cinema = CinemaEventSourcing(
        cinema_id=cinema_id,
        date=None,
        time=None,
        cinema=None,
        movie=None,
        hall_number=None,
        type=None,
        owner_id=None
    )
    cinema.load()
    if cinema.__deleted__:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cinema is deleted")

    try:
        cinema.update(old_version=val_cinema.version, date=val_cinema.date,
                      time=val_cinema.time, cinema=val_cinema.cinema,
                      movie=val_cinema.movie,
                      hall_number=val_cinema.hall_number, type=val_cinema.type)
    except RuntimeError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    return {}

@app.get("/api/cinemas/{cinema_id}", response_model=CinemaOut)
def get_cinema_by_id(cinema_id: str):
    cinema = CinemaEventSourcing(cinema_id)
    cinema.load()

    if cinema.get_version() == -1 or cinema.__deleted__:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"cinema_id": cinema.get_id(),
             "date": cinema.get_date(),
             "time": cinema.get_time(),
             "cinema": cinema.get_cinema(),
             "movie": cinema.get_movie(),
             "hall_number": cinema.get_hall_number(),
             "type": cinema.get_type()}

@app.delete("/api/cinemas/{cinema_id}")
def delete_cinema(cinema_id: str):
    cinema = CinemaEventSourcing(cinema_id)
    try:
        cinema.load()
        cinema.delete(cinema.get_version())
    except:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    return {}