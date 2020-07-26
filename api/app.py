import logging
import socket
import sys
from datetime import date

from flask import Flask, Response, jsonify, request

from api.client import DBClient
from api.model import Actions

root = logging.getLogger()
root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)


def build_routes(client: DBClient):
    app = Flask(__name__)

    @app.route("/health", methods=['GET'])
    def health():
        return {"status": 200}

    @app.route("/actions/<action>", methods=['GET'])
    def get_action(action):
        logging.info(f"GET /actions/{action}")
        limit_today = request.args.get('limit_today', default='True', type=str) == 'True'  # FIXME -> terrible!

        # fail fast with non-standard actions
        if not Actions.contains(action):
            return Response(status=400, response="invalid action")

        logging.info(f"retrieving action -> {action}")

        resp = client.get_actions(Actions[action], limit_today=limit_today)
        return jsonify({"status": 200, "response": resp})

    @app.route("/today", methods=['GET'])
    def get_today():
        logging.info(f"GET /today")
        today = date.today().strftime('%Y-%m-%d')
        logging.info(f"retrieving today -> {today}")

        resp = client.get_today(today)
        return jsonify({"status": 200, "response": resp})

    @app.route("/<action>", methods=['POST'])
    def post_action(action):
        logging.info(f"POST /{action}")

        # fail fast with non-standard actions
        if not Actions.contains(action):
            return jsonify({"status": 400, "response": "invalid action"})

        _ = client.insert_action(Actions[action])

        if action == "lunch":
            _ = client.insert_action(Actions["logoff"])

        return jsonify({"status": 200, "response": "success"})

    return app


if __name__ == "__main__":
    app = build_routes(client=DBClient(db_path="actions.sqlite", table_name="actions"))
    app.run(host=f"{socket.gethostname()}.local", port=8080)
