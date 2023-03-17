from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User,StudentDetails,Class
from rest_framework.exceptions import ValidationError

@receiver(post_save,sender=User)
def createStudentDetails(sender,instance,created,**kwargs):
    if not created:
        if hasattr(instance,"standard"):
            if instance.standard:
                student_detail = StudentDetails.objects.create(student_class=instance.standard,student=instance)
            else:
                raise ValidationError("Class is not created yet")