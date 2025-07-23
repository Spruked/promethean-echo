from flask import Blueprint, jsonify

glyphfeed_bp = Blueprint('glyphfeed', __name__)

@glyphfeed_bp.route("/glyphfeed", methods=["GET"])
def glyphfeed():
    return jsonify({"message": "Glyphfeed endpoint"})
