from http import HTTPStatus
from fastapi import FastAPI, HTTPException
from cinema.cinema_es import CinemaEventSourcing, CinemasEventSourcing
from api.validation_models import CinemaOut, CinemaCreate, CinemaUpdate, BookingCreate, BookingOut
from booking.booking_saga import request_booking
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


@app.patch("/api/cinemas/{cinema_id}")
def update_cinema(cinema_id: str, val_cinema: CinemaUpdate):
    cinema = CinemaEventSourcing(cinema_id=cinema_id)
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


@app.delete("/api/cinemas/{cinema_id}")
def delete_cinema(cinema_id: str):
    cinema = CinemaEventSourcing(cinema_id)
    try:
        cinema.load()
        cinema.delete(cinema.get_version())
    except:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    return {}


@app.post("/api/bookings/", response_model=BookingOut)
def create_booking(val: BookingCreate):
    booking_id = request_booking(val.cinema_id, val.hall_number, val.seat_number)
    return {"booking_id": booking_id, "status": "PENDING"}
