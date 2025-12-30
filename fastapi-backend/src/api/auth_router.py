# api/auth_router.py
"""
API эндпоинты для аутентификации.
Регистрация, логин, обновление токенов, выход.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from ..services.auth_service import AuthService, get_auth_service, get_current_user
from ..schemas.schemas import UserBase, UserCreate, LoginData, Token
from ..models.user_models import User
from ..core.security import TokenService

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/api/auth", tags=["Аутентификация"])


# === Утилиты ===

def set_refresh_cookie(
        response: Response,
        refresh_token: str,
        days: int = 7,
        secure: bool = False  # True для production с HTTPS
) -> None:
    """
    Устанавливает refresh токен в httpOnly cookie.

    Args:
        response: FastAPI Response объект
        refresh_token: JWT refresh токен
        days: Время жизни cookie в днях
        secure: True для HTTPS (production)
    """
    max_age = days * 24 * 60 * 60  # секунды

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Недоступен из JavaScript
        secure=secure,  # Только HTTPS в production
        samesite="lax",  # Защита от CSRF
        max_age=max_age,
        path="/api/auth"  # Ограничиваем scope cookie
    )


def clear_refresh_cookie(response: Response) -> None:
    """Удаляет refresh токен cookie."""
    response.delete_cookie(
        key="refresh_token",
        path="/api/auth"
    )


# === Эндпоинты ===

@auth_router.post(
    "/register",
    response_model=UserBase,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя"
)
async def register_user(
        user_data: UserCreate,
        auth_service: AuthService = Depends(get_auth_service)
):
    """
    Регистрирует нового пользователя.

    - **email**: Уникальный email
    - **username**: Уникальное имя пользователя (3-20 символов)
    - **password**: Пароль (минимум 8 символов)
    - **role**: Роль (student, teacher)
    - **full_name**: Полное имя (опционально)
    """
    logger.info(f"Регистрация нового пользователя: {user_data.email}")
    return await auth_service.create_user(user_data)


@auth_router.post(
    "/login",
    response_model=Token,
    summary="Вход по email и паролю (JSON)"
)
async def login_user(
        response: Response,
        login_data: LoginData,
        auth_service: AuthService = Depends(get_auth_service)
):
    """
    Аутентификация пользователя.

    Возвращает access_token в теле ответа.
    Refresh token устанавливается в httpOnly cookie.
    """
    user = await auth_service.authenticate_user(login_data.email, login_data.password)

    if not user:
        logger.warning(f"Неудачная попытка входа: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаём токены
    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user)

    # Сохраняем хэш refresh токена в БД
    await auth_service.update_refresh_token(user, refresh_token)

    # Устанавливаем refresh токен в cookie
    set_refresh_cookie(response, refresh_token)

    logger.info(f"Успешный вход: {user.email}")

    return Token(access_token=access_token)


@auth_router.post(
    "/login-form",
    response_model=Token,
    summary="Вход через форму (для Swagger UI)"
)
async def login_user_form(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        auth_service: AuthService = Depends(get_auth_service)
):
    """
    Аутентификация через стандартную форму OAuth2.
    Используется Swagger UI для авторизации.

    В поле username введите email.
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_access_token(user)
    refresh_token = auth_service.create_refresh_token(user)

    await auth_service.update_refresh_token(user, refresh_token)
    set_refresh_cookie(response, refresh_token)

    return Token(access_token=access_token)


@auth_router.post(
    "/refresh",
    response_model=Token,
    summary="Обновление access токена"
)
async def refresh_token(
        request: Request,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service)
):
    """
    Обновляет access токен используя refresh токен из cookie.

    Также выполняет ротацию refresh токена для безопасности.
    """
    # Получаем refresh токен из cookie
    refresh_token_value = request.cookies.get("refresh_token")

    if not refresh_token_value:
        logger.warning("Попытка обновления без refresh токена")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен отсутствует"
        )

    # Декодируем и проверяем токен
    payload = TokenService.verify_refresh_token(refresh_token_value)

    if not payload:
        logger.warning("Невалидный refresh токен")
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен"
        )

    # Получаем пользователя
    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный токен"
        )

    from uuid import UUID
    user = await auth_service.get_user_by_id(UUID(user_id))

    if not user:
        logger.warning(f"Пользователь не найден при refresh: {user_id}")
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    # ✅ ИСПРАВЛЕНИЕ: Правильная проверка refresh токена
    # Используем метод, который применяет SHA256 перед сравнением с bcrypt хэшем
    if not user.refresh_token_hash:
        logger.warning(f"Refresh токен отозван для: {user.email}")
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен был отозван"
        )

    if not auth_service.verify_refresh_token_string(refresh_token_value, user.refresh_token_hash):
        logger.warning(f"Несоответствие refresh токена для: {user.email}")
        # Потенциальная атака - очищаем все токены пользователя
        await auth_service.update_refresh_token(user, None)
        clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh токен недействителен"
        )

    # Создаём новые токены (ротация)
    new_access_token = auth_service.create_access_token(user)
    new_refresh_token = auth_service.create_refresh_token(user)

    # Обновляем хэш в БД
    await auth_service.update_refresh_token(user, new_refresh_token)

    # Устанавливаем новый refresh токен
    set_refresh_cookie(response, new_refresh_token)

    logger.info(f"Токены обновлены для: {user.email}")

    return Token(access_token=new_access_token)


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход из системы"
)
async def logout_user(
        request: Request,
        response: Response,
        auth_service: AuthService = Depends(get_auth_service)
):
    """
    Выход из системы.

    Инвалидирует refresh токен и очищает cookie.
    """
    refresh_token_value = request.cookies.get("refresh_token")

    if refresh_token_value:
        payload = TokenService.decode_token(refresh_token_value)

        if payload:
            user_id = payload.get("user_id") or payload.get("sub")
            if user_id:
                from uuid import UUID
                try:
                    user = await auth_service.get_user_by_id(UUID(user_id))
                    if user:
                        await auth_service.update_refresh_token(user, None)
                        logger.info(f"Выход пользователя: {user.email}")
                except Exception as e:
                    logger.error(f"Ошибка при logout: {e}")

    clear_refresh_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@auth_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Информация о текущем пользователе"
)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Возвращает информацию о текущем авторизованном пользователе.

    Требует валидный access_token в заголовке Authorization.
    """
    role_value = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": role_value,
        "rating": current_user.rating,
        "created_at": current_user.created_at,
    }


@auth_router.post(
    "/verify",
    summary="Проверка валидности токена"
)
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    Проверяет валидность access токена.

    Возвращает базовую информацию если токен валиден.
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    }