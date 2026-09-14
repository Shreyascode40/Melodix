from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "username",
            "email",
            "display_name",
            "avatar",
            "avatar_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.avatar.url)
                if request
                else obj.avatar.url
            )
        return None

    def validate_avatar(self, v):
        if v and v.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Max 2MB")
        if v and not v.content_type.startswith("image/"):
            raise serializers.ValidationError("Image only")
        return v


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(min_length=3, max_length=30)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True
    )

    def validate_username(self, v):
        if User.objects.filter(username=v).exists():
            raise serializers.ValidationError("Taken")
        return v

    def validate_email(self, v):
        if User.objects.filter(email=v).exists():
            raise serializers.ValidationError("Taken")
        return v

    def validate_password(self, v):
        validate_password(v)
        return v

    def create(self, vd):
        user = User.objects.create_user(
            username=vd["username"], email=vd["email"], password=vd["password"]
        )
        profile = user.profile
        if vd.get("display_name"):
            profile.display_name = vd["display_name"]
            profile.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="profile.display_name", read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "display_name", "avatar_url"]

    def get_avatar_url(self, obj):
        if hasattr(obj, "profile") and obj.profile.avatar:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.profile.avatar.url)
                if request
                else obj.profile.avatar.url
            )
        return None
