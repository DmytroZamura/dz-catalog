from .models import Chat, ChatParticipant, Message
from rest_framework import serializers
from catalog.user_profile.serializers import UserWithProfileSerializer
from catalog.company.serializers import CompanyShortSerializer



class ChatParticipantSerializer(serializers.ModelSerializer):
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)
    company_details = CompanyShortSerializer(source='company', required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source='company', required=False, read_only=True, language='en')

    class Meta:
        model = ChatParticipant
        fields = (
        'id', 'chat', 'user', 'user_details', 'company_details', 'company_default_details', 'company', 'customer',
        'supplier',
        'unread_messages', 'update_date')

        read_only_fields = ('update_date',)


class ChatSerializer(serializers.ModelSerializer):
    participants = ChatParticipantSerializer(source='chat_users', many=True, read_only=True)
    unread_messages = serializers.SerializerMethodField()

    # request = SupplyRequestChatSerializer( read_only=True, required=False)

    def get_unread_messages(self, obj):
        if self.context:
            unread_messages = 0
            try:
                if self.context['company']:
                    try:
                        participant = ChatParticipant.objects.get(company=self.context['company'], chat=obj.id)
                        unread_messages = participant.unread_messages
                    except ChatParticipant.DoesNotExist:
                        pass
                else:
                    try:
                        participant = ChatParticipant.objects.get(user=self.context['request'].user, chat=obj.id)
                        unread_messages = participant.unread_messages
                    except ChatParticipant.DoesNotExist:
                        pass
            except:
                pass
            return unread_messages
        else:
            return None

    class Meta:
        model = Chat

        fields = ('id', 'type', 'participants', 'unread_messages', 'update_date')

        read_only_fields = ('update_date',)



class ChatSmallSerializer(serializers.ModelSerializer):


    class Meta:
        model = Chat

        fields = ('id', 'type', 'update_date')

        read_only_fields = ('update_date',)


class MessageSerializer(serializers.ModelSerializer):
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)

    company_details = CompanyShortSerializer(source='company', required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source='company', required=False, read_only=True, language='en')


    class Meta:
        model = Message
        fields = ('id', 'chat', 'user', 'user_details', 'company', 'company_details', 'company_default_details', 'type',
                  'message', 'update_date')

        read_only_fields = ('update_date',)
