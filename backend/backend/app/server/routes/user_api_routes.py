"""User API routes for handling user operations"""
from fastapi import APIRouter, HTTPException, status

from backend.app.server.service.user_service import UserService
from backend.app.server.schemas.user_schemas import (
    UserCreateRequest, UserUpdateRequest,
    UserCreateResponse, UserResponse,
    UserListResponse, UserOperationResponse,
    UserLoginRequest, UserLoginResponse,
    AnonymousUserRequest, AnonymousUserResponse
)

user_api_router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Initialize service layer
user_service = UserService()


# ========== User CRUD Endpoints ==========

@user_api_router.post("/create", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: UserCreateRequest):
    """
    Create a new user.

    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Password (minimum 8 characters)
    - **full_name**: Optional full name
    """
    try:
        response = user_service.create_user(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_api_router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    """
    Get a user by their ID.

    Returns user information without password hash.
    """
    try:
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_api_router.get("", response_model=UserListResponse)
def get_all_users(include_inactive: bool = False):
    """
    Get all users.

    - **include_inactive**: Set to true to include deactivated users
    """
    try:
        response = user_service.get_all_users(include_inactive)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_api_router.put("/{user_id}", response_model=UserOperationResponse)
def update_user(user_id: str, request: UserUpdateRequest):
    """
    Update a user's information.

    All fields are optional. Only provided fields will be updated.
    - **username**: New username (3-50 characters)
    - **email**: New email address
    - **password**: New password (minimum 8 characters)
    - **full_name**: New full name
    - **is_active**: Active status
    """
    try:
        response = user_service.update_user(user_id, request)
        if not response.success:
            status_code = status.HTTP_404_NOT_FOUND if "not found" in response.message.lower() else status.HTTP_400_BAD_REQUEST
            raise HTTPException(status_code=status_code, detail=response.message)
        return response
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_api_router.delete("/{user_id}", response_model=UserOperationResponse)
def delete_user(user_id: str):
    """
    Permanently delete a user and all associated data.

    This will delete:
    - The user account
    - All user's chat sessions
    - All user's messages

    **Warning**: This action cannot be undone!
    """
    try:
        response = user_service.delete_user(user_id)
        if not response.success:
            status_code = status.HTTP_404_NOT_FOUND if "not found" in response.message.lower() else status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=status_code, detail=response.message)
        return response
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_api_router.put("/{user_id}/deactivate", response_model=UserOperationResponse)
def deactivate_user(user_id: str):
    """
    Deactivate a user (soft delete).

    This will set the user's is_active flag to False.
    The user will not be able to login but data is preserved.
    """
    try:
        response = user_service.deactivate_user(user_id)
        if not response.success:
            status_code = status.HTTP_404_NOT_FOUND if "not found" in response.message.lower() else status.HTTP_500_INTERNAL_SERVER_ERROR
            raise HTTPException(status_code=status_code, detail=response.message)
        return response
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ========== Authentication Endpoints ==========

@user_api_router.post("/anonymous", response_model=AnonymousUserResponse, status_code=status.HTTP_201_CREATED)
def create_anonymous_user(request: AnonymousUserRequest = AnonymousUserRequest()):
    """
    Create an anonymous user for guest access.

    - **device_id**: Optional device identifier

    Returns anonymous user_id that can be used immediately.
    """
    try:
        response = user_service.create_anonymous_user(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@user_api_router.post("/login", response_model=UserLoginResponse)
def login(request: UserLoginRequest):
    """
    Authenticate a user.

    - **username**: Username or email address
    - **password**: User's password

    Returns user information and authentication token on success.
    """
    try:
        response = user_service.login(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

