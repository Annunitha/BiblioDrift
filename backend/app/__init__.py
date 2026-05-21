from flask import Flask
import logging
from app.extensions import csrf

from app.config import app_config, setup_logging, validate_required_env_vars
from app.extensions import init_extensions

app = Flask(__name__, static_folder='.', static_url_path='')

def _validate_config():
    is_valid, errors = app_config.validate()
    logger = logging.getLogger(__name__)

    if not is_valid:
        if app_config.is_production():
            logger.critical("=" * 70)
            logger.critical("CRITICAL SECURITY ERROR - APPLICATION REFUSING TO START")
            logger.critical("=" * 70)
            for error in errors:
                logger.critical(f"  - {error}")
            logger.critical("=" * 70)
            import sys
            sys.exit(1)
        else:
            logger.warning("=" * 70)
            logger.warning("WARNING: CONFIGURATION ISSUES DETECTED")
            logger.warning("=" * 70)
            for error in errors:
                logger.warning(f"  - {error}")
            logger.warning("=" * 70)
    else:
        if app_config.is_development():
            logger.info("=" * 70)
            logger.info("CONFIGURATION VALIDATION: OK")
            logger.info("=" * 70)
            logger.info(f"Environment: {app_config.get_environment_name()}")
            logger.info(f"Rate limiting: {'Enabled' if app_config.rate_limit.enabled else 'Disabled'}")
            logger.info("=" * 70)


def create_app():
    # Validate required environment vars and configure app
    validate_required_env_vars()

    # Setup logging early
    setup_logging(app_config)
    logger = logging.getLogger(__name__)

    app.config.update(app_config.flask_config)

    # Validate config values (JWT secret checks etc.)
    _validate_config()

    # Initialize extensions, middleware, error handlers, and security headers
    init_extensions(app)

    # Lazy imports to avoid circular dependencies
    from app.middleware import register_middleware
    from app.error_handlers import register_error_handlers
    from app.security import register_security_headers
    from reader_identity.routes import reader_identity_bp

    register_middleware(app)
    register_error_handlers(app)
    register_security_headers(app)

    app.register_blueprint(reader_identity_bp)
    from api.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    from api.mood.routes import mood_bp
    app.register_blueprint(mood_bp)
    from api.books.routes import books_bp
    app.register_blueprint(books_bp)
    csrf.exempt(auth_bp)

    # Ensure DB tables exist
    from models import db
    with app.app_context():
        db.create_all()

    return app

