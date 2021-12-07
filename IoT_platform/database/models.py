from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    role = models.TextField(default="admin")
    def __str__(self):
        return self.username
    class JSONAPIMeta:
        resource_name = "user"

class Sensor(models.Model):
    name = models.TextField(null=False)
    serial = models.TextField(null=False,unique=True)
    lat = models.DecimalField(null=True, max_digits=13, decimal_places=10)
    lng = models.DecimalField(null=True, max_digits=13, decimal_places=10)
    status = models.IntegerField(default=0)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=60)
    last_sent = models.DateTimeField(null=True)
    def __str__(self):
        return str(self.serial)
    def natural_key(self):
        return self.serial
    class JSONAPIMeta:
        resource_name = "sensor"
    class Meta:
        ordering = ['id']

class Parameter(models.Model):
    type = models.TextField(null=False)
    mu = models.TextField(null=False)
    value = models.DecimalField(max_digits=13,decimal_places=3,null=True)
    sensor = models.ForeignKey(Sensor,null=True,on_delete=models.CASCADE)
    threshold_min = models.DecimalField(max_digits=13, decimal_places=10,null=True)
    threshold_max = models.DecimalField(max_digits=13, decimal_places=10,null=True)
    def __str__(self):
        return (str(self.sensor)+": "+str(self.type))
    def natural_key(self):
        return self.self
    class JSONAPIMeta:
        resource_name = "parameter"

class Sensorvalue(models.Model):
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE)     
    timestamp = models.DateTimeField()
    value = models.DecimalField(max_digits=20, decimal_places=10)
    def __str__(self):
        return ('%s, %s, %s') % (self.parameter, self.value, self.timestamp)
    class JSONAPIMeta:
        resource_name = "sensorvalue"
    class Meta:
        get_latest_by = 'timestamp'
        ordering = ['timestamp']
    def save(self, *args, **kwargs):
        parameter = self.parameter
        sensor = self.parameter.sensor
        if ((sensor.last_sent is None) or (parameter.value is None)) or (sensor.last_sent <= self.timestamp):
            sensor.last_sent = self.timestamp
            sensor.status = 1
            parameter.value = self.value
            parameter.save()
            sensor.save()
        super().save(*args, **kwargs)
