from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from models.api_model import create_api, update_api, delete_api, list_apis, get_api

bp_api = Blueprint("api", __name__)


@bp_api.route("/apis", methods=["GET"])
def apis_list():
    return jsonify(list_apis())


@bp_api.route("/apis/page", methods=["GET"])
def apis_page():
    # simple helper; frontend can just use /apis
    return jsonify(list_apis())


@bp_api.route("/apis", methods=["POST"])
def api_create():
    data = request.get_json(force=True) or {}
    api_name = data.get("apiName") or data.get("ApiName")
    endpoint = data.get("endpointURL") or data.get("EndpointURL")
    status = data.get("status", "active")
    if not api_name or not endpoint:
        return jsonify({"error": "apiName and endpointURL are required"}), 400

    api_id = create_api(str(api_name), str(endpoint), str(status))
    return jsonify({"ok": True, "apiId": api_id})


@bp_api.route("/apis/<int:api_id>", methods=["PUT"])
def api_update(api_id: int):
    data = request.get_json(force=True) or {}
    api_name = data.get("apiName") or data.get("ApiName")
    endpoint = data.get("endpointURL") or data.get("EndpointURL")
    status = data.get("status", "active")
    if not api_name or not endpoint:
        return jsonify({"error": "apiName and endpointURL are required"}), 400

    update_api(api_id, str(api_name), str(endpoint), str(status))
    return jsonify({"ok": True})


@bp_api.route("/apis/<int:api_id>", methods=["DELETE"])
def api_delete(api_id: int):
    delete_api(api_id)
    return jsonify({"ok": True})


@bp_api.route("/apis/<int:api_id>", methods=["GET"])
def api_details(api_id: int):
    api = get_api(api_id)
    if not api:
        return jsonify({"error": "Not found"}), 404
    return jsonify(api)


@bp_api.route("/manage", methods=["GET"])
def api_manage_page():
    return render_template("api_list.html")
