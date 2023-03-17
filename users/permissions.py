from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q



class IsStaff(BasePermission):
    

    def has_permission(self,request,view):
        print(request.user.user_type)
        try:
            if request.user.user_type ==1:
                return True
            else:
                return False
        except Exception as e:
            return False
