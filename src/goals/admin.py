from django.contrib import admin
from goals.models import GoalCategory, Goal, GoalComment


@admin.register(GoalCategory)
class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated", "is_deleted")
    search_fields = ("title", "user")
    list_filter = ("is_deleted",)
    readonly_fields = ("created", "updated",)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "description", "status",)
    search_fields = ("title", "description")
    list_filter = ("status",)
    readonly_fields = ("created", "updated",)


@admin.register(GoalComment)
class GoalCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "text",)
    readonly_fields = ("created", "updated",)
