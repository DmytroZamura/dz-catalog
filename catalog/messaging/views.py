from .serializers import ChatSerializer, MessageSerializer
from .models import Chat, ChatParticipant, Message, set_user_contact_chat, set_user_with_company_chat, create_message
from catalog.user_profile.models import UserAction
from catalog.general.models import Translation
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsOwner, IsParticipant, IsMessageChatParticipant
from catalog.company.permissions import IsOwnerOrCompanyAdmin, IsOwnerOrCompanyAdminDetails
from catalog.company.models import Company, CompanyEventsQty, CompanyUser

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from hvad.utils import get_translation_aware_manager
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class CreateMessageView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsParticipant, IsOwner)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class EditMessageView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class DeleteMessageView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class MessageView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsMessageChatParticipant)
    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class ChatMessagesByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsParticipant,)
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs['chat']
        page = int(self.kwargs['page'])
        chat = Chat.objects.get(pk=chat_id)
        self.check_object_permissions(self.request, chat)

        if page == 0:
            objects = Message.objects.filter(chat=chat_id).order_by('-id')[:5]


        else:

            item_from = page * 5
            item_to = page * 5 + 5
            objects = Message.objects.filter(chat=chat_id).order_by('-id')[item_from:item_to]

        return objects


class ChatsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    serializer_class = ChatSerializer

    def get_serializer_context(self):
        company = self.request.GET.get('company', None)
        return {'request': self.request, 'company': company}

    def get_queryset(self):
        page = int(self.kwargs['page'])
        keyword = self.request.GET.get('keyword', None)
        unread = self.request.GET.get('unread', None)
        company = self.request.GET.get('company', None)
        sales = self.request.GET.get('sales', None)
        purchases = self.request.GET.get('purchases', None)
        jobs = self.request.GET.get('jobs', None)
        offering = self.request.GET.get('offering', None)
        requests = self.request.GET.get('requests', None)

        filter_list = Q()

        if company is not None:
            company_object = Company.objects.language().fallbacks('en').get(pk=company)
            self.check_object_permissions(self.request, company_object)

            filter_list = filter_list & Q(chat_users__company=company)
        else:
            filter_list = filter_list & Q(chat_users__user=self.request.user)

        if sales or purchases:
            filter_list = filter_list & Q(type=2)
        if jobs:
            filter_list = filter_list & Q(type=5)

        tr_manager = get_translation_aware_manager(Chat)
        chats = tr_manager.language('en').filter(filter_list).order_by('-update_date')

        if unread is not None:
            filter_list = filter_list & Q(chat_users__unread_messages__gt=0)

        if purchases is not None and sales is None:
            if company is not None:
                filter_list = filter_list & Q(chat_users__company=company, chat_users__customer=True)
            else:
                filter_list = filter_list & Q(chat_users__user=self.request.user, chat_users__customer=True)

        if sales is not None and purchases is None:

            if company is not None:
                filter_list = filter_list & Q(chat_users__company=company, chat_users__supplier=True)
            else:
                filter_list = filter_list & Q(chat_users__user=self.request.user, chat_users__supplier=True)

        if offering:
            filter_list = filter_list & Q(type=4)

        if requests:
            filter_list = filter_list & Q(type=6)

        chats = chats.language('en').filter(filter_list)

        if keyword is not None:

            participants_manager = get_translation_aware_manager(ChatParticipant)
            if company is not None:
                # participants = participants_manager.language().filter(chat__in=chats).exclude(company=company)
                participants = participants_manager.language().filter(
                    chat__in=chats)  # TODO exclude(company=company) doesn't work. I think that reason is that Company is translatable Model. If we don't solve this issue we will have a bug when a keyword is contained in the company name.

            else:
                participants = participants_manager.language().filter(chat__in=chats).exclude(user=self.request.user)

            new_filter_list = (Q(user__user_profile__first_name__icontains=keyword) |
                               Q(user__user_profile__last_name__icontains=keyword))

            filtered_participants = participants.language().filter(new_filter_list)
            if not filtered_participants:
                filtered_participants = participants.language('en').filter(new_filter_list)

            company_filtered_participants = participants.language().filter(company__name__icontains=keyword)
            if not company_filtered_participants:
                company_filtered_participants = participants.language('en').filter(company__name__icontains=keyword)

            filtered_participants = filtered_participants | company_filtered_participants

            chats = chats.language().filter(chat_users__in=filtered_participants)

        if page == 0:
            objects = chats.distinct()[:20]

        else:

            item_from = page * 20
            item_to = page * 20 + 20
            objects = chats.distinct()[item_from:item_to]

        return objects


class ChatsCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = self.request.GET.get('user', None)
        company = self.request.GET.get('company', None)

        keyword = self.request.GET.get('keyword', None)
        unread = self.request.GET.get('unread', None)
        sales = self.request.GET.get('sales', None)
        purchases = self.request.GET.get('purchases', None)

        filter_list = Q()

        if user is not None:
            filter_list = filter_list & Q(chat_users__user=user)
        if company is not None:
            filter_list = filter_list & Q(chat_users__company=company)

        chat_manager = get_translation_aware_manager(Chat)
        chats = chat_manager.language().filter(filter_list)
        count = chats.count()

        if unread is not None:
            filter_list = filter_list & Q(chat_users__unread_messages__gt=0)
            count = chats.language().filter(filter_list).count()

        if sales is not None:
            if user is not None:
                filter_list = filter_list & Q(request__supply_request__customer_user=user)
            if company is not None:
                filter_list = filter_list & Q(request__supply_request__customer_company=company)

            count = chats.language().filter(filter_list).count()

        if purchases is not None:
            if user is not None:
                filter_list = filter_list & Q(request__supply_request__supplier_user=user)
            if company is not None:
                filter_list = filter_list & Q(request__supply_request__supplier_company=company)

            count = chats.language().filter(filter_list).count()

        if keyword is not None:

            participants_manager = get_translation_aware_manager(ChatParticipant)

            if company is not None:

                participants = participants_manager.language().filter(
                    chat__in=chats)  # TODO exclude(company=company) doesn't work. I think that reason is that Company is translatable Model. If we don't solve this issue we will have a bug when a keyword is contained in the company name.

            else:
                participants = participants_manager.language().filter(chat__in=chats).exclude(user=user)

            new_filter_list = (Q(user__user_profile__first_name__icontains=keyword) |
                               Q(user__user_profile__last_name__icontains=keyword))

            filtered_participants = participants.language().filter(new_filter_list)

            if not filtered_participants:
                filtered_participants = participants.language('en').filter(new_filter_list)

            company_filtered_participants = participants.language().filter(company__name__icontains=keyword)
            if not company_filtered_participants:
                company_filtered_participants = participants.language('en').filter(company__name__icontains=keyword)

            filtered_participants = filtered_participants | company_filtered_participants

            count_users = chats.language().filter(chat_users__in=filtered_participants).count()

            filtered_participants = participants.language().filter(company__name__icontains=keyword)
            if not filtered_participants:
                filtered_participants = participants.language('en').filter(company__name__icontains=keyword)

            count_companies = chats.language().filter(chat_users__in=filtered_participants).count()

            count = count_users + count_companies

        data = {'count': count}

        return Response(data)


class MessagesCountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, chat):
        count = Message.objects.filter(chat=chat).count()

        data = {'count': count}

        return Response(data)


class UnreadMessagesCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_messages = self.request.user.user_profile.eventsqty.new_messages

        user_companies = CompanyUser.objects.filter(user=self.request.user)
        company_messages = 0
        for user_company in user_companies:
            company_messages = company_messages + user_company.company.eventsqty.new_messages

        total_messages = user_messages + company_messages

        data = {
            'count': total_messages,
            'user_count': user_messages,
            'company_count': total_messages}

        return Response(data)


class CompanyUnreadMessagesCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, company):
        obj = CompanyEventsQty.objects.get(company=company)
        new_messages = obj.new_messages

        data = {'company_count': new_messages}

        return Response(data)


class ChatIdForUserContactView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user, contact):
        chat_id = set_user_contact_chat(user, contact)

        data = {'chat': chat_id}

        return Response(data)


class SetReadMessagesForChatUserView(APIView):
    permission_classes = (IsAuthenticated, IsOwner)

    def put(self, request, chat):
        obj = ChatParticipant.objects.get(chat=chat, user=self.request.user)
        self.check_object_permissions(self.request, obj)
        old_unread_messages = obj.unread_messages
        obj.unread_messages = 0
        obj.save()

        obj.user.user_profile.eventsqty.update_events_qty('new_messages', -old_unread_messages)

        return Response({'res': True})


class SetReadMessagesForChatCompanyView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdminDetails)

    def put(self, request, chat, company):
        obj = ChatParticipant.objects.get(chat=chat, company=company)
        self.check_object_permissions(self.request, obj)
        old_unread_messages = obj.unread_messages
        obj.unread_messages = 0
        obj.save()
        obj.company.eventsqty.update_events_qty('new_messages', -old_unread_messages)

        return Response({'res': True})


class YourParticipantView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, chat):

        user_chat = ChatParticipant.objects.filter(chat=chat, company__isnull=True, user=self.request.user).exists()
        if not user_chat:
            try:
                company = ChatParticipant.objects.get(company__isnull=False, chat=chat,
                                                      company__in=self.request.user.managed_companies.values(
                                                          'company').all()).company
                object_id = company.id
            except ObjectDoesNotExist:
                object_id = self.request.user.id
        else:
            object_id = self.request.user.id

        data = {'user': user_chat, 'id': object_id}

        return Response(data)


def check_action(action):
    if action.code == 'welcome':
        chat = set_user_with_company_chat(action.user.id, settings.UAFINE_ID)
        try:
            lang = action.user.user_profile.interface_lang.code
            welcome_message = Translation.objects.language(lang).fallbacks('en').get(code='welcome')
            create_message(chat, 1, settings.UAFINE_USER_ID, settings.UAFINE_ID, welcome_message.text)
        except Translation.DoesNotExist:
            pass

    action.processed = True
    action.save()


class CheckUserActions(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        actions = UserAction.objects.filter(user=self.request.user, processed=False)
        for action in actions:
            check_action(action)
        return Response({'res': True})
