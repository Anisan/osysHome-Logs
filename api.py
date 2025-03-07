import os
import datetime
from flask import jsonify
from flask_restx import Namespace, Resource
from app.authentication.handlers import handle_admin_required

LOGS_DIR = 'logs'

_api_ns = Namespace(name="Logs", description="Logs namespace", validate=True)

def create_api_ns():
    return _api_ns

@_api_ns.route("/list", endpoint="logs_list")
class GetLogs(Resource):
    @handle_admin_required
    def get(self):
        """
        Получение списка файлов логов.
        """
        try:
            logs = [
                {
                    "name": filename,
                    "size": os.path.getsize(os.path.join(LOGS_DIR, filename)),
                    "modified": datetime.datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(LOGS_DIR, filename))
                    ).isoformat(),  # Время изменения в ISO формате
                }
                for filename in os.listdir(LOGS_DIR)
                if os.path.isfile(os.path.join(LOGS_DIR, filename))
            ]
            return {"success": True, "result": logs}, 200
        except Exception as e:
            return {"success": False, "error": str(e)}, 500

@_api_ns.route("/<string:filename>", endpoint="log_content")
class GetLogContent(Resource):
    @handle_admin_required
    def get(self, filename):
        """
        Получение содержимого файла лога.
        """
        file_path = os.path.join(LOGS_DIR, filename)

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            return {"success": True, "result": content}, 200
        except Exception as e:
            return {"success": False, "error": str(e)}, 500

    @handle_admin_required
    def delete(self, filename):
        """
        Удаление файла лога.
        """
        file_path = os.path.join(LOGS_DIR, filename)

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404

        try:
            os.remove(file_path)
            return {"success": True, "result": f"File '{filename}' deleted successfully"}, 200
        except Exception as e:
            return {"success": False, "error": str(e)}, 500