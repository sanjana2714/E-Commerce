from app.core.exceptions import DuplicateRequestError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User, UserRole
from app.schemas.auth import Token, UserLogin, UserRegister
from sqlalchemy.orm import Session


class AuthService:
    def register_user(self, db: Session, user_in: UserRegister) -> User:
        existing_user = db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise DuplicateRequestError("User with this email already exists.")
        
        hashed = hash_password(user_in.password)
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hashed,
            role=user_in.role or UserRole.CUSTOMER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(self, db: Session, login_in: UserLogin) -> Token:
        user = db.query(User).filter(User.email == login_in.email).first()
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
        
        token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value
        }
        access_token = create_access_token(token_payload)
        return Token(access_token=access_token)

auth_service = AuthService()
