"""Application configuration.

Values are read from the environment so the same image can run in different
deployments. Sensible defaults are provided for local development.
"""
import os

JWT_SECRET = os.getenv("JWT_SECRET", "cowork-dev-secret-change-me")
JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cowork.db")
