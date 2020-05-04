class CurrencyConverter:

    # 25/04/20 by Google [Data provided by Morningstar for Currency and Coinbase for Cryptocurrency]
    RATES = {
        "GBP": 1.24,
        "EUR": 1.08,
        "CHF": 1.03,
        "USD": 1,
        "CAD": 0.71,
        "SGD": 0.70,
        "AUD": 0.64,
        "NZD": 0.60,
        "BGN": 0.55,
        "PEN": 0.29,
        "ILS": 0.28,
        "SAR": 0.27,
        "AED": 0.27,
        "QAR": 0.27,
        "PLN": 0.24,
        "MYR": 0.23,
        "RON": 0.22,
        "BRL": 0.18,
        "DKK": 0.15,
        "CNY": 0.14,
        "HRK": 0.14,
        "TRY": 0.14,
        "HKD": 0.13,
        "INR": 0.013,
        "SEK": 0.099,
        "NOK": 0.094,
        "EGP": 0.063,
        "ZAR": 0.053,
        "MXN": 0.040,
        "CZK": 0.040,
        "TWD": 0.033,
        "THB": 0.031,
        "PHP": 0.020,
        "RUB": 0.013,
        "JPY": 0.0093,
        "PKR": 0.0062,
        "HUF": 0.0030,
        "NGN": 0.0026,
        "KZT": 0.0023,
        "CLP": 0.0012,
        "TZS": 0.00043,
        "COP": 0.00025,
        "IDR": 0.000064,
        "VND": 0.000043,
    }

    def __init__(self, currency, value):
        self.currency = currency
        self.value = value
        pass

    def to_usd(self):
        return self.value * self.RATES[self.currency]
