from fastapi import APIRouter, HTTPException, status

from backend.app.server.service.user_service import UserService
from backend.app.server.schemas.user_schemas import UserLoginRequest, UserLoginResponse

login_api_routes = APIRouter(
    prefix="/login",
    tags=["authentication"]
)

# Initialize service layer
user_service = UserService()


@login_api_routes.get("/get_user_id")
def get_user_id():
    """Legacy endpoint - kept for backwards compatibility"""
    return {"user_id": "1"}


@login_api_routes.post("", response_model=UserLoginResponse)
def login(request: UserLoginRequest):
    """
    User login endpoint.

    - **username**: Username or email address
    - **password**: User's password

    Returns user information and authentication token on success.
    """
    try:
        response = user_service.login(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


