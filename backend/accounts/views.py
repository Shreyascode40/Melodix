from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User

from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer
from .models import Profile


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user, context={"request": request}).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    pass


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = request.data.get("refresh")
            if not token:
                return Response({"detail": "refresh required"}, status=400)
            t = RefreshToken(token)
            t.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "invalid token"}, status=400)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user, context={"request": request}).data)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request):
        profile = request.user.profile
        s = ProfileSerializer(
            profile, data=request.data, partial=True, context={"request": request}
        )
        s.is_valid(raise_exception=True)
        s.save()
        if "email" in request.data:
            request.user.email = request.data["email"]
            request.user.save()
        if "username" in request.data:
            new_u = request.data["username"]
            if User.objects.filter(username=new_u).exclude(pk=request.user.pk).exists():
                return Response({"username": ["Taken"]}, status=400)
            request.user.username = new_u
            request.user.save()
        return Response(ProfileSerializer(profile, context={"request": request}).data)

    def get(self, request):
        return Response(
            ProfileSerializer(request.user.profile, context={"request": request}).data
        )
