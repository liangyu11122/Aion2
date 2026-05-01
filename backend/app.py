"""Flask app factory + entry."""
import os, sys
from flask import Flask, send_from_directory
from flask_cors import CORS

from controllers.search import bp as search_bp
from controllers.character import bp as character_bp
from controllers.proxy import bp as proxy_bp


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(search_bp)
    app.register_blueprint(character_bp)
    app.register_blueprint(proxy_bp)

    # Serve the built Vue SPA from ../frontend/dist when present.
    here = os.path.dirname(os.path.abspath(__file__))
    dist = os.path.normpath(os.path.join(here, "..", "frontend", "dist"))

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path):
        if path and os.path.isfile(os.path.join(dist, path)):
            return send_from_directory(dist, path)
        index = os.path.join(dist, "index.html")
        if os.path.isfile(index):
            return send_from_directory(dist, "index.html")
        return (
            "<h1>Aion 2 backend running.</h1>"
            "<p>Frontend not built. Run <code>cd frontend && npm install && npm run build</code> "
            "or use <code>npm run dev</code> in the frontend folder.</p>",
            200,
        )

    return app


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5180
    app = create_app()
    print(f"Aion 2 backend on http://127.0.0.1:{port}/")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
