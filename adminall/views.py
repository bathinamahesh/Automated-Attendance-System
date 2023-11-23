from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from users.models import Student,Faculty,Student_Class,Classes,Subjects,Faculty_Subject_Class
from adminall.models import DayModel,PeriodModel,TimeTable
from adminall.models import DayModel,PeriodModel
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required(login_url='/login')
def admin_home(request):
    logged_in = request.session.get('logged_in')
    if logged_in:
        val=1
        del request.session['logged_in']  # Clear the logged_in session variable after use
    else:
        val=0
    classes=Classes.objects.all().count()
    students=Student.objects.all().count()
    faculty=Faculty.objects.all().count()
    subjects=Subjects.objects.all().count()
    allstudents=Student_Class.objects.all()
    return render(request,'admin/admin_dash.html',context={
        'classcount':classes,
        'studentcount':students,
        'facultycount':faculty,
        'subjectcount':subjects,
        'allstudents':allstudents,
        'logged_in':val
                          })
@login_required(login_url='/login')
def admin_student(request):

    classes=Classes.objects.all()
    students=Student_Class.objects.all()
    if request.method == 'POST':
        user_status = "student"
        user_ids = request.POST.get('user_id')
        username = user_ids
        first_name = request.POST.get('user_firstname')
        last_name = request.POST.get('user_lastname')
        email = request.POST.get('email')
        dateofbirth = request.POST.get('user_dob')
        sex = request.POST.get('user_sex')
        password = request.POST.get('password')
        #classname
        clas=request.POST.get('selclass')
        variable = User.objects.filter(username=username)
        if(len(list(variable)) == 0):
            user = User.objects.create_user(
                username=username, email=email, password=password, user_status=user_status, user_id=user_ids, first_name=first_name, last_name=last_name, birth_date=dateofbirth, sex=sex)
            user.save()
            ###Register Student also
            obj=Student(studentname=user)
            obj.save()
            ###Register Student to Class
            classs=Classes.objects.get(classname=clas)
            obj2=Student_Class(student_id=obj,class_name=classs)
            obj2.save()
            return render(request, 'admin/admin_student.html', context={
                'errorcame': 0,
                'classes':classes,
                "students":students
            })
        else:
            return render(request, 'admin/admin_student.html', context={
                'errorcame': 1,
                'classes':classes,
                "students":students
            })
    return render(request,'admin/admin_student.html', context={
                'classes':classes,
                "students":students
            })

@login_required(login_url='/login')
def admin_faculty(request):
    faculty=Faculty.objects.all()
    if request.method == 'POST':
        user_status = "faculty"
        user_ids = request.POST.get('user_id')
        username = user_ids
        first_name = request.POST.get('user_firstname')
        last_name = request.POST.get('user_lastname')
        email = request.POST.get('email')
        dateofbirth = request.POST.get('user_dob')
        sex = request.POST.get('user_sex')
        password = request.POST.get('password')
        phnno=request.POST.get('phn')
        #classname
        variable = User.objects.filter(username=username)
        if(len(list(variable)) == 0):
            user = User.objects.create_user(
                username=username, email=email, password=password, user_status=user_status, user_id=user_ids, first_name=first_name, last_name=last_name, birth_date=dateofbirth, sex=sex)
            user.save()
            ###Register Student to Class also
            obj=Faculty(facultyname=user)
            obj.save()
            return render(request, 'admin/admin_faculty.html', context={
                'errorcame': 0,
                "faculty":faculty
            })
        else:
            return render(request, 'admin/admin_faculty.html', context={
                'errorcame': 1,
                "faculty":faculty
            })
    return render(request,'admin/admin_faculty.html',context={
                "faculty":faculty
            })

@login_required(login_url='/login')
def admin_classes(request):
    if request.method == 'POST':
        try:
            clname = request.POST.get('clsname')
            obj=Classes(classname=clname)
            obj.save()
            return redirect('admin_classes')
        except:
            allclasses=Classes.objects.all()
            return render(request,'admin/admin_classes.html',context={"allclasses": allclasses,'errorcame': 1})

    allclasses=Classes.objects.all()
    return render(request,'admin/admin_classes.html',context={"allclasses": allclasses})

@login_required(login_url='/login')
def admin_subjects(request):
    if request.method == 'POST':
        subname = request.POST.get('suname')
        if(len(Subjects.objects.filter(subject=subname))==0):
            
            obj=Subjects(subject=subname)
            obj.save()
            allsub=Subjects.objects.all()
            return render(request,'admin/admin_subjects.html',context={"allsubjects": allsub,'errorcame': 0})
        else:
            allsub=Subjects.objects.all()
            return render(request,'admin/admin_subjects.html',context={"allsubjects": allsub,'errorcame': 1})

    allsub=Subjects.objects.all()
    return render(request,'admin/admin_subjects.html',context={"allsubjects": allsub})

@login_required(login_url='/login')
def admin_assign_faculty(request):
    classes=Classes.objects.all()
    faculty=Faculty.objects.all()
    subjects=Subjects.objects.all()
    allfaculty=Faculty_Subject_Class.objects.all()
    if request.method=="POST":
        subname = request.POST.get('subname')
        clname = request.POST.get('clsname')
        fac = request.POST.get('faculty')
        sub_obj=Subjects.objects.get(subject=subname)
        class_obj=Classes.objects.get(classname=clname)
        fac_obj=Faculty.objects.get(facultyname=fac)
        if(Faculty_Subject_Class.objects.filter(faculty_name=fac_obj,class_name=class_obj,subject_name=sub_obj).count()==0):
            new_obj=Faculty_Subject_Class(faculty_name=fac_obj,class_name=class_obj,subject_name=sub_obj)
            new_obj.save()

    return render(request,'admin/admin_assign_faculty.html',context={
        'class':classes,
        'faculty':faculty,
        'subject':subjects,
        'allfaculty':allfaculty
                                })
@login_required(login_url='/login')
def admin_timetable(request):
    classes=Classes.objects.all()
    subjects=Subjects.objects.all().reverse()
    days=DayModel.objects.all()
    periods=PeriodModel.objects.all()
    periodnames=[str(i.period) for i in periods]
    daynames=[str(i.day) for i in days]
    if request.method == 'POST':
        classname=request.POST.get('classtime')
        all_list=[]
        for i in daynames:
            for j in periodnames:
                data=request.POST.get(i+","+j)
                try:
                    faculty=Faculty_Subject_Class.objects.get(subject_name=Subjects.objects.get(subject=data.split(',')[2]),class_name=Classes.objects.get(classname=classname))
                    faculty=faculty.faculty_name.facultyname.username
                except:
                    faculty="None"
                if(faculty!="None"):
                    data+=","+faculty
                    all_list.append(data.split(','))
        if(len(all_list)>0):
            objs=TimeTable.objects.filter(classnamett=classname).delete()
            for i in all_list:
                print("\n",i)
                new_obj=TimeTable(facultynamett=i[3],classnamett=classname,subjectnamett=i[2],daynamett=DayModel.objects.get(day=i[0]),periodnamett=PeriodModel.objects.get(period=i[1]))
                new_obj.save()

    return render(request,'admin/admin_timetable.html',context={
        'class':classes,
        'subject':subjects,
        'days':days,
        'periods':periods,
                                })