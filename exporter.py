#!/usr/bin/env python

import sys
import csv


from django.db import transaction
from django.db import IntegrityError

from products.models import Product

def main(filename):
    with open(filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)

        added_products_data = set()
        added_products = []

        for product_data in reader:
            product_data_items = (
                product_data['name'],
                product_data['barcode'],
                product_data['order']
            )

            if product_data_items not in added_products_data:
                added_products_data.add(product_data_items)
                added_products.append(product_data)

        Product.objects.bulk_create(Product(**p) for p in added_products)
