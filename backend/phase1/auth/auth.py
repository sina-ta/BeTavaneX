"""Authentication scheme and OAuth2 token endpoint.



User credentials are persisted in ``platform_users`` (see ``UserAuthService``).

"""



from __future__ import annotations



from fastapi import APIRouter, Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



from backend.phase1.auth.security import create_access_token

from backend.phase1.auth.user_models import (

    PILOT_SEED_USERS,

    ROLE_ADMIN,

    ROLE_INVESTOR,

    ROLE_SUPERVISOR,

    ROLE_WORKER,

    Token,

    User,

    UserInDB,

)

from backend.phase1.auth.user_service import UserAuthService

from backend.phase1.dependencies.auth_users import get_user_auth_service



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")



auth_router = APIRouter(prefix="/auth", tags=["auth"])





@auth_router.post("/token", response_model=Token)

def login_for_access_token(

    form_data: OAuth2PasswordRequestForm = Depends(),

    user_auth: UserAuthService = Depends(get_user_auth_service),

) -> Token:

    user_auth.ensure_seed_users(PILOT_SEED_USERS)

    user = user_auth.authenticate_user(form_data.username, form_data.password)

    if user is None:

        raise HTTPException(

            status_code=status.HTTP_401_UNAUTHORIZED,

            detail="Incorrect username or password",

            headers={"WWW-Authenticate": "Bearer"},

        )

    access_token = create_access_token({"sub": user.username, "role": user.role})

    return Token(access_token=access_token)





__all__ = [

    "ROLE_ADMIN",

    "ROLE_INVESTOR",

    "ROLE_SUPERVISOR",

    "ROLE_WORKER",

    "PILOT_SEED_USERS",

    "Token",

    "User",

    "UserInDB",

    "auth_router",

    "oauth2_scheme",

]

