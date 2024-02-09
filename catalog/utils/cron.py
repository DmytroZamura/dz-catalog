import requests
from django.conf import settings
from catalog.general.models import Currency, CurrencyRate
from _datetime import datetime


def initCurrLangs():
    currensies = Currency.objects.language('en').all()

    for curr in currensies:
        # print(curr.default_name)

        try:
            curr = curr.translate('ru')
            curr.name = curr.default_name
            curr.save()
        except:
            pass

        try:
            curr = curr.translate('uk')
            curr.name = curr.default_name
            curr.save()
        except:
            pass


def refreshRates():
    current_rate = CurrencyRate.objects.first()
    if current_rate.update_date.date() != datetime.now().date():
        url = 'https://data.fixer.io/api/latest?access_key=' + settings.FIXER_KEY + '&base=USD'
        response = requests.get(url).json()
        currensies = Currency.objects.language('en').all()
        rates = response['rates']
        for curr in currensies:

            # print(curr.default_name)

            rate = 0
            try:
                rate = rates[curr.code]
            except:
                print(curr.default_name + ' - no rate')

            if rate != 0:
                try:
                    cur_rate = CurrencyRate.objects.get(currency__code=curr.code, currency_to__code='USD')
                    cur_rate.rate = rate
                    cur_rate.save()
                except CurrencyRate.DoesNotExist:
                    CurrencyRate.objects.create(currency=curr, currency_to_id=1,
                                                rate=rate)
