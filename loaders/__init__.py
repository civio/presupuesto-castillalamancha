import six

if six.PY2:
    from castilla_la_mancha_budget_loader import CastillaLaManchaBudgetLoader
else:
    from .castilla_la_mancha_budget_loader import CastillaLaManchaBudgetLoader
