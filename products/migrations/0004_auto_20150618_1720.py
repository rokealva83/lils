# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20150611_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='productpurchase',
            name='order_override',
            field=models.CharField(verbose_name='order', null=True, max_length=120, blank=True),
        ),
        migrations.AlterField(
            model_name='productpurchase',
            name='quantity_override',
            field=models.PositiveIntegerField(verbose_name='quantity', null=True, blank=True),
        ),
    ]
