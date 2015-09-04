# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20150618_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productpurchase',
            name='quantity_override',
            field=models.PositiveIntegerField(null=True, blank=True, verbose_name='quantity', default=None),
        ),
    ]
