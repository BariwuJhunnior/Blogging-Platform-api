from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit or delete it.
    Read permissions are allowed to any request.
    """
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        # Allow GET, HEAD, or OPTIONS requests (Read-only access) for anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the author of the post
        # obj is the Post instance retrieved by the view
        # Note: 'view' parameter is not used in this implementation but is required by the method signature
        if obj is None:
            return False
        
        if not hasattr(obj, 'author'):
            return False
        
        # Check if user is authenticated and is the author
        if not hasattr(request, 'user') or request.user is None:
            return False
            
        return obj.author == request.user