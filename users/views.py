from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (UserSerializer,StudentSerializer,
                          ClassSerializer,SubjectSerializer,StaffSerializer,
                          ResultSerializer
                          )
from .models import  User,Class,Subject,Result,StudentDetails
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django.db import connection
from .permissions import IsStaff
import json
from django.http import JsonResponse

@api_view(['GET'])
@permission_classes([])
def home(request):
    list_routes = """admin/[name='home']
student/register [name='student_register']
student/ [name='students_list']
student/<str:id>/ [name='student_detail']
student/dashboard/<str:id>/ [name='student_dashboard']
staff/register [name='staff_register']
staff/ [name='students_list']
staff/<str:id>/ [name='staff_detail']
staff/dashboard/<str:id>/ [name='staff_dashboard']
staff/addresult [name='add_result']
staff/addresult/<str:id>/ [name='update_result']
^class/$ [name='class-list']
^class\.(?P<format>[a-z0-9]+)/?$ [name='class-list']
^class/(?P<pk>[^/.]+)/$ [name='class-detail']
^class/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ [name='class-detail']
^subject/$ [name='subject-list']
^subject\.(?P<format>[a-z0-9]+)/?$ [name='subject-list']
^subject/(?P<pk>[^/.]+)/$ [name='subject-detail']
^subject/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ [name='subject-detail']"""

    list_routes = list_routes.split("\n")
    return JsonResponse(list_routes,safe=False)

@api_view(['POST'])
@permission_classes([IsStaff])
def registerStudent(request):
    if request.data.get('student_class'):
        standard = Class.objects.filter(id=request.data['student_class']).first()
        if standard:
            serializer = StudentSerializer(data=request.data,context = {"standard":standard})
            if serializer.is_valid(raise_exception=True):
                serializer.validated_data['user_type'] = 2 
                serializer.save()
                return Response(serializer.data)
        else:
            raise ValidationError("student_class is not created yet")
    else:
        raise ValidationError("student_class shouldn't be empty")

# @api_view(['PUT'])
# def updateStudent(request,id=None):
#     standard = None
#     if id:
#         try:
#             instance = User.objects.get(id=id)
#             if instance and instance.user_type != 2:
#                 raise ValidationError("User is not a Student")
#         except Exception as e:
#             return Response(f"{e}")
#     if request.data.get('student_class'):
#         standard = Class.objects.filter(id=request.data['student_class']).first()
#         if not standard:
#                 raise ValidationError("student_class is not created yet")
    
#     serializer = StudentSerializer(data=request.data,context = {"standard":standard},partial=True)
#     if serializer.is_valid(raise_exception=True):
#         serializer.save()
#         return Response(serializer.data)   

@api_view(['POST'])
@permission_classes([])
def registerStaff(request):
    serializer = StaffSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.validated_data['user_type'] = 1
        serializer.save()
        return Response(serializer.data)
    
class classViewset(viewsets.ModelViewSet):
    # A simple Viewset for view and edit classes in school
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsStaff,]

class subjectViewset(viewsets.ModelViewSet):
    # A simple Viewset for view and edit subjects
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsStaff,]

# class resultViewset(viewsets.ModelViewSet):
#     # A simple Viewset for view and edit subjects
#     queryset = Result.objects.all()
#     serializer_class = ResultSerializer

@api_view(['POST'])
def createResultView(request):
    
    if request.data.get("student"):
        try:
            student = User.objects.get(id = request.data.get("student"))
            if student.user_type == 2:
                student_details = StudentDetails.objects.get(student = student).student_class
                print(student_details)
                subject = Subject.objects.get(id = request.data.get('subject')).class_id
                print(subject)
                if subject==student_details:
                    serializer = ResultSerializer(data = request.data)
                    if serializer.is_valid(raise_exception=True):
                        serializer.validated_data['current_class'] = subject
                        serializer.save()
                        return Response(serializer.data)
                else:
                    return Response({'subject':"Subject is not for class {}".format(student_details)})
            else:
                return Response({'student':"{} is not a Student".format(student.first_name)})
        except Exception as e:
            return Response({"student":f"{e}"})

@api_view(['PUT'])
def updateResultView(request,id=None):
    try:
        result = Result.objects.get(id = id)
        serializer = ResultSerializer(result,data = request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    except Exception as e:
        return Response(f"result is Not Found {e}")

@api_view(['GET'])
def studentListView(request):
    instance = User.objects.filter(user_type=2)
    serializer = UserSerializer(instance,many=True)
    return Response(serializer.data)
@api_view(['GET'])
def staffListView(request):
    instance = User.objects.filter(user_type=1)
    serializer = UserSerializer(instance,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def studentDetailView(request,id=None):
    try:
        instance = User.objects.get(Q(user_type=2 )&Q(id=id))
        serializer = UserSerializer(instance)
        return Response(serializer.data)  
    except Exception as e:
        return Response(f"{e}")

@api_view(['GET'])
def staffDetailView(request,id=None):
    try:
        instance = User.objects.get(Q(user_type=1 )&Q(id=id))
        serializer = UserSerializer(instance)
        return Response(serializer.data)  
    except Exception as e:
        return Response(f"{e}")

@api_view(['GET'])    
def dashboardStudent(request,id = None):
    with connection.cursor() as c:
        c.execute("""SELECT u.first_name,u.email,(CASE 
        WHEN u.gender='M' THEN 'Male' ELSE 'Female'END)as gender,u.address FROM users_user as u
        WHERE u.id = %s AND u.user_type=2""",(id,))
        user = c.fetchone()
        if user:
            columns = [col[0] for col in c.description]
            user = dict(zip(columns, user))
            c.execute(
                """ SELECT r.exam_score,r.current_class_id,
                    r.subject_id FROM users_user as u
                    LEFT JOIN result as r
                    ON u.id = r.student_id
                    WHERE u.id = %s AND u.user_type=2""",(id,))
            student = c.fetchall()
            students = []
            columns = [col[0] for col in c.description]
            for i in range(len(student)):
                out = dict(zip(columns, student[i]))
                students.append(out)
            user["result"] = students
            return Response(user)
        else:
            return Response("User Not Found")

@api_view(['GET'])    
def dashboardStaff(request,id = None):
    with connection.cursor() as c:
        c.execute("""SELECT u.first_name,u.email,(CASE 
        WHEN u.gender='M' THEN 'Male' ELSE 'Female'END)as gender,u.address FROM users_user as u
        WHERE u.id = %s AND u.user_type=1""",(id,))
        user = c.fetchone()
        if user:
            columns = [col[0] for col in c.description]
            user = dict(zip(columns, user))
            c.execute("""SELECT s.subject_name,
            (SELECT standard FROM class WHERE id=s.class_id_id)as class FROM users_user u
            LEFT JOIN subject s
            ON u.id=staff_id_id
            WHERE u.id = %s""",(id,))
            subject = c.fetchall()
            subjects = []
            columns = [col[0] for col in c.description]
            for i in range(len(subject)):
                out = dict(zip(columns, subject[i]))
                subjects.append(out)
            user["subjects"] = subjects
            return Response(user)
        else:
            return Response("User Not Found")