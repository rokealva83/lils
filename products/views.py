import json
from collections import OrderedDict

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
    TemplateView,
    View
)

from django.views.generic.edit import (
    BaseUpdateView,
)

from django.views.generic.detail import (
    SingleObjectMixin
)

from django.db.models.loading import get_model
from django.shortcuts import get_object_or_404

from django.core.urlresolvers import (
    reverse,
    reverse_lazy
)

from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core import serializers

from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect
)

from braces.views import (
    LoginRequiredMixin,
    StaticContextMixin,
    CsrfExemptMixin,
    SuperuserRequiredMixin,
    PermissionRequiredMixin,
)

from .models import (
    Customer,
    Box,
    ProductPurchase,
    Product,

    PRIORITY
)


from .exporters import get_exporter

from .services import (
    CollectLogsService,
    ExportLogsService
)

from .utils import (
    FileResponseBuilder
)


class PKUrlKwargByModelMixin(object):

    def __new__(cls, *args, **kwargs):
        new_cls = super().__new__(cls, *args, **kwargs)

        setattr(
            new_cls,
            'pk_url_kwarg',
            '{}_pk'.format(cls.model._meta.model_name)
        )

        return new_cls


class BaseView(object):
    def get_parents(self):
        parents_list = []

        for model_name, model, pk in self._get_models_by_pk():
            parents_list.append({
                'model_name': model_name,
                'instacnce': get_object_or_404(model, pk=pk),
                'priority': PRIORITY.index(model)
            })

        parents_list.sort(key=lambda i: i['priority'])

        parents = OrderedDict(
            (parent['model_name'], parent['instacnce'])
            for parent in parents_list
        )

        return parents

    def _get_models_by_pk(self):
        for param, pk in self.kwargs.items():
            model_name, _ = param.split('_')
            model = get_model('products', model_name)
            yield model_name, model, pk

    def check(self):
        for _, model, pk in self._get_models_by_pk():
            get_object_or_404(model, pk=pk)

    def get_direct_parent(self):
        parents = list(self.get_parents().values())
        return parents[-1] if parents else None



class BaseListView(LoginRequiredMixin, BaseView, ListView):
    template_name = 'products/base_list.html'

    def get_create_url(self):
        return reverse(self.create_url, kwargs=self.kwargs)

    def get_header(self):
        return self.model._meta.verbose_name_plural.title()

    @property
    def get_queryset(self):
        direct_parent = self.get_direct_parent()

        filter_kwargs = {}

        if direct_parent:
            filter_kwargs = {
                'parent': direct_parent
            }

        return super().get_queryset().filter(**filter_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['header'] = self.get_header()
        context['paths'] = self.get_parents()
        context['create_url'] = self.get_create_url()
        context['verbose_name'] = self.model._meta.verbose_name

        if hasattr(self.model, 'parent'):
            context['parent_verbose_name'] = self.model.parent.field.related_model._meta.verbose_name
            context['parent'] = self.get_direct_parent()

        return context


class BaseExportView(PKUrlKwargByModelMixin,
                     SingleObjectMixin,
                     BaseView,
                     View):

    def get_exporter(self):
        return get_exporter(self.model)

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        exporter = self.get_exporter()

        object_exported = exporter.export(object)

        response = HttpResponse(
            content=object_exported,
            content_type=exporter.content_type,
        )
        response['Content-Disposition'] = \
                             'attachment; filename="{}.xlsx"'.format(object)
        response['Content-Length'] = len(object_exported)

        return response


class BaseCreateView(LoginRequiredMixin, BaseView, CreateView):
    template_name = 'products/base_create.html'

    fields = (
        'name',
    )

    def form_valid(self, form):
        item = form.save(commit=False)

        item.parent = self.get_direct_parent()
        item.save()

        messages.success(
            self.request,
            _('{type} <b>{name}</b> was successeful created!').format(
                type=item._meta.verbose_name.title(),
                name=str(item)
            )
        )

        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        request = super().get(request, *args, **kwargs)

        self.check()

        return request

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_name'] = self.model._meta.verbose_name
        return context


class BaseDeleteView(SuperuserRequiredMixin,
                     PKUrlKwargByModelMixin,
                     BaseView,
                     DeleteView):

    template_name = 'products/base_confirm_delete.html'



# Customer


class CustomerMixin(object):
    model = Customer


class CustomerListView(CustomerMixin, BaseListView):
    create_url = 'customer-create'
    template_name = 'products/customer_list.html'


class CustomerCreateView(CustomerMixin, BaseCreateView):
    fields = (
        'name',
        'invoice',
        'total_weight',
    )


class CustomerDeleteView(CustomerMixin,  BaseDeleteView):
    success_url = reverse_lazy('customer-list')


class CustomerExportView(CustomerMixin, BaseExportView):
    pass


class CustomerUpdateView(CustomerMixin, UpdateView):
    fields = (
        'invoice',
        'total_weight',
    )


# Box


class BoxMixin(object):
    model = Box


class BoxListView(BoxMixin, BaseListView):
    template_name = 'products/box_list.html'

    create_url = 'box-create'


class BoxCreateView(BoxMixin, BaseCreateView):
    pass


class BoxDeleteView(BoxMixin, BaseDeleteView):

    def get_success_url(self):
        return self.get_object().parent.get_absolute_url()


class BoxExportView(BoxMixin, BaseExportView):
    pass


class BoxToggleCloseView(LoginRequiredMixin, BoxMixin, SingleObjectMixin, View):

    def get(self, request, *args, **kwargs):
        box = self.get_object()

        box.is_closed = not box.is_closed
        box.save()

        if box.is_closed:
            messages.success(
                request,
                _('Now <b>{}</b> is <b>Closed</b>').format(str(box).title())
            )
        else:
            messages.success(
                request,
                _('Now <b>{}</b> is <b>Open</b>').format(str(box).title())
            )

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# Product


class ProductMixin(object):
    model = ProductPurchase


class ProductUpdateView(
    PKUrlKwargByModelMixin,
    PermissionRequiredMixin,
    ProductMixin,
    UpdateView):

    permission_required = 'products.change_productpurchase'

    def get_success_url(self):
        object = self.get_object()

        return reverse('product-list', kwargs={
            'customer_pk': object.parent.parent.pk,
            'box_pk': object.parent.pk,
        })

    def get_initial(self):
        object = self.get_object()

        return {
            'order_override': object.order,
            'quantity_override': object.quantity
        }

    fields = (
        'order_override',
        'quantity_override',
    )


class ProductListView(ProductMixin, BaseListView):
    create_url = 'product-create'
    template_name = 'products/product_list.html'


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response


class ProductCreateView(ProductMixin,
                        CsrfExemptMixin,
                        AjaxableResponseMixin,
                        BaseCreateView):

    fields = (
        'product',
        'quantity_override',
    )

    template_name = 'products/create_purchase.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['previous_page'] = reverse(
            'product-list',
            kwargs=self.kwargs
        )

        return context

    def get_success_url(self):
        return reverse('product-list', kwargs=self.kwargs)


class ProductDeleteView(ProductMixin, BaseDeleteView):

    def get_success_url(self):
        return self.get_object().parent.get_absolute_url()


class ProductSearchView(ProductMixin, LoginRequiredMixin, View):

    def serialize_product(self, product):
        return {
            'id': product.pk,
            'barcode': product.barcode,
            'order': product.order,
            'name': product.name,
            'quantity': product.quantity,
        }

    def get(self, request, *args, **kwargs):

        barcode = kwargs.get('barcode')

        if barcode is not None:
            products = [
                self.serialize_product(p)
                for p in Product.objects.filter(barcode=barcode)
            ]

            return JsonResponse(products, safe=False)


class BaseLogsView(SuperuserRequiredMixin):
    models_with_history = (
        Customer,
        Box,
        ProductPurchase
    )


class LogsView(BaseLogsView,
               TemplateView):

    template_name = 'products/logs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        collect_logs_service = CollectLogsService(self.models_with_history)

        context['logs'] = collect_logs_service.process()

        return context


class LogsExportView(BaseLogsView,
                     View):

    CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    FILENAME = 'logs.xlsx'

    def get(self, request, *args, **kwargs):
        collect_logs_service = CollectLogsService(self.models_with_history)
        logs = collect_logs_service.process()

        export_logs_service = ExportLogsService(logs)
        raw_data = export_logs_service.process()

        response_builder = FileResponseBuilder(
            response_class=HttpResponse,
            content=raw_data,
            content_type=self.CONTENT_TYPE,
            filename=self.FILENAME,
        )

        return response_builder.build()
