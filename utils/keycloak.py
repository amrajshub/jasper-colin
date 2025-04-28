from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from keycloak import KeycloakOpenID


import socket

try:
    socket.gethostbyname("keycloak")
    print("Keycloak hostname resolved successfully")
except socket.gaierror:
    print("Failed to resolve Keycloak hostname")


# Initialize Keycloak OpenID client
keycloak_openid = KeycloakOpenID(
    server_url="http://keycloak:8080/",
    client_id="fastapi-app",
    realm_name="fastapi-realm",
    client_secret_key="bNL45D6yTxhJnTjNCQiG0PcAdKdPEkgk",
)

# OAuth2PasswordBearer is used for getting the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to verify the token
async def verify_token(token: str):
    try:
        # This verifies the token
        userinfo = keycloak_openid.decode_token(token)
        return userinfo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )


# Middleware for authentication
async def auth_middleware(request: Request):
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization token is missing",
        )

    # Bearer token expected in Authorization header
    token = authorization.split(" ")[1]

    user_info = await verify_token(token)  # Verifying the token

    # Attach user info to the request for further use
    request.state.user_info = user_info


async def check_privileges(request: Request):
    user_info = request.state.user_info
    roles = user_info.get("realm_access", {}).get("roles")


def check_privilege(required_role: str):
    async def wrapper(request: Request):
        user_info = request.state.user_info
        roles = user_info.get("realm_access", {}).get("roles")
        if not required_role in roles:
            raise HTTPException(
                detail={"error": "User is not Authorized for the given action"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

    return wrapper
