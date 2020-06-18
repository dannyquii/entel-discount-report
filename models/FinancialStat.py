import decimal


class FinancialStat:
    """Estadística financiera vicunala a una glosa."""

    def __init__(self):
        self.count = 0
        self.discount = decimal.Decimal(0)
        pass

    def merge(self, other):
        self.count += other.count
        self.discount = self.discount + other.discount
