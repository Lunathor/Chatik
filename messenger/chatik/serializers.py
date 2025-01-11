from rest_framework import serializers
from .models import User, Chat, Message

class UserSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(allow_null=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id',
            'login',
            'firstName',
            'lastName',
            'photo'
        ]
     
        
class UserRegSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'login',
            'password',
            'firstName',
            'lastName',
            'photo'
        ]
    
    def registration(self, validated_data):
        required_fields = ['login', 'firstName', 'lastName', 'password']
        for field in required_fields:
            if field not in validated_data:
                raise ValueError(f"Поле {field} обязательно для заполнения.")
            
        user = User(
            login=validated_data['login'],
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            photo=validated_data.get('photo')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    
class ChatSerializer(serializers.ModelSerializer):
    chatMembers = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Chat
        fields = [
            'id',
            'title',
            'members'
        ]
        

class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id',
            'user',
            'chat',
            'text',
            'sendtime'
        ]
    
    def validate(self, data):
        if not data.get(self.fields['chat'].source):
            raise serializers.ValidationError("Необходим идентификатор чата.")
        if not data.get(self.fields['content'].source):
            raise serializers.ValidationError("Содержимое сообщения обязательно.")
        return data