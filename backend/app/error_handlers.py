from flask import request, jsonify
from flask_wtf.csrf import CSRFError
import logging

from core.responses.error_responses import ErrorCodes, error_response

logger = logging.getLogger(__name__)
from flask import current_app as app

def page_not_found(e):
    if request.path.startswith('/api/'):
        return error_response(ErrorCodes.ENDPOINT_NOT_FOUND, "Endpoint not found", 404)
    try:
        return app.send_static_file('404.html'), 404
    except Exception:
        return error_response(ErrorCodes.ENDPOINT_NOT_FOUND, "Not found", 404)


def handle_csrf_error(e):
    logger.warning(f"CSRF Validation Failed: {e.description} | Remote IP: {request.remote_addr}")
    return jsonify({
        "success": False,
        "error": "CSRF_VALIDATION_FAILED",
        "message": f"Security token validation failed: {e.description}. Please refresh the page.",
        "code": 400
    }), 400


def register_error_handlers(app):
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(CSRFError, handle_csrf_error)
