import os
from flask import render_template, request
from app.core.main.BasePlugin import BasePlugin
from app.authentication.handlers import handle_admin_required
from app.api import api

LOGS_FOLDER = 'logs'

class Logs(BasePlugin):

    def __init__(self,app):
        super().__init__(app,__name__)
        self.title = "Logs"
        self.description = """Logs viewer"""
        self.category = "System"

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

        return render_template('logs.html', log_files=log_files, selected_log_file=selected_log_file, log_content=log_content)

