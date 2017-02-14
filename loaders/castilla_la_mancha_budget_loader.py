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
        # Type of data
        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)

        # Execution
        if is_actual:
            # Expenses
            if is_expense:
                # We got 3- or 4- digit functional codes as input, so add a trailing zero
                fc_code = line[8].strip()
                fc_code = fc_code.ljust(4, '0')

                # On economic codes we get the first three digits (everything but last two)
                ec_code = line[16].strip()
                ec_code = ec_code[:-2]

                # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
                item_number = line[16].strip()
                item_number = item_number[-2:]

                # Institutional code (all income goes to the root node)
                ic_code = '0000'

                # Description
                description = line[17].strip()

                # Parse amount
                amount = line[18].strip()
                amount = self._parse_amount(amount)

                return {
                    'is_expense': True,
                    'is_actual': True,
                    'fc_code': fc_code,
                    'ec_code': ec_code,
                    'ic_code': ic_code,
                    'item_number': item_number,
                    'description': description,
                    'amount': amount
                }

            # Income
            else:
                # On economic codes we get the first three digits (everything but last two)
                ec_code = line[10].strip()
                ec_code = ec_code[:-2]

                # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
                item_number = line[10].strip()
                item_number = item_number[-2:]

                # Institutional code (all income goes to the root node)
                ic_code = '0000'

                # Description
                description = line[11].strip()

                # Parse amount
                amount = line[12].strip()
                amount = self._parse_amount(amount)

                return {
                    'is_expense': False,
                    'is_actual': True,
                    'ec_code': ec_code,
                    'ic_code': ic_code,
                    'item_number': item_number,
                    'description': description,
                    'amount': amount
                }
        
        # Budget    
        else:
            # Expenses
            if is_expense:
                # We got 3- or 4- digit functional codes as input, so add a trailing zero
                fc_code = line[10].strip()
                fc_code = fc_code.ljust(4, '0')

                # On economic codes we get the first three digits (everything but last two)
                ec_code = line[18].strip()
                ec_code = ec_code[:-2]

                # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
                item_number = line[18].strip()
                item_number = item_number[-2:]

                # Institutional code (all income goes to the root node)
                ic_code = '0000'

                # Description
                description = line[19].strip()

                # Parse amount
                amount = line[25].strip()
                amount = self._parse_amount(amount)


                return {
                    'is_expense': True,
                    'is_actual': False,
                    'fc_code': fc_code,
                    'ec_code': ec_code,
                    'ic_code': ic_code,
                    'item_number': item_number,
                    'description': description,
                    'amount': amount
                }

            # Income
            else:
                # On economic codes we get the first three digits (everything but last two)
                ec_code = line[10].strip()
                ec_code = ec_code[:-2]

                # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
                item_number = line[10].strip()
                item_number = item_number[-2:]

                # Institutional code (all income goes to the root node)
                ic_code = '0000'

                # Description
                description = line[11].strip()

                # Parse amount
                amount = line[12].strip()
                amount = self._parse_amount(amount)

                return {
                    'is_expense': False,
                    'is_actual': False,
                    'ec_code': ec_code,
                    'ic_code': ic_code,
                    'item_number': item_number,
                    'description': description,
                    'amount': amount
                }
