# -*- coding: UTF-8 -*-
from budget_app.loaders import SimpleBudgetLoader


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
        '76': 'P',
        '77': 'Q',
        '80': 'R',
        '81': 'S'
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
                    **self._institutional_fields(ic_code),
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
                    **self._institutional_fields(ic_code),
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
                    **self._institutional_fields(ic_code),
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
                    **self._institutional_fields(ic_code),
                    'item_number': item_number,
                    'description': description,
                    'amount': amount,
                }

    # Their institutional codes don't follow the default one-character-per-level split:
    # the institution is the first character, the section the first three, and the
    # department the whole code (from four characters on)
    def _institutional_fields(self, ic_code):
        return {
            'ic_institution': ic_code[0],
            'ic_section': ic_code[0:3] if len(ic_code) >= 3 else None,
            'ic_department': ic_code if len(ic_code) >= 4 else None,
        }

    # We need to map the two digits institution code (their section code) to one char.
    # (The classification changes every year, so it lives in each year's folder.)
    def parse_institutional_category(self, line):
        institution, section, department, description = line[:4]
        institution, section, department = self._join_codes(self.sections_mapping.get(institution, 'Z'), section, department)
        return {
            'institution': institution,
            'section': section,
            'department': department,
            'description': description
        }
