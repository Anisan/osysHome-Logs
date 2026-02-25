import os
import re
from flask import render_template
from app.core.main.BasePlugin import BasePlugin
from app.api import api
from plugins.Logs.api import LOGS_DIR as LOGS_FOLDER

class Logs(BasePlugin):

    def __init__(self,app):
        super().__init__(app,__name__)
        self.title = "Logs"
        self.description = """Logs viewer"""
        self.category = "System"
        self.actions = ["widget"]

        from plugins.Logs.api import create_api_ns
        api_ns = create_api_ns()
        api.add_namespace(api_ns, path="/logs")

    def initialization(self):
        pass

    def admin(self, request):
        # Получаем список файлов в папке LOGS_FOLDER
        log_files = os.listdir(LOGS_FOLDER)

        # Создаем список кортежей, содержащий имя файла и время его последнего изменения
        file_times = [(f, os.path.getmtime(os.path.join(LOGS_FOLDER, f))) for f in log_files]

        # Сортируем список кортежей по времени последнего изменения
        file_times.sort(key=lambda x: x[1], reverse=True)

        # Получаем отсортированный список имен файлов
        log_files = [f[0] for f in file_times]

        selected_log_file = None
        log_content = None

        if request.method == 'POST':
            # Получаем имя выбранного файла из формы
            selected_log_file = request.form['log_file']
            # Читаем последние 50 строк выбранного файла в обратном порядке
            with open(os.path.join(LOGS_FOLDER, selected_log_file), 'r', encoding='utf-8') as f:
                lines = f.readlines()
                log_content = ''.join(lines[-50:][::-1])

        return render_template(
            'logs.html',
            log_files=log_files,
            selected_log_file=selected_log_file,
            log_content=log_content,
        )

    def widget(self, name: str = None):
        error_count = self._get_error_count()
        return self.render(
            "widget_logs_errors.html",
            {
                "error_count": error_count,
                "has_errors": error_count > 0,
                "logs_admin_url": "/admin/Logs",
            },
        )

    def _get_error_count(self) -> int:
        error_log_path = os.path.join(LOGS_FOLDER, "errors.log")
        if not os.path.exists(error_log_path):
            return 0

        # Регулярное выражение ДОЛЖНО полностью совпадать с Vue (`logs.html`):
        # const regex =
        #   /^(\d{2}:\d{2}:\d{2}(?:\.\d{3})?)\[(INFO|ERROR|DEBUG|WARNING|CRITICAL)](?:\[([^\]]*)])*([^\n\r]*)/m;
        # Здесь используем то же самое выражение — считаем записью только строки,
        # которые фронтенд воспринимает как отдельный лог‑вход.
        entry_pattern = re.compile(
            r"^(\d{2}:\d{2}:\d{2}(?:\.\d{3})?)\[(INFO|ERROR|DEBUG|WARNING|CRITICAL)](?:\[([^\]]*)])*([^\n\r]*)"
        )
        count = 0
        try:
            with open(error_log_path, "r", encoding="utf-8", errors="ignore") as error_file:
                for line in error_file:
                    if entry_pattern.match(line):
                        count += 1
            return count
        except OSError:
            self.logger.exception("Failed to read errors.log for widget")
        return 0
