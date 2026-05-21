from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os

# External services / extensions imported from project modules
from cache_service import cache_service
from models import db

# Instantiate extension objects (not bound to app yet)
cors = CORS()
jwt = JWTManager()
csrf = CSRFProtect()
limiter = Limiter(get_remote_address, default_limits=["200 per day", "50 per hour"], storage_uri="memory://")
migrate = Migrate()


def init_extensions(app):
    """Initialize Flask extensions and other app-level services."""
    # Configure CORS with the same options used previously
    cors.init_app(app, supports_credentials=True, origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:5000", "http://localhost:5000"])

    # CSRF, JWT
    csrf.init_app(app)
    jwt.init_app(app)

    # Cache service and DB
    cache_service.init_app(app)
    db.init_app(app)

    # Limiter and migrate
    limiter.init_app(app)
    migrate.init_app(app, db)
