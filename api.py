import os
import datetime
from flask import jsonify, request, send_file
from flask_restx import Namespace, Resource
from app.authentication.handlers import handle_admin_required
from app.configuration import Config

# Директория логов берётся относительно PROJECT_ROOT из конфигурации приложения
LOGS_DIR = os.path.join(Config.APP_DIR, "logs")

_api_ns = Namespace(name="Logs", description="Logs namespace", validate=True)


def _ensure_logs_dir_exists() -> None:
    """
    Ensure that the logs directory exists.
    """
    try:
        os.makedirs(LOGS_DIR, exist_ok=True)
    except OSError:
        # If we can't create the directory, subsequent operations will fail
        # and return a proper error to the client.
        pass


def _safe_log_path(filename: str):
    """
    Build a safe path to a log file and protect against path traversal.
    """
    # Disallow path separators and normalize to basename
    if not filename or os.path.basename(filename) != filename:
        return None

    _ensure_logs_dir_exists()
    return os.path.join(LOGS_DIR, filename)

def create_api_ns():
    return _api_ns

@_api_ns.route("/list", endpoint="logs_list")
class GetLogs(Resource):
    @handle_admin_required
    def get(self):
        """
        Получение списка файлов логов.
        """
        _ensure_logs_dir_exists()
        try:
            logs = [
                {
                    "name": filename,
                    "size": os.path.getsize(_safe_log_path(filename)),
                    "modified": datetime.datetime.fromtimestamp(os.path.getmtime(_safe_log_path(filename))).isoformat(),
                }
                for filename in os.listdir(LOGS_DIR)
                if os.path.isfile(os.path.join(LOGS_DIR, filename))
            ]
            # Сортировка по времени изменения по убыванию (новые сверху)
            logs.sort(key=lambda x: x["modified"], reverse=True)
            return {"success": True, "result": logs}, 200
        except Exception as e:
            return {"success": False, "error": str(e)}, 500

@_api_ns.route("/<string:filename>", endpoint="log_content")
class GetLogContent(Resource):
    @handle_admin_required
    def get(self, filename):
        """
        Получение содержимого файла лога (API, JSON).
        """
        file_path = _safe_log_path(filename)

        if not file_path:
            return jsonify({"error": "Invalid filename"}), 400

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404

        try:
            # Возможность запрашивать только часть файла для больших логов.
            # Сервер дополнительно сообщает, была ли отдана только часть.
            lines_count = request.args.get("lines", type=int)
            position = request.args.get("position", default="end")
            content: str
            truncated = False
            total_lines: int | None = None
            if lines_count and lines_count > 0:
                if position == "start":
                    content, truncated, total_lines = _read_first_lines(file_path, lines_count)
                else:
                    # Эффективное чтение последних N строк
                    content, truncated, total_lines = _read_last_lines(file_path, lines_count)
            else:
                # Читаем весь файл и считаем количество строк
                with open(file_path, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                content = "".join(lines)
                total_lines = len(lines)
            return {
                "success": True,
                "result": content,
                "truncated": truncated,
                "total_lines": total_lines,
            }, 200
        except Exception as e:
            return {"success": False, "error": str(e)}, 500

    @handle_admin_required
    def delete(self, filename):
        """
        Удаление файла лога.
        """
        file_path = _safe_log_path(filename)

        if not file_path:
            return jsonify({"error": "Invalid filename"}), 400

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404

        try:
            os.remove(file_path)
            return {"success": True, "result": f"File '{filename}' deleted successfully"}, 200
        except Exception as e:
            return {"success": False, "error": str(e)}, 500


@_api_ns.route("/<string:filename>/download", endpoint="log_download")
class DownloadLog(Resource):
    @handle_admin_required
    def get(self, filename):
        """
        Скачивание файла лога через браузер.
        """
        file_path = _safe_log_path(filename)

        if not file_path:
            return jsonify({"error": "Invalid filename"}), 400

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404

        try:
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype="text/plain; charset=utf-8",
            )
        except Exception as e:
            return {"success": False, "error": str(e)}, 500


def _read_last_lines(file_path: str, lines_count: int):
    """
    Read last N lines from a file efficiently.
    """
    # Simple and robust implementation: один проход по файлу,
    # deque хранит только последние N+1 строк для определения усечения.
    from collections import deque

    try:
        total_lines = 0
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            tail = deque(maxlen=lines_count + 1)
            for line in f:
                total_lines += 1
                tail.append(line)
        truncated = total_lines > lines_count
        if truncated:
            # Убираем "лишнюю" строку, оставляя ровно N последних
            tail.popleft()
        return "".join(tail), truncated, total_lines
    except OSError:
        # Fall back: читаем весь файл, помечая как не усечённый
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        return "".join(lines), False, len(lines)


def _read_first_lines(file_path: str, lines_count: int):
    """
    Read first N lines from a file.
    """
    try:
        total_lines = 0
        lines: list[str] = []
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                total_lines += 1
                if len(lines) < lines_count:
                    lines.append(line)
        truncated = total_lines > lines_count
        return "".join(lines), truncated, total_lines
    except OSError:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        return "".join(lines), False, len(lines)
