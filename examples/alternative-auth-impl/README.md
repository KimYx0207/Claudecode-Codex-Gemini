# Alternative Auth Implementation (Integer PK + Token Hash)

This is an alternative implementation of the authentication system with different design choices:

## Key Differences from `src/auth`

| Feature | `src/auth` | This Implementation |
|---------|------------|---------------------|
| **Primary Key** | UUID string | Integer auto-increment |
| **Token Storage** | Plain JWT in `token` field | SHA-256 hash in `token_hash` |
| **Extra Fields** | - | `is_superuser`, `jti` |
| **Base Class** | Separate `database.py` | Inline in `models.py` |
| **Config Pattern** | `@dataclass` + `load()` | `@lru_cache` + `get_settings()` |

## When to Use This

- If you prefer integer primary keys for simplicity
- If you need superuser role distinction
- If you want token hash storage for extra security (tokens not stored in plaintext)

## Files

- `auth/models.py` - ORM models with engine/session setup
- `auth/schemas.py` - Pydantic validation schemas
- `auth/router.py` - FastAPI routes
- `auth/service.py` - Business logic
- `auth/utils.py` - JWT and password utilities
- `auth/dependencies.py` - OAuth2 dependencies
- `core/config.py` - Settings with `@lru_cache`

## Note

This is provided as a reference implementation. The production code is in `src/auth`.
