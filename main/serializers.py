from rest_framework import serializers, exceptions
from main.models import User


class ChangeEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', )


class DeleteMyAccountSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True
    )

    def validate(self, attrs):
        if not attrs.get('username'):
            raise exceptions.ValidationError({'username': 'Please input username.'})

        if not self.instance:
            raise exceptions.ValidationError({'user': 'Not logged in.'})

        if self.instance.username != attrs.get('username'):
            raise exceptions.ValidationError({'username': 'Wrong username.'})
