# -*- coding: utf-8 -*-
from rest_framework import serializers
from database.models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('__all__')

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ('__all__')

class SensorvalueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensorvalue
        fields = ('__all__')
