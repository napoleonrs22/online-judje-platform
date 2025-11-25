
from fastapi import  APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..database import get_db
from ..services.dashboard_service import DashboardService
from ..services.auth_service import get_current_active_user
from ..models.user_models import User

dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Дашборд"])

def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> DashboardService:
    return DashboardService(db)

@dashboard_router.get("/top-students")
async def top_students(
    limit: int = 10,
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_active_user)
):
    return await service.get_top_students(limit)

# будущем
# @dashboard_router.get("/recent-contests")
# async def recent_contests(
#     service: DashboardService = Depends(get_dashboard_service),
#     current_user: User = Depends(get_current_active_user)
# ):
#     return await service.get_recent_contests()

@dashboard_router.get("/available-problems")
async def available_problems(
    skip: int = 0,
    limit: int = 20,
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_active_user)
):
    return await service.get_available_problems(current_user.id, skip, limit)