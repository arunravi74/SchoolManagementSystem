from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import UserType

# Create your models here.
gender_options = (
    ('M', "Male"),
    ('F', "Female"),
  )

class User(AbstractUser):
    user_type = models.IntegerField(
        choices=UserType.choices(), default=UserType.STUDENT)
    address = models.TextField()
    gender = models.CharField(choices=gender_options,max_length=1)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.username +" "+UserType(self.user_type).name.title()

class Class(models.Model):
    standard =  models.CharField(max_length=12,verbose_name='class',unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'class'

    def __str__(self):
        return self.standard

class Subject(models.Model):
    subject_name = models.CharField(max_length=256)
    class_id = models.ForeignKey('Class',on_delete=models.CASCADE)
    staff_id = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subject'
        unique_together = ('subject_name','class_id')

    def __str__(self):
        return self.subject_name

class StudentDetails(models.Model):
    student_class = models.ForeignKey(Class,on_delete=models.CASCADE)
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    class Meta:
        db_table = 'student_details'

class Result(models.Model):
    student = models.ForeignKey(User,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    current_class = models.ForeignKey(Class,on_delete=models.CASCADE)
    exam_score = models.IntegerField(default=0)

    class Meta:
        ordering = ["subject"]
        db_table = "result"
        unique_together = ('student','subject')

    def __str__(self):
        return f"{self.student} {self.subject}"

    def total_score(self):
        return self.exam_score