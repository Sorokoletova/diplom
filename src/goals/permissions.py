from rest_framework import permissions
from goals.models import GoalCategory, GoalComment, Goal, Board, BoardParticipant


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_id == request.user.id


class BoardPermissions(permissions.IsAuthenticated):

    def has_object_permission(self, request, view, obj: Board):
        filters = {'user': request.user, 'board': obj}
        if request.method not in permissions.SAFE_METHODS:
            filters['role'] = BoardParticipant.Role.owner
        return BoardParticipant.objects.filter(**filters).exists()


class GoalCategoryPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: GoalCategory):
        filters = {'user': request.user, 'board': obj.board}
        if request.method not in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class GoalPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: Goal):
        filters = {'user': request.user, 'board': obj.category.board}
        if request.method not in permissions.SAFE_METHODS:
            filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        return BoardParticipant.objects.filter(**filters).exists()


class GoalCommentPermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj: GoalComment):
        return any((
            request.method in permissions.SAFE_METHODS,
            obj.user_id == request.user.id,
        ))
        # filters = {'user': request.user, 'board': obj.goal.category.board}
        # if request.method not in permissions.SAFE_METHODS:
        #     filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        # return BoardParticipant.objects.filter(**filters).exists()