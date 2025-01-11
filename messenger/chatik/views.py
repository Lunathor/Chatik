from django.shortcuts import render
from models import *
from .serializers import *
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
import logging
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