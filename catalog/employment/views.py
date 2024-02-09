from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserProfileEmploymentSerializer
from rest_framework import generics
from .models import UserProfileEmployment

from .permissions import IsOwnerDetails


class UserEmploymentsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserProfileEmploymentSerializer

    def get_queryset(self):
        profile = self.kwargs['profile']
        language = self.kwargs['language']
        education = self.kwargs['education'] == 'true'

        return UserProfileEmployment.objects.language(language).fallbacks('en').filter(profile=profile,
                                                                                       education=education).order_by(
            '-present_time', '-end_date', '-start_date')


class CreateUserEmploymentView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)
    queryset = UserProfileEmployment.objects.language().all()
    serializer_class = UserProfileEmploymentSerializer


class DeleteUserEmploymentView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)
    queryset = UserProfileEmployment.objects.language().fallbacks('en').all()
    serializer_class = UserProfileEmploymentSerializer


class UpdateUserEmploymentView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)
    queryset = UserProfileEmployment.objects.language().fallbacks('en').all()
    serializer_class = UserProfileEmploymentSerializer


class UpdateUserEmploymentInLanguageView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)

    serializer_class = UserProfileEmploymentSerializer

    def get_object(self):
        language = self.kwargs['language']
        pk = self.kwargs['pk']

        obj = UserProfileEmployment.objects.language(language).fallbacks('en').get(pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj


class UserEmploymentDetailsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)
    queryset = UserProfileEmployment.objects.language().fallbacks('en').all()
    serializer_class = UserProfileEmploymentSerializer
