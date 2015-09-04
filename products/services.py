from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.writer.excel import save_virtual_workbook


class CollectLogsService(object):

    def __init__(self, models):
        self.models = models

    def get_history_for_model(self, model):
        objects = model.objects.all()

        logs = (
            log
            for object in objects
            for log in object.history.all()
        )

        return logs

    def process(self):
        logs = (
            log
            for model in self.models
            for log in self.get_history_for_model(model)
        )

        sorted_logs = sorted(
            logs,
            key=lambda log: log.history_date,
            reverse=True
        )

        return sorted_logs


class ExportLogsService(object):
    DATE_TIME_FORMAT = '%d.%m.%Y %H:%M:%S'

    def __init__(self, logs):
        self.logs = logs

    def _write_table_title(self, work_sheet):
        work_sheet.append((
            'Object',
            'Action',
            'User',
            'Date'
        ))

    def _write_log(self, work_sheet, log):
        work_sheet.append((
            str(log.history_object),
            str(log.get_history_type_display()),
            str(log.history_user),
            str(log.history_date.strftime(self.DATE_TIME_FORMAT))
        ))

    def process(self):
        workbook = Workbook()

        work_sheet = workbook.active
        work_sheet.title = 'Logs'

        self._write_table_title(work_sheet)

        for log in self.logs:
            self._write_log(work_sheet, log)

        return save_virtual_workbook(workbook)
