from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserView, ChatViewSet, MessageViewSet, CustomTokenObtainPairView, mainPage, ChatMessagesView

router = DefaultRouter()
router.register(r'users', UserView)
router.register(r'chats', ChatViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', mainPage, name='mainpage'),  # Главная страница
    path('api/', include(router.urls)),  # Маршруты API
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/chats/<int:chat_id>/messages/', ChatMessagesView.as_view(), name='chat-messages'),
]