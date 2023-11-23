from django.contrib import admin
from .models import TimeTable,DayModel,PeriodModel,RemaindersModel
# Register your models here.
admin.site.register(DayModel)
admin.site.register(PeriodModel)
admin.site.register(TimeTable)
admin.site.register(RemaindersModel)