from rest_framework import serializers
from goals.models import GoalCategory, GoalComment, Goal
from core.serializers import ProfileSerializer


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """Создание категории"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"


class GoalCategorySerializer(serializers.ModelSerializer):
    """Просмотр и изменение категории"""
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user")


class GoalCreateSerializer(serializers.ModelSerializer):
    """Создание цели"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(queryset=GoalCategory.objects.filter(is_deleted=False))

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

        def validate_category(self, value):
            if value.user != self.context["request"].user:
                raise serializers.ValidationError("not owner of category")
            return value


class GoalSerializer(serializers.ModelSerializer):
    """Просмотр и изменение цели"""
    category = serializers.PrimaryKeyRelatedField(queryset=GoalCategory.objects.filter(is_deleted=False))

    class Meta:
        model = Goal
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"

        def validate_category(self, value):
            if value.user != self.context["request"].user:
                raise serializers.ValidationError("not owner of category")
            return value


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """Создание комментария"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user")
        fields = "__all__"


class GoalCommentSerializer(serializers.ModelSerializer):
    """Просмотр и изменение комментария"""
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        read_only_fields = ("id", "created", "updated", "user", "goal")
        fields = "__all__"
