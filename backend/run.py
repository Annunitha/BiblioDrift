# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    from app.config import app_config
    s = app_config.server
    app.run(debug=s.debug, port=s.port, host=s.host)