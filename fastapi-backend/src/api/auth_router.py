from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
import uuid
from ..services.auth_service import AuthService, get_auth_service
from ..schemas.schemas import UserBase, UserCreate, LoginData, Token
from fastapi.security import OAuth2PasswordRequestForm
from ..models.user_models import  User

auth_router = APIRouter(prefix="/api/auth", tags=["Аутентификация"])

def set_refresh_cookie(response: Response, refresh_token: str, days: int = 7):
    max_age = days * 24 * 60 * 60
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=max_age
    )

@auth_router.post("/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.create_user(user_data)

@auth_router.post("/login", response_model=Token)
async def login_user(response: Response, login_data: LoginData, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.get_user_by_email(login_data.email)
    if not user or not auth_service.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неправильный email или пароль")
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    await auth_service.update_refresh_token(user, refresh_token)
    set_refresh_cookie(response, refresh_token)
    return Token(access_token=access_token)


@auth_router.post("/login-form", response_model=Token)
async def login_user_form(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Авторизация через стандартную форму Swagger (username + password)."""
    user = await auth_service.get_user_by_email(form_data.username)
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неправильный email или пароль")

    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)
    await auth_service.update_refresh_token(user, refresh_token)

    set_refresh_cookie(response, refresh_token)
    return Token(access_token=access_token)


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, response: Response, auth_service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token отсутствует")
    payload = auth_service.decode_jwt_token(refresh_token)
    if payload is None or payload.get("token_type") != "refresh":
        raise HTTPException(status_code=401, detail="Недействительный refresh token")
    user = await auth_service.get_user_by_id(uuid.UUID(payload["user_id"]))
    if not user or not auth_service.verify_password(refresh_token, user.refresh_token_hash):
        raise HTTPException(status_code=401, detail="Refresh token отозван")
    new_access_token = auth_service.create_access_token(user.id)
    new_refresh_token = auth_service.create_refresh_token(user.id)
    await auth_service.update_refresh_token(user, new_refresh_token)
    set_refresh_cookie(response, new_refresh_token)
    return Token(access_token=new_access_token)


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(request: Request, response: Response, auth_service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        payload = auth_service.decode_jwt_token(refresh_token)
        if payload and payload.get("user_id"):
            user = await auth_service.get_user_by_id(uuid.UUID(payload["user_id"]))
            if user:
                await auth_service.update_refresh_token(user, None)
    response.delete_cookie("refresh_token")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@auth_router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(
        current_user: User = Depends(get_auth_service.get_current_user)
):
    """
    Получить информацию о текущем пользователе.

    Требует валидный access_token в Authorization header.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "rating": current_user.rating,
        "created_at": current_user.created_at
    }
