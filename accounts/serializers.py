from rest_framework import serializers, exceptions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.utils import timezone
from accounts.models import *
from django.utils.timezone import now


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['email'],
            email=validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.is_staff = True
        user.save()
        token = self.get_token(user)
        ctx = {
            'user': user.pk,
            'token': token,
        }
        return ctx

    def get_token(self, obj):
        token = Token.objects.create(user=obj)
        return token.key


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=35)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        user = authenticate(
            username=data['email'], password=data['password'])
        if not user:
            raise exceptions.AuthenticationFailed()
        elif not user.is_active:
            raise exceptions.PermissionDenied()
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    def get_profile(self,obj):
        pro = Profile.objects.filter(created_by=obj.pk).last()
        serializers = UserProfileSerializer(pro)
        return serializers.data

    class Meta:
        model = User
        fields = ('pk', 'username', 'first_name', 'last_name', 'email', 'last_login', 'profile')

class UserLoginReplySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Token
        fields = ('key', 'user')


class UserDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('created_on', 'updated_on', 'updated_by', 'created_by')

class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        exclude = ('created_on', 'updated_on', 'updated_by', 'created_by')

class InvitedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvitedUser
        fields = ('email',)

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

class InventoryListSerializer(serializers.ModelSerializer):
    supplier = SupplierListSerializer()
    class Meta:
        model = Inventory
        exclude = ('updated_on', 'updated_by')