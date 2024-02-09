from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from catalog.company.models import Company
from catalog.general.models import Currency
from catalog.product.models import Product
from catalog.file.models import File
from catalog.messaging.models import Chat, ChatParticipant, create_message
from django.db.models.signals import post_save, post_delete, pre_save
from hvad.models import TranslatableModel, TranslatedFields
from django.db.models import Sum, F, Func
from catalog.getstream.utils import create_notification_by_instance
from hvad.utils import get_translation
from django.core.exceptions import ObjectDoesNotExist


class Round(Func):
    function = 'ROUND'
    arity = 2

open_request_statuses_supplier = ['posted', 'confirm', 'confirmed', 'processing']
open_request_statuses_customer = ['new','posted', 'confirm', 'confirmed', 'processing']

class SupplyRequestStatus(TranslatableModel):
    code = models.CharField(max_length=10, null=True, unique=True)
    is_open = models.BooleanField(default=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )
    position = models.IntegerField(null=True, blank=True)
    icon = models.CharField(max_length=40, null=True, blank=True)
    color_class = models.CharField(max_length=20, null=True, blank=True)

    def get_status_name_in_lang(self, lang):

        try:
            trans = get_translation(self, lang)
        except ObjectDoesNotExist:
            trans = get_translation(self, 'en')

        return trans.name

    def __unicode__(self):
        return self.code


class SupplyRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer_user = models.ForeignKey(User, related_name='customer_user_requests', null=True, blank=True,
                                      on_delete=models.SET_NULL)
    customer_company = models.ForeignKey(Company, blank=True, null=True, related_name='customer_company_requests',
                                         on_delete=models.SET_NULL)
    customer_comment = models.TextField(null=True, blank=True)
    contact_email = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    skype = models.CharField(max_length=50, null=True, blank=True)
    supplier_user = models.ForeignKey(User, blank=True, null=True, related_name='supplier_user_requests',
                                      on_delete=models.SET_NULL)
    supplier_company = models.ForeignKey(Company, blank=True, null=True, related_name='supplier_company_requests',
                                         on_delete=models.SET_NULL)
    supplier_comment = models.TextField(null=True, blank=True)
    supplier_request_id = models.CharField(max_length=25, null=True, blank=True)
    status = models.ForeignKey(SupplyRequestStatus, on_delete=models.SET_NULL, null=True, blank=False)
    need_confirmation = models.BooleanField(default=False)
    show_to_supplier = models.BooleanField(default=False)
    currency = models.ForeignKey(Currency, blank=True, null=True, on_delete=models.SET_NULL)
    charges = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    charges_comment = models.CharField(max_length=1000, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    delivery_address = models.CharField(max_length=350, null=True, blank=True)

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


    canceled_by = models.ForeignKey(User, blank=True, null=True, related_name='canceled_requests',
                                    on_delete=models.SET_NULL)

    @property
    def activity_object_serializer_class(self):
        from .serializers import SupplyRequestSerializer
        return SupplyRequestSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import SupplyRequestSmallSerializer
        return SupplyRequestSmallSerializer

    def calculate_total_amount(self):
        total = 0
        if self.positions.exists():
            ammount = self.positions.aggregate(total=Sum(Round(F('price') * F('quantity'), 2)))
            total = ammount['total']
        if self.charges:
            total = total + self.charges
        return total

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total_amount()

        return super(SupplyRequest, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id


def new_supplier_request_qty(instance):
    if instance.supplier_company:
        instance.supplier_company.eventsqty.update_events_qty('new_customer_requests', 1)
        instance.supplier_company.eventsqty.update_events_qty('open_customer_requests', 1)
    else:
        instance.supplier_user.user_profile.eventsqty.update_events_qty('new_customer_requests', 1)
        instance.supplier_user.user_profile.eventsqty.update_events_qty('open_customer_requests', 1)


def update_request_objects_qty(sender, instance, created, **kwargs):
    if created:
        if instance.customer_company:
            instance.customer_company.eventsqty.update_events_qty('your_open_supply_requests', 1)
        else:
            instance.customer_user.user_profile.eventsqty.update_events_qty('your_open_supply_requests', 1)

        if instance.status.code == 'posted':
            new_supplier_request_qty(instance)


post_save.connect(update_request_objects_qty, sender=SupplyRequest)


def delete_request_objects_qty(sender, instance, **kwargs):
    if instance.status.code in open_request_statuses_customer:
        if instance.customer_company:
            instance.customer_company.eventsqty.update_events_qty('your_open_supply_requests', -1)
        else:
            instance.customer_user.user_profile.eventsqty.update_events_qty('your_open_supply_requests', -1)

    if instance.status.code in open_request_statuses_supplier:
        if instance.supplier_company:
            instance.supplier_company.eventsqty.update_events_qty('open_customer_requests', -1)
            if instance.status.code == 'posted':
                instance.supplier_company.eventsqty.update_events_qty('new_customer_requests', -1)

        else:
            instance.supplier_user.user_profile.eventsqty.update_events_qty('open_customer_requests', -1)
            if instance.status.code == 'posted':
                instance.supplier_user.user_profile.eventsqty.update_events_qty('new_customer_requests', -1)


post_delete.connect(delete_request_objects_qty, sender=SupplyRequest)


def check_request_objects_qty_on_save(sender, instance, **kwargs):
    try:
        old_request = SupplyRequest.objects.get(pk=instance.pk)
    except SupplyRequest.DoesNotExist:
        old_request = None

    if old_request:
        if old_request.status != instance.status:
            if old_request.status.code == 'new' and instance.status.code == 'posted':
                supplier_notification(instance)
                new_supplier_request_qty(instance)
            else:
                if old_request.status.code != 'new' and instance.status.code != 'c_canceled':
                    create_notification_by_instance(instance, 'status_changed')

            if old_request.status.is_open and not instance.status.is_open:

                if instance.customer_company:
                    instance.customer_company.eventsqty.update_events_qty('your_open_supply_requests', -1)
                else:
                    instance.customer_user.user_profile.eventsqty.update_events_qty('your_open_supply_requests', -1)

                if instance.supplier_company:
                    instance.supplier_company.eventsqty.update_events_qty('open_customer_requests', -1)
                else:
                    instance.supplier_user.user_profile.eventsqty.update_events_qty('open_customer_requests', -1)

            if not old_request.status.is_open and instance.status.is_open:

                if instance.customer_company:
                    instance.customer_company.eventsqty.update_events_qty('your_open_supply_requests', 1)
                else:
                    instance.customer_user.user_profile.eventsqty.update_events_qty('your_open_supply_requests', 1)
                if instance.supplier_company:
                    instance.supplier_company.eventsqty.update_events_qty('open_customer_requests', 1)
                else:
                    instance.supplier_user.user_profile.eventsqty.update_events_qty('open_customer_requests', 1)


pre_save.connect(check_request_objects_qty_on_save, sender=SupplyRequest)


class SupplyRequestChat(models.Model):
    supply_request = models.OneToOneField(SupplyRequest, related_name="chat", primary_key=True)
    chat = models.OneToOneField(Chat, related_name="request")

    class Meta:
        unique_together = ("supply_request", "chat")

    def __unicode__(self):
        return self.id


def set_supply_request_chat(supply_request_id):
    try:
        chat = Chat.objects.get(request__supply_request=supply_request_id)
    except:
        chat = Chat(type=2)
        chat.save()
        request_chat = SupplyRequestChat(supply_request_id=supply_request_id, chat=chat)
        request_chat.save()

        supply_request = SupplyRequest.objects.get(pk=supply_request_id)
        if supply_request.customer_company_id:
            participant = ChatParticipant(chat=chat, company_id=supply_request.customer_company_id, customer=True)
            participant.save()
        else:
            participant = ChatParticipant(chat=chat, user_id=supply_request.customer_user_id, customer=True)
            participant.save()

        if supply_request.supplier_company_id:
            participant = ChatParticipant(chat=chat, company_id=supply_request.supplier_company_id, supplier=True)
            participant.save()
        else:
            participant = ChatParticipant(chat=chat, user_id=supply_request.supplier_user_id, supplier=True)
            participant.save()
    return chat.id


def supplier_notification(instance):
    chat_id = set_supply_request_chat(instance.id)
    comment = '<h3><b>№' + str(instance.id) + '</b></h3>'
    if instance.customer_comment:
        comment = comment + instance.customer_comment
    create_message(chat_id, 5, instance.customer_user_id, instance.customer_company_id,
                   comment)  # type 5 - request message
    create_notification_by_instance(instance)


def supplier_notification_on_create(sender, instance, created, **kwargs):
    if created and instance.status.code == 'posted':
        supplier_notification(instance)


post_save.connect(supplier_notification_on_create, sender=SupplyRequest)


class SupplyRequestNote(models.Model):
    id = models.BigAutoField(primary_key=True)
    supply_request = models.ForeignKey(SupplyRequest)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason_win_lost = models.CharField(max_length=350, null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("supply_request", "user")

    def __unicode__(self):
        return self.id


class SupplyRequestDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    supply_request = models.ForeignKey(SupplyRequest, related_name='documents')
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("supply_request", "file")

    def __unicode__(self):
        return self.id


class SupplyRequestPosition(models.Model):
    id = models.BigAutoField(primary_key=True)
    supply_request = models.ForeignKey(SupplyRequest, related_name='positions', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True)

    def _get_position_total(self):
        total = 0
        if self.price and self.quantity:
            total = round(self.price * self.quantity, 2)
        return total

    total = property(_get_position_total)

    class Meta:
        unique_together = ("supply_request", "product")

    def __unicode__(self):
        return self.id


def calculate_total_ammount_on_save(sender, instance, created=False, **kwargs):
    total = instance.supply_request.calculate_total_amount()
    instance.supply_request.total_amount = total
    if instance.supply_request.status.code == 'posted' and not created:
        instance.supply_request.need_confirmation = True

    instance.supply_request.save()


post_save.connect(calculate_total_ammount_on_save, sender=SupplyRequestPosition)
post_delete.connect(calculate_total_ammount_on_save, sender=SupplyRequestPosition)
