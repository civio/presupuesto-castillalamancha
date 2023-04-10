# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
import csv
import os
import re


class CastillaLaManchaBudgetLoader(SimpleBudgetLoader):

    sections_mapping = {
        '02': '1',
        '03': '2',
        '04': '3',
        '05': '4',
        '06': '5',
        '07': '6',
        '11': '7',
        '15': '8',
        '17': '9',
        '18': 'A',
        '19': 'B',
        '20': 'C',
        '21': 'D',
        '22': 'E',
        '23': 'F',
        '26': 'G',
        '27': 'H',
        '50': 'I',
        '51': 'J',
        '55': 'K',
        '56': 'L',
        '57': 'M',
        '61': 'N',
        '70': 'O',
        '80': 'P',
        '81': 'Q'
    }

    def _get_fc_code(self, value):
        # We got 3- or 4- digit functional codes as input, so add a trailing zero
        fc_code = value.strip()
        fc_code = fc_code.ljust(4, '0')
        return fc_code

    def _get_ec_code(self, value):
        # On economic codes we get the first three digits (everything but last two)
        ec_code = value.strip()
        ec_code = ec_code[:-2]
        return ec_code

    def _get_item_number(self, value):
        # Item numbers are the last two digits from the economic codes (fourth and fifth digit)
        item_number = value.strip()
        item_number = item_number[-2:]
        return item_number

    def _get_ic_code(self, value):
        # We got 3- or 4- digit organic codes as input, so add a prefixing zero (also add a trailing one to fill up the department)
        ic_code = value.rjust(4, '0') + '0'
        # But we need just one digit for the institutional breakdown section grouping, and as the section is comprised by the two
        # first digits, we need to map them to just one char in order for the breakdown grouping to work properly
        ic_code = self.sections_mapping.get(ic_code[:2], 'Z') + ic_code[-3:]
        return ic_code

    def _get_description(self, value):
        # Description
        description = value.strip()
        return description

    def _get_amount(self, value):
        # Parse amount
        amount = value.strip()
        amount = self._parse_amount(amount)
        return amount

    # Parse an input line into fields
    def parse_item(self, filename, line):
        # Type of data
        is_expense = filename.find('gastos.csv') != -1
        is_actual = filename.find('/ejecucion_') != -1

        # Execution
        if is_actual:
            # Expenses
            if is_expense:
                fc_code = self._get_fc_code(line[8])
                ec_code = self._get_ec_code(line[16])
                item_number = self._get_item_number(line[16])
                ic_code = self._get_ic_code(line[2])
                description = self._get_description(line[17])
                amount = self._get_amount(line[18])

                return {
                    'is_expense': True,
                    'is_actual': True,
                    'fc_code': fc_code,
                    'ec_code': ec_code,
                    'ic_code': ic_code,
                    'item_number': item_number,
                    'description': description,
                    'amount': amount,
                }

            # Income
            else:
                ec_code = self._get_ec_code(line[10])
                item_number = self._get_item_number(line[10])
                ic_code = self._get_ic_code(line[2])
                description = self._get_description(line[11])
                amount = self._get_amount(line[12])

                return {
                    'is_expense': False,
                    'is_actual': True,
                    'ec_code': ec_code,
                    'ic_code': ic_code,
                    'item_number': item_number,
                    'description': description,
                    'amount': amount,
                }

        # Budget
        else:
            # Expenses
            if is_expense:
                fc_code = self._get_fc_code(line[10])
                ec_code = self._get_ec_code(line[18])
                item_number = self._get_item_number(line[18])
                ic_code = self._get_ic_code(line[2])
                description = self._get_description(line[19])
                amount = self._get_amount(line[25])

                return {
                    'is_expense': True,
                    'is_actual': False,
                    'fc_code': fc_code,
                    'ec_code': ec_code,
                    'ic_code': ic_code,
                    'item_number': item_number,
                    'description': description,
                    'amount': amount,
                }

            # Income
            else:
                ec_code = self._get_ec_code(line[12])
                item_number = self._get_item_number(line[12])
                ic_code = self._get_ic_code(line[2])
                description = self._get_description(line[13])
                amount = self._get_amount(line[17])

                return {
                    'is_expense': False,
                    'is_actual': False,
                    'ec_code': ec_code,
                    'ic_code': ic_code,
                    'item_number': item_number,
                    'description': description,
                    'amount': amount,
                }

    # We override this method in order to be able to change the institutional code check
    def load_budget_items(self, budget, budget_items):
        # Since the incoming data is not fully classified along the four dimensions we defined
        # for the main budget (Aragón, the good one), we are forced to assign the items a
        # catch-all fake category. (Leaving the category blank would be another possibility,
        # but we'd have to modify the DB structure for that, and also our breakdown queries,
        # so I'm going this slightly hackier way first.)
        dummy_fdc = FundingCategory(
            expense=True,  # True/False doesn't really matter
            source='X',
            fund_class=None,
            fund=None,
            description='Desconocido',
            budget=budget,
        )
        dummy_fdc.save()

        # Income data is often not classified functionally, but we need every budget item to be classified
        # along all dimensions (at least for now), because of the way we denormalize/join the data in the app.
        # So we create a fake functional category that will contain all the income data.
        dummy_fc = FunctionalCategory(
            area='X',
            policy='XX',
            function='XXX',
            programme='XXXX',
            subprogramme='XXXX',
            description='Ingresos',
            budget=budget,
        )
        dummy_fc.save()

        # Store data in the database
        budgeted_income = 0
        budgeted_expense = 0
        for item in budget_items:
            # Ignore null entries or entries with no amount
            if item is None or item['amount'] == 0:
                continue

            # Check whether budget income and expense match
            if not item['is_actual']:
                if item['is_expense']:
                    budgeted_expense += item['amount']
                else:
                    budgeted_income += item['amount']

            # Fetch economic category
            ec = EconomicCategory.objects.filter(
                expense=item['is_expense'],
                chapter=item['ec_code'][0],
                article=item['ec_code'][0:2] if len(item['ec_code']) >= 2 else None,
                heading=item['ec_code'][0:3] if len(item['ec_code']) >= 3 else None,
                subheading=None,
                budget=budget,
            )
            if not ec:
                print u"ALERTA: No se encuentra la categoría económica de %s '%s' para '%s': %s€" % (
                    "gastos" if item['is_expense'] else "ingresos",
                    item['ec_code'].decode("utf8"),
                    item['description'].decode("utf8"),
                    item['amount'] / 100,
                )
                continue
            else:
                ec = ec[0]

            # Fetch institutional category (the slice ranges are the actual thing we're changing)
            # FIXME: the base class now supports a better way (see La Rioja for example)
            ic = InstitutionalCategory.objects.filter(
                institution=item['ic_code'][0],
                section=item['ic_code'][0:3] if len(item['ic_code']) >= 3 else None,
                department=item['ic_code'] if len(item['ic_code']) >= 4 else None,
                budget=budget,
            )
            if not ic:
                print u"ALERTA: No se encuentra la categoría institucional '%s' para '%s': %s€" % (
                    item['ic_code'].decode("utf8"),
                    item['description'].decode("utf8"),
                    item['amount'] / 100,
                )
                continue
            else:
                ic = ic[0]

            # Fetch functional category, only for expense items
            if item['is_expense']:
                fc = FunctionalCategory.objects.filter(
                    area=item['fc_code'][0:1],
                    policy=item['fc_code'][0:2],
                    function=item['fc_code'][0:3],
                    programme=item['fc_code'][0:4]
                    if self._use_subprogrammes()
                    else item['fc_code'],
                    subprogramme=item['fc_code'] if self._use_subprogrammes() else None,
                    budget=budget,
                )
                if not fc:
                    print u"ALERTA: No se encuentra la categoría funcional '%s' para '%s': %s€" % (
                        item['fc_code'].decode("utf8"),
                        item['description'].decode("utf8"),
                        item['amount'] / 100,
                    )
                    continue
                else:
                    fc = fc[0]
            else:
                fc = dummy_fc

            BudgetItem(
                institutional_category=ic,
                functional_category=fc,
                economic_category=ec,
                funding_category=dummy_fdc,
                item_number=item.get('item_number', ''),
                expense=item['is_expense'],
                actual=item['is_actual'],
                amount=item['amount'],
                description=item['description'],
                budget=budget,
            ).save()

        if budgeted_income != budgeted_expense:
            print "  Info: los ingresos y gastos del presupuesto no coinciden %0.2f <> %0.2f" % (
                budgeted_income / 100.0,
                budgeted_expense / 100.0,
            )

    # We override this method to be able to load per year classification files
    def load_institutional_classification(self, path, budget):
        # The load path is the actual change we make
        reader = csv.reader(
            open(os.path.join(path, 'clasificacion_organica.csv'), 'rb')
        )
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):  # Ignore comments
                continue

            # We need to map the two digits institution code (their section code) to one char
            institution = line[0]
            institution = self.sections_mapping.get(institution, 'Z')
            section = line[1]
            department = line[2]
            description = line[3]

            ic = InstitutionalCategory(
                institution=institution if institution != "" else None,
                section=institution + section if section != "" else None,
                department=institution + section + department
                if department != ""
                else None,
                description=description,
                budget=budget,
            )
            ic.save()
