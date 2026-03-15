import datetime

from crypt import CryptService
from database import SessionLocal
from database_model import Cinema, SessionType, User

session = SessionLocal()

session.query(User).delete()
session.commit()

user = session.query(User).filter(User.login == "admin").first()

if not user:
    password = "12345678"
    hashed_password = CryptService.get_hashed_password(password)

    user = User(login="admin", password_hash=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)

    print(f"Admin user created with ID: {user.id}")
    print(f"Login: admin")
    print(f"Password: {password}")


# чистим бд
session.query(Cinema).delete()
session.commit()

for i in range(10):
    now = datetime.datetime.now()
    time_without_seconds = now.replace(second=0, microsecond=0).time()

    cinema = Cinema(
        date=datetime.date.today(),
        time=time_without_seconds,
        cinema="Каро",
        movie=f"Ёлки {i + 1}",
        hall_number= i % 5 + 1,
        type=SessionType.REGULAR,
        owner_id=user.id
    )
    session.add(cinema)

session.commit()
