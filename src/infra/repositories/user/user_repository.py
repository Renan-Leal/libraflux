from nest.core import Injectable
from ...models.user_model import UserModel
from ...db import SessionLocal


@Injectable
class UserRepository:
    def __init__(self):
        pass

    def save(self, user: UserModel):
        with SessionLocal() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def find_by_email(self, email: str):
        with SessionLocal() as session:
            return session.query(UserModel).filter_by(email=email).first()
