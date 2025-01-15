from django.shortcuts import render, get_object_or_404
from .models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
import logging
from django.http import JsonResponse, Http404
from django.views import View
# Create your views here.
logger = logging.getLogger(__name__)

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        # Получаем текущего аутентифицированного пользователя из запроса
        current_user = request.user
        
        # Создаем экземпляр сериализатора для текущего пользователя
        user_serializer = self.get_serializer(current_user)
        
        # Возвращаем ответ с сериализованными данными пользователя
        return Response(user_serializer.data)
    
    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        # Получаем текущего аутентифицированного пользователя из запроса
        current_user = request.user
        
        # Создаем экземпляр сериализатора для текущего пользователя с данными из запроса
        # Параметр partial=True позволяет обновлять только те поля, которые были переданы
        user_serializer = self.get_serializer(current_user, data=request.data, partial=True)
        
        # Проверяем, валидны ли данные, переданные в сериализатор
        if user_serializer.is_valid():
            # Если данные валидны, сохраняем обновленные данные пользователя
            user_serializer.save()
            # Возвращаем ответ с обновленными данными пользователя
            return Response(user_serializer.data)
        
        # Если данные не валидны, возвращаем ошибки и статус 400 (Bad Request)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['options'])
    def availableMethods(self, request):
        # Возвращаем доступные методы для данного ресурса
        return Response({
            'methods': ['PATCH', 'GET', 'OPTIONS']
        })
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def registerUser(self, request):
        # Создаем сериализатор с данными из запроса
        serializer = UserRegSerializer(data=request.data)
        if serializer.is_valid():
            # Сохраняем нового пользователя
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Возвращаем ошибки валидации, если данные не валидны
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatViewSet(viewsets.ModelViewSet):
    # Определяем набор данных, который будет использоваться в этом представлении
    queryset = Chat.objects.all()
    
    # Указываем сериализатор, который будет использоваться для преобразования данных
    serializer_class = ChatSerializer
    
    # Указываем классы разрешений, которые определяют доступ к этому представлению
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Метод, который вызывается при создании нового объекта
        # Здесь можно добавить дополнительную логику перед сохранением (если понадобиться в будущем при масштабировании)
        serializer.save()


class MessageViewSet(viewsets.ModelViewSet):
    # Определяем набор данных для сообщений
    queryset = Message.objects.all()
    
    # Указываем сериализатор, который будет использоваться для преобразования данных
    serializer_class = MessageSerializer
    
    # Указываем классы разрешений, которые определяют доступ к этому представлению
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Устанавливаем текущего пользователя как отправителя сообщения
        serializer.save(user=self.request.user)


class ChatMessagesView(View):
    def get(self, request, chat_id):
        try:
            # Проверяем существование чата по его идентификатору
            current_chat = get_object_or_404(Chat, id=chat_id)
            
            # Получаем все сообщения, связанные с этим чатом
            messages = Message.objects.filter(chat=current_chat)
            
            # Сериализуем сообщения для отправки в ответе
            serializer = MessageSerializer(messages, many=True)
            
            # Возвращаем сериализованные данные в формате JSON
            return JsonResponse(serializer.data, safe=False)
        
        except Http404:
            # Обрабатываем ошибку 404, если чат не найден
            return JsonResponse({'error': 'Chat not found'}, status=404)
        

def mainPage(request):
    # Обрабатываем GET-запрос и возвращаем главную страницу
    # 'index.html' - это шаблон, который будет отрендерен
    return render(request, 'index.html')


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]