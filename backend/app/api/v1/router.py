from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.body_metrics import router as body_metrics_router
from app.api.v1.exercise_overrides import router as exercise_overrides_router
from app.api.v1.exercises import router as exercises_router
from app.api.v1.nutrition import router as nutrition_router
from app.api.v1.programs import router as programs_router
from app.api.v1.users import router as users_router
from app.api.v1.workout_logs import router as workout_logs_router
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="fitness-tracker-api")


router.include_router(auth_router)
router.include_router(body_metrics_router)
router.include_router(exercise_overrides_router)
router.include_router(exercises_router)
router.include_router(nutrition_router)
router.include_router(programs_router)
router.include_router(users_router)
router.include_router(workout_logs_router)

api_router = router
