from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password','role', 'phone_number')
    
    
    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            email = validated_data['email'],
            role = validated_data.get('role','CUSTOMER'),
            # phone_number = validated_data.get('phone_number', '')
            phone_number =validated_data.get('phone_number')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
          