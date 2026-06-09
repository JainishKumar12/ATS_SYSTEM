import logging
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.config import SUPABASE_JWT_SECRET, SUPABASE_URL

logger = logging.getLogger('ats_resume_scorer')

_bearer_scheme = HTTPBearer(auto_error=False) # HTTPBearer extracts the Authorization: Bearer <token> header automatically. auto_error=False means if the header is missing, FastAPI won't immediately throw a 401 — it returns None instead and lets the function handle it manually. This gives you control over the error message.

_ASYMMETRIC_ALGS = ['ES256', 'RS256']

_jwks_client: jwt.PyJWKClient | None = None  # Two JWT verification strategies exist — asymmetric (public/private key pair) and symmetric (shared secret). This file handles both. The | None type hint is Python 3.10+ union syntax — same as Optional[jwt.PyJWKClient].


def _get_jwks_client() -> jwt.PyJWKClient | None:
    global _jwks_client  # global _jwks_client lets the function modify the module-level variable. The early return if already initialized is the singleton pattern — only one client is ever created, then reused. Avoids making a network request on every token verification.
    if _jwks_client is not None:
        return _jwks_client
    if not SUPABASE_URL:
        return None
    jwks_url = f"{SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
    _jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)  # JWKS (JSON Web Key Set) is a standard endpoint that publishes public keys. rstrip('/') prevents double slashes if SUPABASE_URL already ends with /. cache_keys=True, lifespan=3600 caches the public keys for 1 hour — avoids hitting Supabase's JWKS endpoint on every single request.
    return _jwks_client


def _verify_token(token: str) -> dict:
    header = jwt.get_unverified_header(token)  # JWT tokens have three parts: header, payload, signature. The header is readable without verifying the signature — it tells you which algorithm was used to sign it. You need to know the algorithm before you can verify.
    alg = header.get('alg')

    if alg in _ASYMMETRIC_ALGS:
        jwks_client = _get_jwks_client()
        if jwks_client is None:
            raise jwt.InvalidTokenError(
                'SUPABASE_URL not configured — cannot fetch JWKS to verify token'
            )
        signing_key = jwks_client.get_signing_key_from_jwt(token).key   # etches the correct public key from Supabase's JWKS endpoint (uses the kid claim in the JWT header to pick the right key). Then verifies the token's signature using that public key. audience='authenticated' — Supabase sets this on all user tokens, verifying it prevents tokens meant for other services from being accepted.
        return jwt.decode(
            token,
            signing_key,
            algorithms=_ASYMMETRIC_ALGS,
            audience='authenticated',
        )

    if alg == 'HS256':    # Simpler — uses a shared secret string from your .env. Both Supabase and your server know the secret, so the server can verify without a network call. Older Supabase projects use this; newer ones use asymmetric keys.
        if not SUPABASE_JWT_SECRET:
            raise jwt.InvalidTokenError(
                'HS256 token received but SUPABASE_JWT_SECRET is not configured'
            )
        return jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=['HS256'],
            audience='authenticated',
        )

    raise jwt.InvalidTokenError(f'Unsupported JWT algorithm: {alg}')


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing Authorization: Bearer <token> header',
            headers={'WWW-Authenticate': 'Bearer'},  # headers={'WWW-Authenticate': 'Bearer'} is part of the HTTP standard — tells the client what authentication scheme is expected. Many HTTP clients use this header to automatically trigger a login flow.
        )

    if not SUPABASE_URL and not SUPABASE_JWT_SECRET:
        logger.error('Neither SUPABASE_URL (for JWKS) nor SUPABASE_JWT_SECRET configured — cannot verify tokens')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,   # If neither auth method is configured, this is a server misconfiguration — returns 500, not 401. Important distinction: 401 means "you're not authenticated", 500 means "the server itself is broken."
            detail='Auth not configured on the server',
        )

    try:
        payload = _verify_token(creds.credentials)
    # Three separate catches, most specific first — Python matches the first one that fits:
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired — sign in again',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Invalid token: {exc}',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except Exception as exc:
        # PyJWKClient can raise network errors fetching JWKS; surface them as 401
        # so a misconfigured backend doesn't look like a 500 to the user.
        logger.warning(f'JWT verification failed: {exc}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Token verification failed: {exc}',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token missing subject claim',
        )
    return user_id