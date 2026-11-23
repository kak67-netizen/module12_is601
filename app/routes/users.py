from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import hash_password, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        sqlstate = getattr(error.orig, "sqlstate", None) or getattr(
            error.orig, "pgcode", None
        )
        if sqlstate == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already registered.",
            ) from error
        raise

    db.refresh(user)
    return user


@router.post("/login", response_model=UserRead)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return user