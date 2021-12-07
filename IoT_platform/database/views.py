from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from database.models import *
from database.serializers import *
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Q

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def create(self, request):
        try:
            data = request.data
            s = UserSerializer(data=data)
            print("Valid data: "+str(s.is_valid()))
            if s.is_valid():
                username = data['username']
                password = data['password']
                is_staff = data['is_staff']
                role = data['role']
                email = data['email']
                User.objects.create_user(username=username,email=email,password=password,is_staff=is_staff,role=role)
                return Response(status=201, data=data)
            else:
                data = s.errors
                return Response(status=400, data=data)
        except Exception as e:
            print(e)
            return HttpResponse(status=400)

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        print(token)
        role = token.user.role
        return Response({'token': token.key, 'role': role, 'id': token.user_id})

class ParameterViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Parameters to be CRUDed.
    """
    serializer_class = ParameterSerializer

    def get_queryset(self):
        sensor = self.request.query_params.get('sensor', None)
        serial = self.request.query_params.get('serial', None)
        type = self.request.query_params.get('type', None)
        query = Q()
        if sensor is not None:
            query = query & Q(sensor=sensor)
        if serial is not None:
            query = query & Q(sensor__serial=serial)
        if type is not None:
            query = query & Q(type=type)
        #if not self.request.user.is_staff:
        #    query = query & Q(sensor__owner=self.request.user)    
        queryset = Parameter.objects.all()
        queryset = queryset.filter(query)
        return queryset

class SensorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Sensors to be CRUDed.
    """
    serializer_class = SensorSerializer

    def get_queryset(self):
        query = Q()
        queryset = Sensor.objects.all()
        queryset = queryset.filter(query)
        return queryset

class SensorvalueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Sensorvalues to be CRUDed.
    """
    serializer_class = SensorvalueSerializer
    def get_queryset(self):
        parameter = self.request.query_params.get('parameter',None)
        starts_after = self.request.query_params.get('starts_after', None)
        ends_before = self.request.query_params.get('ends_before', None)
        last = self.request.query_params.get('last', 0)
        queryset = Sensorvalue.objects.all()
        query = Q()
        if parameter is not None:
            query = query & Q(parameter=parameter)
        if starts_after is not None:
            query = query & Q(timestamp__gte=starts_after)
        if ends_before is not None:
            query = query & Q(timestamp__lte=ends_before)
        queryset = queryset.filter(query)
        if last is not 0:
            sliced_qs = queryset.order_by('-timestamp')[:int(last)]
            queryset = queryset.filter(id__in=sliced_qs).order_by('timestamp')
        #if not self.request.user.is_staff:
        #    query = query & Q(parameter__sensor__owner=self.request.user)
        return queryset

