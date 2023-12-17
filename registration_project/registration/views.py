import secrets
import string

from django.contrib.auth import get_user_model
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer

User = get_user_model()


@swagger_auto_schema(
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['email', 'username', 'password','phone_number'],
    ),
    responses={
        201: 'Created',
        400: 'Bad Request',
    },
)
@authentication_classes([SessionAuthentication, BasicAuthentication])
@api_view(['POST'])
@permission_classes([AllowAny])
def registration_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.create(request.data)

        # Установите пароль для пользователя
        user.set_password(request.data['password'])
        user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Возвращаем успешный ответ после регистрации
        return Response({'message': 'Registration successful'})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['username', 'password'],
    ),
    responses={
        200: 'OK',
        401: 'Unauthorized',
    },
)
@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Устанавливаем токены в cookies
        response = Response({'message': 'Login successful'})
        response.set_cookie('access_token', access_token, httponly=True)
        response.set_cookie('refresh_token', str(refresh), httponly=True)

        return response
    else:
        return Response({'message': 'Login failed'}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    methods=['POST'],
    responses={
        200: 'OK',
    },
)
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Вызываем logout для аутентификации пользователя
    logout(request)

    # Удаляем куки из ответа
    response = Response({'message': 'Logout successful'})
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response


def generate_random_password():
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for i in range(6))

@swagger_auto_schema(
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email',
                                    description='Адрес электронной почты для сброса пароля'),
        },
        required=['email'],
    ),
    responses={
        # Добавьте описания ответов здесь
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь с такой почтой не найден'}, status=400)

    # Генерируем новый пароль
    new_password = generate_random_password()

    # Отправляем новый пароль на почту пользователя
    subject = 'Ваш новый пароль'
    message = f'Ваш новый пароль: {new_password}'
    from_email = 'noreply@example.com'
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

    # Хешируем новый пароль и сохраняем его в базе данных
    user.password = make_password(new_password)
    user.save()

    return JsonResponse({'message': 'Новый пароль отправлен на вашу почту'})