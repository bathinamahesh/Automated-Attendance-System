from django.urls import path
from .views import admin_home,admin_student,admin_faculty,admin_classes,admin_subjects,admin_assign_faculty,admin_timetable


urlpatterns = [
    path('admindash/', admin_home, name='admin_home'),
    path('adminstudent/', admin_student, name='admin_student'),
    path('adminfaculty/', admin_faculty, name='admin_faculty'),
    path('adminsubjects/', admin_subjects, name='admin_subjects'),
    path('adminclasses/', admin_classes, name='admin_classes'),
    path('adminassignfaculty/', admin_assign_faculty, name='admin_assign_faculty'),
    path('admintimetable/', admin_timetable, name='admin_timetable'),
]