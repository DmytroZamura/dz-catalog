from django.test import TestCase
from django.contrib.auth.models import User
from catalog.general.models import Language, Currency
from django.utils import translation


class BaseTestCaseMixin(TestCase):
    class Meta:
        abstract = True

    def setUp(self):
        translation.activate('en')
        lang = Language.objects.language('en').create(code='en', locale_lang=True, name='English')
        lang.translate('uk')
        lang.name = 'Англійська'
        lang.save()

        cur = Currency.objects.language('en').create(id=1, code='USD', number=840, default_name='US Dollar',
                                                     name='US Dollar')
        cur.translate('uk')
        cur.name = 'Долари США'
        cur.save()

        User.objects.create(id=1, username='84b1ba62-b6d1-4563-ad5a-0590213cb5e1', first_name='Dmytro', last_name='One',
                            email='dmitry.zamura@gmail.com', is_active=True)
        User.objects.create(id=2, username='a0286032-4351-4878-9004-934dfe54ccbc', first_name='Dmytro Test',
                            last_name='Two',
                            email='zamura.dmytro@gmail.com', is_active=True)
