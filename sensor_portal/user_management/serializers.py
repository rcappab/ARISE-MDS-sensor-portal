from data_models.models import Deployment, Device, Project
from data_models.serializers import (DeploymentSerializer, DeviceSerializer,
                                     ProjectSerializer)
from django.contrib.auth.password_validation import (
    CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator,
    UserAttributeSimilarityValidator)
from drf_recaptcha.fields import ReCaptchaV3Field
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        # validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    recaptcha = ReCaptchaV3Field(
        action="register",
        required_score=0.8,
    )

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'],
                                        validated_data['password'],
                                        first_name=validated_data['first_name'],
                                        last_name=validated_data['last_name'],
                                        bio=validated_data['bio'],
                                        organisation=validated_data['organisation'])
        return user

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords don't match.")

        data = super().validate(data)
        return data

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'confirm_password', 'email',
                  'first_name', 'last_name', 'bio', 'organisation', 'recaptcha')


class UserProfileSerializer(serializers.ModelSerializer):

    owned_projects = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='project_ID')
    managed_projects = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='project_ID')
    owned_devices = DeviceSerializer(
        many=True, read_only=True)
    managed_devices = DeviceSerializer(
        many=True, read_only=True)
    owned_deployments = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='deployment_device_ID')
    managed_deployments = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='deployment_device_ID')

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name',
                  'bio', 'organisation'
                  'owned_projects', 'managed_projects',
                  'owned_devices', 'managed_devices',
                  'owned_deployments', 'managed_deployments'
                  )


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    recaptcha = ReCaptchaV3Field(
        action="login",
        required_score=0.6,
    )

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token
