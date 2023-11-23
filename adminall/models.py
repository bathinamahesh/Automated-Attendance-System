from django.db import models

# Create your models here.
from users.models import User

class DayModel(models.Model):
    day=models.CharField(max_length=255)
    def __str__(self):
        return self.day
    
class PeriodModel(models.Model):
    period=models.CharField(max_length=255)
    def __str__(self):
        return self.period


class TimeTable(models.Model):
    facultynamett=models.CharField(max_length=255,null=True,blank=True)
    classnamett=models.CharField(max_length=255,null=True,blank=True)
    subjectnamett=models.CharField(max_length=255,null=True,blank=True)
    daynamett=models.ForeignKey(DayModel,on_delete=models.CASCADE,related_name="time_table_day")
    periodnamett=models.ForeignKey(PeriodModel,on_delete=models.CASCADE,related_name="time_table_period")
    def __str__(self):
        return str(self.facultynamett)+" "+str(self.subjectnamett)+" "+str(self.daynamett)+" "+str(self.periodnamett)
     
class RemaindersModel(models.Model):
    username=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    title=models.CharField(max_length=255,null=True,blank=True)
    created_at=models.DateField(null=True,blank=True)
    comment=models.CharField(max_length=255,null=True,blank=True)