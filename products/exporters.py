from openpyxl import (
    Workbook
)

from openpyxl.styles import (
    Font
)

from openpyxl.writer.excel import save_virtual_workbook


class Exporter(object):

    def export(self, model):
        raise NotImplementedError()


class BoxExporter(Exporter):
    metadata_font = Font(
        size=20,
        bold=True
    )

    table_header_font = Font(
        bold=True
    )

    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def _write_customer_title(self, work_sheet, customer):
        work_sheet.append((
            'Customer', str(customer),
        ))

        row = self._get_last_row(work_sheet)
        row.font = self.metadata_font

        if customer.invoice:
            work_sheet.append((
                'Invoice', customer.invoice,
            ))

            row = self._get_last_row(work_sheet)
            row.font = self.metadata_font


    def _write_box_title(self, work_sheet, box):
        work_sheet.append((
            'Box', str(box),
        ))

        row = self._get_last_row(work_sheet)
        row.font = self.metadata_font

    def _write_customer_total_weight(self, work_sheet, customer):
        if customer.total_weight:
            work_sheet.append((
                'Total weight', customer.total_weight
            ))

            row = self._get_last_row(work_sheet)
            row.font = self.metadata_font

    def _write_product_table_header(self, work_sheet):
        work_sheet.append((
            'Barcode',
            'Name',
            'Order',
            'Quantity',
        ))

        row = self._get_last_row(work_sheet)
        row.font = self.table_header_font

    def _write_empty_line(self, work_sheet):
        work_sheet.append([])

    def _get_last_row(self, work_sheet):
        rows = work_sheet.row_dimensions
        return rows[max(rows.keys())]

    def _write_product_table_row(self, work_sheet, product):
        work_sheet.append((
            product.barcode,
            product.name,
            product.order,
            product.quantity,
        ))

    def export(self, box):
        work_book = Workbook()

        work_sheet = work_book.active
        work_sheet.title = 'Box'

        self._write_customer_title(work_sheet, box.parent)
        self._write_box_title(work_sheet, box)
        self._write_empty_line(work_sheet)
        self._write_product_table_header(work_sheet)

        for product in box.productpurchase_set.all():
            self._write_product_table_row(work_sheet, product)

        return save_virtual_workbook(work_book)


class CustomerExporter(BoxExporter):

    def export(self, customer):
        work_book = Workbook()

        work_sheet = work_book.active
        work_sheet.title = 'Boxs'

        self._write_customer_title(work_sheet, customer)
        self._write_customer_total_weight(work_sheet, customer)

        self._write_empty_line(work_sheet)

        for box in customer.box_set.all():
            self._write_box_title(work_sheet, box)
            self._write_product_table_header(work_sheet)
            for product in box.productpurchase_set.all():
                self._write_product_table_row(work_sheet, product)
            self._write_empty_line(work_sheet)

        return save_virtual_workbook(work_book)


from .models import Box, Customer

__exporters_instances = {
    Box: BoxExporter(),
    Customer: CustomerExporter(),
}

def get_exporter(model):
    return __exporters_instances[model]
