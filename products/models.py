from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from simple_history.models import HistoricalRecords


class AbstractNamedItem(models.Model):
    name = models.CharField(
        max_length=120,
        verbose_name=_('name'),
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class HistoryURLMixin(object):

    def get_history_url(self):
        return reverse('admin:products_{model_name}_history'.format(
            model_name=self._meta.model_name
        ), args=[self.pk])



class AbstractTreeItem(models.Model):

    def get_path(self):
        path = []
        current = self

        while current is not None:
            path.append(current)
            current = current.parent if hasattr(current, 'parent') else None

        return reversed(path)

    class Meta:
        abstract = True


class AbstractNamedTreeItem(AbstractNamedItem, AbstractTreeItem):

    class Meta:
        abstract = True


class ChildMetaMixin(object):
    unique_together = (
        'name',
        'parent',
    )


class Customer(AbstractNamedTreeItem, HistoryURLMixin):
    history = HistoricalRecords()

    invoice = models.CharField(
        max_length=100,
        blank=True,
    )

    total_weight = models.CharField(
        blank=True,
        null=True,
        max_length=256,
    )

    @property
    def is_closed(self):
        return self.box_set.filter(is_closed=True).count() == self.box_set.count()


    def get_absolute_url(self):
        return reverse('box-list', kwargs={
            'customer_pk': self.pk
        })

    def get_delete_url(self):
        return reverse('customer-delete', kwargs={
            'customer_pk': self.pk
        })

    def get_export_url(self):
        return reverse('customer-export', kwargs={
            'customer_pk': self.pk
        })

    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')


class Box(AbstractNamedTreeItem, HistoryURLMixin):
    history = HistoricalRecords()

    parent = models.ForeignKey(
        Customer,
        related_name='box_set',
        verbose_name=_('customer')
    )

    is_closed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('product-list', kwargs={
            'customer_pk': self.parent.pk,
            'box_pk': self.pk
        })

    def get_delete_url(self):
        return reverse('box-delete', kwargs={
            'customer_pk': self.parent.pk,
            'box_pk': self.pk,
        })

    def get_export_url(self):
        return reverse('box-export', kwargs={
            'customer_pk': self.parent.pk,
            'box_pk': self.pk,
        })

    class Meta(ChildMetaMixin):
        verbose_name = _('box')
        verbose_name_plural = _('boxes')


class Product(AbstractNamedItem):
    history = HistoricalRecords()

    barcode = models.CharField(
        max_length=64,
        verbose_name=_('barcode')
    )

    order = models.CharField(
        max_length=120,
        verbose_name=_('order')
    )

    quantity = models.PositiveIntegerField(
        verbose_name=_('quantity')
    )

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

        unique_together = (
            'name',
            'barcode',
            'order',
        )


class ProductPurchase(AbstractTreeItem, HistoryURLMixin):
    history = HistoricalRecords()

    parent = models.ForeignKey(
        Box,
        verbose_name=_('box')
    )

    product = models.ForeignKey(
        Product,
    )

    quantity_override = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('quantity')
    )

    order_override = models.CharField(
        max_length=120,
        verbose_name=_('order'),
        blank=True,
        null=True,
    )

    def get_delete_url(self):
        return reverse('product-delete', kwargs={
            'customer_pk': self.parent.parent.pk,
            'box_pk': self.parent.pk,
            'productpurchase_pk': self.pk
        })

    def get_edit_url(self):
        return reverse('product-update', kwargs={
            'customer_pk': self.parent.parent.pk,
            'box_pk': self.parent.pk,
            'productpurchase_pk': self.pk
        })

    @property
    def name(self):
        return self.product.name

    @property
    def barcode(self):
        return self.product.barcode

    @property
    def order(self):
        return self.product.order if self.order_override is None else self.order_override

    @order.setter
    def order(self, value):
        self.order_override = value

    @property
    def quantity(self):
        return self.product.quantity if self.quantity_override is None else self.quantity_override

    @quantity.setter
    def quantity(self, value):
        self.quantity_override = value

    def __str__(self):
        return str(self.product)

    class Meta:
        verbose_name = _('product purchase')
        verbose_name_plural = _('product purchases')

        unique_together = (
            'product',
            'parent'
        )


PRIORITY = (
    Customer,
    Box,
)
