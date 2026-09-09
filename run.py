from flask import Flask
from app.api.routes import api
import os

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

app.register_blueprint(api)

if __name__ == "__main__":
    app.run(
    debug=True,
    use_reloader=False,
    host="0.0.0.0",
    port=5000
)