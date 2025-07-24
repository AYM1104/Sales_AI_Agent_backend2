from fastapi import APIRouter, HTTPException
import json
from app.config import settings
from app.models.schemas import (
    CompanySearchRequest,
    CompanySearchResponse,
    SolutionsResponse,
    HealthResponse
)
from app.api.dependencies import (
    ApiKeyDep,
    CompanyServiceDep,
    SolutionServiceDep,
    RateLimitDep
)


router = APIRouter()


@router.get("/solutions", response_model=SolutionsResponse)
async def get_solutions(
    solution_service: SolutionServiceDep,
    _: RateLimitDep
):
    """ソリューション一覧を取得"""
    try:
        solutions = solution_service.get_solutions()
        return SolutionsResponse(success=True, solutions=solutions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))