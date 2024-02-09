from rest_framework import permissions
from .models import ChatParticipant

class IsOwner(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        # if request.method in permissions.SAFE_METHODS:
        #     return True

        res = obj.user == request.user




        return res

class IsParticipant(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):



        res = ChatParticipant.objects.filter(chat=obj.id, user=request.user).exists()


        if not res:
            res = ChatParticipant.objects.filter(chat=obj.id, company__users__user=request.user).exists()



        return res


class IsMessageChatParticipant(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        res = ChatParticipant.objects.filter(chat=obj.chat, user=request.user).exists()

        if not res:
            res = ChatParticipant.objects.filter(chat=obj.chat, company__users__user=request.user).exists()

        return res

