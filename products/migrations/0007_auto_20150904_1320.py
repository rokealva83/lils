# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_historicalbox_historicalcustomer_historicalproduct_historicalproductpurchase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='total_weight',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='historicalcustomer',
            name='total_weight',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
