from rest_framework import serializers
from .models import User,Class,Subject,Result,gender_options
from rest_framework.exceptions import ValidationError
from .utils import UserType



class UserSerializer(serializers.ModelSerializer):
    # user_type = serializers.CharField(max_length=50)
    class Meta:
        model = User
        fields = ['id','username','first_name','email','gender','address','user_type']
        # exclude = ['password']
        
    def to_representation(self, instance):
        res = super(UserSerializer,self).to_representation(instance)
        res['gender'] = gender_options[0][1] if res['gender'] == "M" else gender_options[1][1]
        res['user_type'] = UserType(res['user_type']).name.title()
        return res  
    

class StudentSerializer(serializers.ModelSerializer):   
    class Meta:
        model = User
        fields = ['username','first_name','email','gender','address','password','user_type']
        extra_kwargs = {'password': {'write_only': True},'user_type':{'read_only':True}}

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.standard = self.context['standard']
        user.save()
        return user
    
    # def update(self, instance, validated_data):
    #     validated_data.pop('password', None)        
    #     instance.username = validated_data.get('username',instance.username)
    #     instance.first_name = validated_data.get('first_name',instance.first_name)
    #     instance.email = validated_data.get('email',instance.email)
    #     instance.gender = validated_data.get('gender',instance.gender)
    #     instance.address = validated_data.get('address',instance.address)
    #     return super().update(instance, validated_data)
    
class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','first_name','email','gender','address','password','user_type']
        extra_kwargs = {'password': {'write_only': True},'user_type':{'read_only':True}}

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

    def create(self, validated_data):
        if validated_data['staff_id'].user_type == 2:
            raise ValidationError("Please Enter Staff User in Staff_id Field")
        return super().create(validated_data)
    
    def to_representation(self, instance):
        
        res = super(SubjectSerializer,self).to_representation(instance)
        res['class_id'] = instance.class_id.standard
        res['staff_id'] = instance.staff_id.first_name
        return res 
    
class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = "__all__"
        extra_kwargs = {'current_class':{'read_only':True}}

    def update(self, instance, validated_data):
        validated_data.pop('student', None)
        instance.exam_score = validated_data.get('exam_score',instance.exam_score)
        instance.subject = validated_data.get('subject',instance.subject)
        return super().update(instance, validated_data)