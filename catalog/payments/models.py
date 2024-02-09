from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from catalog.general.models import UnitType, Country, Currency
from catalog.category.models import Category
from django.contrib.auth.models import User
from catalog.company.models import Company
from catalog.post.models import Post
from catalog.product.models import Product
from catalog.user_profile.models import UserProfile
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
import uuid

post_product_codes = ['post-promotion', 'post-grade']


# Create your models here.
class PaymentProduct(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=100),
        description=models.TextField(null=True, blank=True)
    )
    code = models.CharField(max_length=60, unique=True, db_index=True)
    unit_type = models.ForeignKey(UnitType, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["code"]

    def __unicode__(self):
        return self.id


class ProductPrice(models.Model):
    default_name = models.CharField(max_length=150, null=False, blank=True)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, default=None)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    product = models.ForeignKey(PaymentProduct, on_delete=models.CASCADE)
    price_uah = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    price_usd = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)

    def __unicode__(self):
        return self.id


class PaymentAccount(models.Model):
    user = models.OneToOneField(User, related_name='balance', on_delete=models.CASCADE, null=True, blank=True)
    company = models.OneToOneField(Company, related_name='balance', on_delete=models.CASCADE, null=True, blank=True)
    currency = models.ForeignKey(Currency, blank=True, null=True, on_delete=models.SET_NULL)
    balance = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2, default=0)
    update_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id


class PaymentOrder(models.Model):
    id = models.BigAutoField(primary_key=True)
    account = models.ForeignKey(PaymentAccount, related_name='orders', blank=False, null=True,
                                on_delete=models.CASCADE)
    payment_product = models.ForeignKey(PaymentProduct, related_name='orders', blank=False, null=True,
                                        on_delete=models.CASCADE)
    promoted_post = models.ForeignKey(Post, on_delete=models.SET_NULL, blank=True, null=True)
    promoted_company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True)
    promoted_product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    sum = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id


def update_account_on_order_save(sender, instance: PaymentOrder, created, **kwargs):
    if created:
        instance.account.balance = instance.account.balance - instance.sum
        instance.account.save()
        if instance.payment_product.code in post_product_codes and instance.promoted_post:
            if instance.payment_product.code == 'post-promotion':
                instance.promoted_post.promotion = True
                date = datetime.now().date()
                date = date + timedelta(days=instance.quantity + 1)
                instance.promoted_post.promotion_date = date
                instance.promoted_post.promotion_grade = 1
                instance.promoted_post.save()
            if instance.payment_product.code == 'post-grade':
                if not instance.promoted_post.promotion_grade:
                    instance.promoted_post.promotion_grade = 1
                instance.promoted_post.promotion_grade += instance.quantity
                instance.promoted_post.save()


post_save.connect(update_account_on_order_save, sender=PaymentOrder)


class Payment(models.Model):
    account = models.ForeignKey(PaymentAccount, related_name='payments', blank=False, null=False,
                                on_delete=models.CASCADE)
    sum = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2, default=0)
    # order_id = models.CharField(max_length=30, unique=True)
    order_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    confirmed = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    payment_id = models.BigIntegerField(blank=True, null=True)
    callback_link = models.CharField(max_length=250, null=True, blank=True)

    def __unicode__(self):
        return self.id


def update_account_on_payment_save(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Payment.objects.get(pk=instance.pk)
        if old_instance.confirmed == False and instance.confirmed == True and instance.order_id:
            instance.account.balance = instance.account.balance + instance.sum
            instance.account.save()


pre_save.connect(update_account_on_payment_save, sender=Payment)


def check_payment_account(user, company, currency):
    currency_obj = Currency.objects.get(code=currency)
    if company:
        filter_list = Q(company=company)
    else:
        filter_list = Q(user=user)
    try:
        account = PaymentAccount.objects.get(filter_list)
        if account.currency != currency_obj and account.balance == 0:
            account.currency = currency_obj
            account.save()
    except PaymentAccount.DoesNotExist:
        PaymentAccount.objects.create(user=user, company=company, currency=currency_obj, balance=0)


def create_user_payment_account_save(sender, instance, created, **kwargs):
    if created and instance.country:
        if instance.country.code == 'UKR':
            check_payment_account(instance.user, None, 'UAH')
        else:
            check_payment_account(instance.user, None, 'USD')


def check_user_payment_account_on_save(sender, instance, **kwargs):
    if instance.pk:
        old_instance = UserProfile.objects.get(pk=instance.pk)

        if instance.country and old_instance.country != instance.country:
            if instance.country.code == 'UKR':
                check_payment_account(instance.user, None, 'UAH')
            else:
                check_payment_account(instance.user, None, 'USD')


post_save.connect(check_user_payment_account_on_save, sender=UserProfile)
pre_save.connect(check_user_payment_account_on_save, UserProfile)


def create_company_payment_account_save(sender, instance, created, **kwargs):
    if created and instance.country:
        if instance.country.code == 'UKR':
            check_payment_account(None, instance, 'UAH')
        else:
            check_payment_account(None, instance, 'USD')


def check_company_payment_account_on_save(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Company.objects.get(pk=instance.pk)

        if instance.country and old_instance.country != instance.country:
            if instance.country.code == 'UKR':
                check_payment_account(None, instance, 'UAH')
            else:
                check_payment_account(None, instance, 'USD')


post_save.connect(create_company_payment_account_save, sender=Company)
pre_save.connect(check_company_payment_account_on_save, Company)
