from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, SecurityScopes
from app.src.services.organization_service.http import OrganizationServices


async def verify_token(token: str = Depends(HTTPBearer())):
    is_success, authorized_user = await OrganizationServices.check_authorization(token.credentials)
    if is_success is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication not valid, please check your user account")
    authorized_user['user_token'] = token.credentials
    return authorized_user


async def check_permission(
    security_scopes: SecurityScopes,
    current_user: [] = Security(verify_token, scopes=[]),
):
    permission = list(
        filter(
            lambda x: x["permission_page"] in security_scopes.scopes,
            current_user["permission"],
        )
    )

    if len(permission) == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to access this API. Please ask Administrator for further information",
        )

    return current_user
