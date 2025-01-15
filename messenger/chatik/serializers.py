from rest_framework import serializers
from .models import User, Chat, Message


class UserSerializer(serializers.ModelSerializer):
    # Поле для загрузки изображения профиля пользователя
    photo = serializers.ImageField(allow_null=True, required=False)
    
    class Meta:
        # Указываем модель, с которой будет работать сериализатор
        model = User
        
        # Указываем поля, которые будут включены в сериализацию/десериализацию
        fields = [
            'id',  # Уникальный идентификатор пользователя
            'username',  # Логин пользователя
            'first_name',  # Имя пользователя
            'last_name',  # Фамилия пользователя
            'photo'  # Фото пользователя (опционально)
        ]


class UserRegSerializer(serializers.ModelSerializer):
    # Поле для пароля, доступное только для записи (не возвращается в ответах)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        # Указываем модель, с которой будет работать сериализатор
        model = User
        
        # Указываем поля, которые будут включены в сериализацию/десериализацию
        fields = [
            'username',  # Логин пользователя
            'password',  # Пароль пользователя (только для записи)
            'first_name',  # Имя пользователя
            'last_name',  # Фамилия пользователя
            'photo'  # Фото пользователя (опционально)
        ]
    
    def registration(self, validated_data):
        # Список обязательных полей для регистрации
        required_fields = ['username', 'firstName', 'lastName', 'password']
        
        # Проверяем, что все обязательные поля присутствуют в данных
        for field in required_fields:
            if field not in validated_data:
                raise ValueError(f"Поле {field} обязательно для заполнения.")
        
        # Создаем нового пользователя с переданными данными
        user = User(
            username=validated_data['username'],
            firstName=validated_data['firstName'],
            lastName=validated_data['lastName'],
            photo=validated_data.get('photo')  # Получаем фото, если оно есть
        )
        
        # Устанавливаем хэшированный пароль для пользователя
        user.set_password(validated_data['password'])
        
        # Сохраняем нового пользователя в базе данных
        user.save()
        
        # Возвращаем созданного пользователя
        return user


class ChatSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True)  # Add title field
    
    # Поле для сериализации участников чата (пользователей)
    chatMembers = UserSerializer(many=True, read_only=True)
    
    class Meta:
        # Указываем модель, с которой будет работать сериализатор
        model = Chat
        
        # Указываем поля, которые будут включены в сериализацию/десериализацию
        fields = [
            'id',  # Уникальный идентификатор чата
            'title',  # Заголовок чата
            'chatMembers'  # Участники чата (сериализуются через UserSerializer)
        ]


class MessageSerializer(serializers.ModelSerializer):
    # Поле для сериализации пользователя, отправившего сообщение
    user = UserSerializer(read_only=True)
    
    class Meta:
        # Указываем модель, с которой будет работать сериализатор
        model = Message
        
        # Указываем поля, которые будут включены в сериализацию/десериализацию
        fields = [
            'id',  # Уникальный идентификатор сообщения
            'user',  # Пользователь, отправивший сообщение
            'chat',  # Чат, в котором было отправлено сообщение
            'text',  # Текст сообщения
            'sendtime'  # Время отправки сообщения
        ]
    
    def validate(self, data):
        # Проверяем, что идентификатор чата присутствует в данных
        if not data.get(self.fields['chat'].source):
            raise serializers.ValidationError("Необходим идентификатор чата.")
        
        # Проверяем, что содержимое сообщения присутствует в данных
        if not data.get(self.fields['content'].source):
            raise serializers.ValidationError("Содержимое сообщения обязательно.")
        
        # Если все проверки пройдены, возвращаем данные
        return data