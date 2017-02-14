# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
import csv
import os
import re

class CastillaLaManchaBudgetLoader(SimpleBudgetLoader):

    # Parse an input line into fields
    def parse_item(self, filename, line):
        # On economic codes we get the first three digits (everything but last two)
        ec_code = line[2].strip()
        ec_code = ec_code[:-2]

        # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
        item_number = line[2].strip()
        item_number = item_number[-2:]

        # Institutional code (all income goes to the root node)
        ic_code = '0000'

        # Description
        description = line[3].strip()

        # Type of data
        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)

        # Expenses
        if is_expense:
            # We got 3- or 4- digit functional codes as input, so add a trailing zero
            fc_code = line[1].strip()
            fc_code = fc_code.ljust(4, '0')

            # Parse amount
            amount = line[10 if is_actual else 7].strip()
            amount = self._parse_amount(amount)


            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code,
                'ic_code': ic_code,
                'item_number': item_number,
                'description': description,
                'amount': amount
            }

        # Income
        else:
            # Parse amount
            amount = line[7 if is_actual else 4].strip()
            amount = self._parse_amount(amount)

            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code,
                'ic_code': ic_code,
                'item_number': item_number,
                'description': description,
                'amount': amount
            }
