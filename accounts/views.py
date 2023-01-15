from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import permissions, status
from rest_framework.views import APIView
from accounts.serializers import *
from rest_framework.response import Response
from gemstone_erp import settings
from django.core.mail import send_mail
import threading
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

# Create your views here.

class RegistrationAPI(GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        try:
            invite_data = InvitedUser.objects.filter(email = request.data['email']).last()
            if invite_data:
                payload = request.data.copy()
                payload['username'] = request.data['email']
                serializer = self.get_serializer(data=payload)
                if serializer.is_valid(raise_exception=True):
                    user = serializer.save()
                    payload['created_by'] = user['user']
                    payload['updated_by'] = user['user']
                    serializer = ProfileSerializer(data=payload)
                    if serializer.is_valid():
                        serializer.save()
                        return Response({'status': True, 'massage': 'Your registration successfully.'}, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors)
            return Response({'status': False, 'massage':'You are not get invite this email'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_data = {
                "status": "failed",
                "message": str(e)
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPI(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            token, created = Token.objects.get_or_create(
                user=serializer.validated_data['user'])
            request = {
                'user': serializer.validated_data['user']
            }
            response_serializer = UserLoginReplySerializer(token, context={'request': request})
            return Response(response_serializer.data)
        except Exception as e:
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InvitedUserViewSet(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = InvitedUserSerializer

    def post(self, request, *args, **kwargs):
        try:
            if self.request.user.is_superuser == True:
                serializer = self.get_serializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save(created_by=self.request.user)
                    email = request.data['email']
                    thrd=threading.Thread(target=email_sending,args=(email,))
                    thrd.start()
                    return Response( {'status': True, 'data': 'Invite send successfully.'}, status=status.HTTP_200_OK)
                return Response(serializer.errors)
            return Response({'status': False, 'message': 'Invlied key.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_data = {
                "status": "failed",
                "message": str(e)
            }
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)

def email_sending(email):
    try:
        subject = 'Gemstone is inviting you to Register'
        message = f'Please register with below register link \n http://127.0.0.1:8000/api/v1/account/register'
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email,]
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        print('send email.')


class PasswordChangeAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        password = request.data.get("password")
        confirmPassword = request.data.get("confirmPassword")

        if password != confirmPassword:
            return Response({'error': 'Password does not match'},
                            status=500)

        user = User.objects.get(pk=request.user.pk)
        user.set_password(password)
        user.save()
        return Response({'ok': 'Password changed successfully! '},
                        status=200)


class InventoryViewSet(viewsets.ModelViewSet):
    serializer_classes = {
        'create': InventorySerializer,
        'list': InventoryListSerializer
    }
    create_profile_serializer = InventorySerializer
    default_serializer_class = InventorySerializer
    queryset = Inventory.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def list(self, request, *args, **kwargs):
        queryset = Inventory.objects.all().order_by('-id')
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if self.request.user.is_superuser == True:
            payload = request.data.copy()
            serializer = self.get_serializer_class()(data=payload)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
            return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response({'status': False, 'message': 'You have no permission for create inventory.'}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        query = get_object_or_404(Inventory, id=kwargs['pk'])
        return Response(self.get_serializer_class()(query, many=False).data)

    def update(self, request, *args, **kwargs):
        if self.request.user.is_superuser == True:
            payload = request.data.copy()
            query = get_object_or_404(Inventory, id=kwargs['pk'])
            payload['updated_by'] = request.user.id
            serializer = self.get_serializer_class()(query, payload, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'status': False, 'message': 'You have no permission for create inventory.'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if self.request.user.is_superuser == True:
            query = get_object_or_404(Inventory,  id=kwargs['pk'])
            query.delete()
            return Response({'status': True, 'message': 'Inventory delete successfully,'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'status': False, 'message': 'You have no permission for create inventory.'}, status=status.HTTP_400_BAD_REQUEST)