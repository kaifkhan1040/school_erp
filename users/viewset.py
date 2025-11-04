from rest_framework.viewsets import ModelViewSet
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import logout, get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from base import response
from constants import CONFIG, CONST_REPORT_MAIL
from .serializers import UserSerializer,DesignationSerializer
from .models import Designation,CustomUser
from .service import auth_password_change
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
def now_local(only_date=False):
    """
    In this method takes only date is true or false. If true means return the date with time (2016-03-15 13:09:08).
    If false means return the date (2016-03-15)
    :param only_date: true / false
    :return: date with time (2016-03-15 13:09:08) and date (2016-03-15)
    """
    if only_date:
        return (timezone.localtime(timezone.now())).date()
    else:
        return timezone.localtime(timezone.now())
    
class userSignupView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = get_user_model().objects.all()
    permission_classes = ('')
    serializer_class = UserSerializer

    @action(methods=['GET'], detail=False)
    def config(self, request):
        data = {}
        parameters = request.query_params.get("parameters", None)
        param_list = parameters.split(",") if parameters else []
        CONFIG["config_date_time"] = now_local()
        CONFIG["config_date_only"] = now_local(True)
        for parameter in param_list:
            if parameter in CONFIG:
                data[parameter] = CONFIG[parameter]
            else:
                data[parameter] = None
        return response.Ok(data)

    @action(methods=["POST"], detail=False)
    def login(self, request):
        print('8'*100,request.data)
        # data=request.data.get()
        email, password =request.data.get('email'), request.data.get('password')
        print('email',email)
        user = authenticate(username=request.data['email'], password=request.data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key,'user':UserSerializer(user).data})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)

   

    @action(methods=['POST'], detail=False,permission_classes=[IsAuthenticated],authentication_classes = [TokenAuthentication])
    def logout(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return response.Ok({"detail": "Successfully logged out."})
    
    @action(methods=['Get'], detail=False,permission_classes=[IsAuthenticated],authentication_classes = [TokenAuthentication])
    def get_team(self, request):
        manager = CustomUser.objects.get(id=request.user.id)
        subordinates = manager.subordinates.all()
        team= [
            {
                "id": u.id,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "role": u.role,
                "designation": u.designation.name if u.designation else None
            }
            for u in subordinates
        ]
        print('team:',team)

    @action(methods=['POST'], detail=True)
    def passwordchange(self, request,pk=None):
        user = self.get_object()
        data = auth_password_change(request)
        new_password = data.get('new_password')
        if user:
            user.set_password(new_password)
            user.save()
            content = {'success': 'Password changed successfully.'}
            return response.Ok(content)
        else:
            content = {'detail': 'user not found'}
            return response.BadRequest(content)

    @action(methods=['POST'], detail=True)
    def deactivate(self, request):
        user = self.get_object()
        is_active = request.data('is_active')
        user.is_active = is_active
        user.save()
        content = {'success': 'User Deactivted successfully.'}
        return response.Ok(content)
    
    @action(methods=['POST'], detail=False)
    def createuser(self, request):
        email =request.data.get('email')
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        designation = request.data.get('designation')
        role = request.data.get('role')
        password = request.data.get('password')
        reporting_to = request.data.get('reporting_manager')
        des_obj=Designation.objects.filter(id=designation).first()
        reporting_to=CustomUser.objects.filter(id=reporting_to).first() 
        if not reporting_to:
            return Response({'error': 'Please enter valid reporting manager'}, status=401)
        if not des_obj:
            return Response({'error': 'Please enter valid desiganation'}, status=401)
        
        checkuser = CustomUser.objects.filter(email=email,is_active=True).first()
        if not checkuser:
            CustomUser.objects.create_user(
            email=email,
            first_name=firstname,
            last_name=lastname,
            designation=des_obj,
            role=role,
            password=password,
            reporting_manager=reporting_to
        )
            return Response({'message':'user created successfully'},status=201)
        return Response({'error': 'User with this email already exists'}, status=401)
        
            

            

class DesignationViewSet(ModelViewSet):
    serializer_class = DesignationSerializer
    queryset = Designation.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = (JSONParser, MultiPartParser)
    