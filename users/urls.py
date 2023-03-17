from django.urls import path
from . import views
from .views import classViewset,subjectViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'class', classViewset, basename='class')
router.register(r'subject', subjectViewset, basename='subject')
# router.register(r'result',resultViewset, basename='result')

urlpatterns = [
    path('',views.home,name='home'),
    path('student/register',views.registerStudent,name='student_register'),
    path('student/',views.studentListView,name='students_list'),
    path('student/<str:id>/',views.studentDetailView,name='student_detail'),
    path('student/dashboard/<str:id>/',views.dashboardStudent,name='student_dashboard'),
    path('staff/register',views.registerStaff,name='staff_register'),
    path('staff/',views.staffListView,name='students_list'),
    path('staff/<str:id>/',views.staffDetailView,name='staff_detail'),
    path('staff/dashboard/<str:id>/',views.dashboardStaff,name='staff_dashboard'),
    path('staff/addresult',views.createResultView,name="add_result"),
    path('staff/addresult/<str:id>/',views.updateResultView,name="update_result"),

]

urlpatterns += router.urls