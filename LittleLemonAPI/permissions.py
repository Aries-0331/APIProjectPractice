from rest_framework.permissions import IsAuthenticated

class IsManagerUser(IsAuthenticated):
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Manager').exists())
