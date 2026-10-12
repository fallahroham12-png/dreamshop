from rest_framework import generics, views, status, viewsets, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .models import Address
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer, AddressSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/  {phone, password, first_name?, last_name?}"""
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserProfileSerializer(user).data}, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    """POST /api/auth/login/  {phone, password} → توکن دسترسی"""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserProfileSerializer(user).data})


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/profile/ — نیازمند هدر Authorization: Token <key>"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AddressViewSet(viewsets.ModelViewSet):
    """CRUD کامل روی آدرس‌های حساب کاربری — بخش ۱۳ سند."""
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
