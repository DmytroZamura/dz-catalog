
from django.core.management.base import BaseCommand
from catalog.supply_request.models import SupplyRequest


def initRequests():
    SupplyRequest.objects.all().update(show_to_supplier=True)


class Command(BaseCommand):
    def handle(self, *args, **options):
        initRequests()
