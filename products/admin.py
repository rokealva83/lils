from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import (
    Customer,
    Box,
    Product,
    ProductPurchase,
)


class ProductResource(resources.ModelResource):

    class Meta:
        model = Product

        fields = (
            'barcode',
            'order',
            'name',
            'quantity'
        )

        export_order = (
            'barcode',
            'order',
            'name',
            'quantity'
        )

        import_id_fields = (
            'barcode',
            'name',
            'order',
        )


class ProductImportExportAdmin(ImportExportModelAdmin):
    resource_class = ProductResource

    list_display = (
        'barcode',
        'name',
        'order',
        'quantity',
    )

# class ProductAdmin(admin.ModelAdmin):


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'parent'
    )


class ProductPurchaseAdmin(SimpleHistoryAdmin):

    list_display = (
        'name',
        'barcode',
        'order',
        'quantity',
    )




class CustomerAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'invoice',
        'total_weight',
        'is_closed',
    )


class BoxAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'is_closed',
    )

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Box, BoxAdmin)
admin.site.register(ProductPurchase, ProductPurchaseAdmin)

admin.site.register(Product, ProductImportExportAdmin)


