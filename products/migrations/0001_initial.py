# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='name')),
                ('is_closed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'box',
                'verbose_name_plural': 'boxes',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='name')),
                ('invoice', models.CharField(max_length=100, blank=True)),
                ('total_weight', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'customer',
                'verbose_name_plural': 'customers',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='name')),
                ('barcode', models.CharField(max_length=64, verbose_name='barcode')),
                ('order', models.CharField(max_length=120, verbose_name='order')),
                ('quantity', models.PositiveIntegerField(verbose_name='quantity')),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'products',
            },
        ),
        migrations.CreateModel(
            name='ProductPurchase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity_override', models.PositiveIntegerField(default=None, null=True, verbose_name='quantity', blank=True)),
                ('parent', models.ForeignKey(verbose_name='box', to='products.Box')),
                ('product', models.ForeignKey(to='products.Product')),
            ],
            options={
                'verbose_name': 'product purchase',
                'verbose_name_plural': 'product purchases',
            },
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('name', 'barcode')]),
        ),
        migrations.AddField(
            model_name='box',
            name='parent',
            field=models.ForeignKey(related_name='box_set', verbose_name='customer', to='products.Customer'),
        ),
        migrations.AlterUniqueTogether(
            name='productpurchase',
            unique_together=set([('product', 'parent')]),
        ),
        migrations.AlterUniqueTogether(
            name='box',
            unique_together=set([('name', 'parent')]),
        ),
    ]
