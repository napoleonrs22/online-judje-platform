from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid, os, hashlib 

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.user_models import User
from ..schemas.schemas import UserCreate
from ..database import get_db


SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login-form", scheme_name="JWT")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # === Хэширование ===
    def get_password_hash(self, password: str) -> str:
        """Безопасно хэширует пароль, даже если он длиннее 72 байт."""
        if not isinstance(password, str):
            password = str(password)

        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # преобразуем обратно в строку, passlib принимает только str
        password = password_bytes.decode("utf-8", errors="ignore")

        return pwd_context.hash(password)


    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие открытого пароля хэшу."""

        plain_password_bytes = plain_password.encode("utf-8")[:72]
        return pwd_context.verify(plain_password_bytes, hashed_password)
    
    # === РАБОТА С JWT ===

    def create_jwt_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Создает JWT-токен (Access или Refresh)."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        to_encode.update({"exp": expire, "sub": str(data["user_id"])}) 
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_access_token(self, user_id: uuid.UUID) -> str:
        """Создает Access Token (короткий срок жизни)."""
        expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return self.create_jwt_token({"user_id": str(user_id), "token_type": "access"}, expires_delta=expire)

    def create_refresh_token(self, user_id: uuid.UUID) -> str:
        """Создает Refresh Token (длительный срок жизни)."""
        expire = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        return self.create_jwt_token({"user_id": str(user_id), "token_type": "refresh"}, expires_delta=expire)

    def decode_jwt_token(self, token: str) -> Optional[dict]:
        """Декодирует и валидирует JWT-токен."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    # === CRUD Пользователя ===

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получает пользователя по email."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Получает пользователя по ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Регистрация нового пользователя."""
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email уже зарегистрирован"
            )

        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            role=user_data.role,
            full_name=user_data.full_name,
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update_refresh_token(self, user: User, refresh_token: Optional[str]):
        """Хранит хэш refresh-токена (не сам токен)."""
        if refresh_token:
            # Используем SHA256 для хэширования Refresh Token перед сохранением в БД
            safe_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            # Хэшируем полученный SHA256 хэш с помощью bcrypt для хранения
            user.refresh_token_hash = self.get_password_hash(safe_hash)
        else:
            user.refresh_token_hash = None

        await self.db.commit()
        await self.db.refresh(user)


# --- Зависимости для роутеров ---
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Извлекает и валидирует Access Token, возвращает объект User."""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительные учетные данные или токен истек",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = auth_service.decode_jwt_token(token)
    
    if payload is None or payload.get("token_type") != "access":
        raise credentials_exception
    
    user_id_str: str = payload.get("user_id")
    if user_id_str is None:
        raise credentials_exception
        
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = await auth_service.get_user_by_id(user_id)
    
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Проверяет, является ли пользователь преподавателем или администратором."""
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль Преподавателя или Администратора."
        )
    return current_user

async def get_current_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "student":
        raise HTTPException(
            status=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав,  Доступ разрещён только студентам."

        )
    return current_user