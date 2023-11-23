from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from faculty.models import messages, Assignments
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages as msg
from students.models import Submissions
from users.models import Classes, Student, Student_Class, Faculty_Subject_Class, Faculty
from datetime import datetime
from django import template
from adminall.models import *
from users.models import Student_Class
from adminall.models import RemaindersModel
from faculty.models import Upload_Notices
register = template.Library()


@register.filter(name='index')
def index(sequence, position):
    return sequence[position]


User = get_user_model()


@login_required
def home_page(request):
    return render(request, 'student/student_main.html')


@login_required
def dash_board(request):
    logged_in = request.session.get('logged_in')
    if logged_in:
        val=1
        del request.session['logged_in']  # Clear the logged_in session variable after use
    else:
        val=0
    today = datetime.now()
    daytoday = today.strftime("%A").upper()
    days=DayModel.objects.all()
    periods=PeriodModel.objects.all()
    periodnames=[str(i.period) for i in periods]
    periods_list=[]
    ##find Student Class
    class_obj=Student_Class.objects.get(student_id=Student.objects.get(studentname=request.user))
    classname=class_obj.class_name
    total_objects = Upload_Notices.objects.filter(notice_class_name=Classes.objects.get(classname=classname)
        ).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    print("\n\n")
    print("Total Objects : ",total_objects)
    for j in periodnames:
            try:
                obj=TimeTable.objects.get(daynamett=DayModel.objects.get(day=daytoday),periodnamett=PeriodModel.objects.get(period=j),classnamett=classname)
                periods_list.append(str(obj.subjectnamett))
            except:
                periods_list.append("-")
                pass
    all_remainders=RemaindersModel.objects.filter(username=request.user).order_by('-created_at')
    if request.method=="POST":
        title=request.POST.get('titlename')
        date=request.POST.get('datename')
        comment=request.POST.get('commentname')
        if(title!="" and date!="" and comment!=""):
            obj=RemaindersModel(username=request.user,title=title,created_at=date,comment=comment)
            obj.save()
        return redirect('student_dashboard')
    submitted = []
    marksassign = []
    user = request.user.user_id
    student = Student_Class.objects.get(student_id=Student(
        studentname=User.objects.get(user_id=user)))
    student_class = student.class_name
    l = Assignments.objects.filter(
        assignment_class=student_class).order_by('-assignment_created')
    submittedcount=0
    unsubmittedcount=0
    for i in l:
        asdet = i
        try:
            new = Submissions.objects.get(student_id=User.objects.get(
                user_id=request.user.user_id), assignment_detail=i)
            submitted += [1]
            submittedcount+=1
            if new.givenmarks is None:
                marksassign += [0]
            else:
                marksassign += [new.givenmarks]
        except Exception as e:
            marksassign += [0]
            submitted += [0]
            unsubmittedcount+=1
      
    return render(request, 'student/student_dashboard.html',
                  context={
                      'days':days,
                      'periods':periods,
                      'today':daytoday,
                      'today_periods':periods_list,
                      'remainders':all_remainders,
                      'classname':classname,
                      "assignments": l, 
                      "submittedlist": submitted,
                      "marksgiven": marksassign,
                      "scount":submittedcount,
                      "ucount":unsubmittedcount,
                      "all_notices": total_objects,
                      "inboxmsg": inboxmsg,
                      'logged_in':val
                  })


@login_required
def std_inbox(request):
    if request.method == "POST":
        userid = request.user.user_id
        username = request.user.first_name
        msgto = request.POST.get("get_name")
        print("__"*20, msgto)
        msg = request.POST.get("textmessage")
        objmsg = messages(sender=userid, receive=msgto,
                          sender_name=username, sendmessage=msg,)
        objmsg.save()
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser))
    ##find Student Class
    class_obj=Student_Class.objects.get(student_id=Student.objects.get(studentname=request.user))
    classname=class_obj.class_name
    total_objects = Upload_Notices.objects.filter(notice_class_name=Classes.objects.get(classname=classname)
        ).order_by('created_at')
    return render(request, 'student/student_inbox.html', 
                  context={
                      "inboxmsg": inboxmsg,
                      "all_notices": total_objects,
                      })


@login_required
def std_profile(request):
    user = request.user.user_id
    student = Student_Class.objects.get(student_id=Student(
    studentname=User.objects.get(user_id=user)))
    student_class = student.class_name
    submitted = []
    marksassign = []
    l = Assignments.objects.filter(
        assignment_class=student_class).order_by('-assignment_created')
    for i in l:
        try:
            new = Submissions.objects.get(student_id=User.objects.get(
                user_id=request.user.user_id), assignment_detail=i)
            submitted += [1]
            if new.givenmarks is None:
                marksassign += [0]
            else:
                result=int(new.givenmarks)/int(i.assignment_marks)*100
                marksassign += [int(result)]
        except Exception as e:
            marksassign += [0]
            submitted += [0]
    if request.method == 'POST':
        curruser = request.user.username
        data = User.objects.get(user_id=curruser)
        return render(request, 'faculty/faculty_profile_update.html', context={"userprofile": data,"assignments": l,})
    curruser = request.user.username
    data = User.objects.get(user_id=curruser)
    ###Sending additional data
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser))
    ##find Student Class
    class_obj=Student_Class.objects.get(student_id=Student.objects.get(studentname=request.user))
    classname=class_obj.class_name
    total_objects = Upload_Notices.objects.filter(notice_class_name=Classes.objects.get(classname=classname)
        ).order_by('created_at')
    return render(request, 'student/student_profile.html', 
                  context={
                      "basicdata": data,
                      "inboxmsg": inboxmsg,
                      "all_notices": total_objects,
                      "assignments": l,
                      "submittedlist": submitted,
                      "marksgiven": marksassign,
                      })


@login_required
def std_profile_update(request):
    errorsave = 0
    if request.method == "POST":
        curruser = request.user.username
        instance = User.objects.get(user_id=curruser)
        # instance.user_id = request.POST.get("profile_id")
        instance.bio = request.POST.get("profile_bio")
        instance.location = request.POST.get("profile_location")
        instance.sex = request.POST.get("profile_gender")
        instance.birth_date = request.POST.get("profile_birth")
        instance.first_name = request.POST.get("profile_first")
        instance.last_name = request.POST.get("profile_last")
        instance.email = request.POST.get("profile_email")
        # -------For Files
        if "profile_pic" in request.FILES:
            upload = request.FILES['profile_pic']
            """fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
            print("__"*30, "__*********"*20, file_url)"""
            instance.profile_pic = upload
        print("|___|"*20, instance.profile_pic.url)
        try:
            instance.save()
            print("\n\n\n", instance.user_id, " ", instance.first_name, " ", instance.last_name, " ", instance.email, " ", instance.bio, " ", instance.location,
                  " ", instance.sex, " ", instance.birth_date, " ", "\n\n")
            profile_edited = 1
            return redirect('student_profile')
        except Exception as e:
            print("______"*30, "Error While Saving", e)

    curr = request.user.username
    data = User.objects.get(user_id=curr)
    ###Sending additional data
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser))
    class_obj=Student_Class.objects.get(student_id=Student.objects.get(studentname=request.user))
    classname=class_obj.class_name
    total_objects = Upload_Notices.objects.filter(notice_class_name=Classes.objects.get(classname=classname)
        ).order_by('created_at')
    return render(request, 'student/student_profile_update.html',
                   context={
                       "userprofile": data,
                        "inboxmsg": inboxmsg,
                      "all_notices": total_objects,
                       })


@ login_required
def std_marks(request):
    return render(request, 'student/student_marks.html')


@ login_required
def std_assignments(request):
    submitted = []
    marksassign = []
    user = request.user.user_id
    student = Student_Class.objects.get(student_id=Student(
        studentname=User.objects.get(user_id=user)))
    student_class = student.class_name
    l = Assignments.objects.filter(
        assignment_class=student_class).order_by('-assignment_created')
    for i in l:
        asdet = i
        print("\n\n", asdet)
        try:
            new = Submissions.objects.get(student_id=User.objects.get(
                user_id=request.user.user_id), assignment_detail=i)
            submitted += [1]
            if new.givenmarks is None:
                marksassign += [0]
            else:
                marksassign += [new.givenmarks]
        except Exception as e:
            marksassign += [0]
            submitted += [0]
    ###Sending additional data
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser))
    class_obj=Student_Class.objects.get(student_id=Student.objects.get(studentname=request.user))
    classname=class_obj.class_name
    total_objects = Upload_Notices.objects.filter(notice_class_name=Classes.objects.get(classname=classname)
        ).order_by('created_at')
    print("\n\n", submitted, "\n\n")
    return render(request, 'student/student_assignments.html', 
                  context={
                      "assignments": l, 
                      "submittedlist": submitted,
                      "marksgiven": marksassign,
                      "inboxmsg": inboxmsg,
                      "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                        })


@ login_required
def teachers_list(request):
    user = request.user.user_id
    student = Student_Class.objects.get(student_id=Student(
        studentname=User.objects.get(user_id=user)))
    student_class = student.class_name
    tot_teachers = Faculty_Subject_Class.objects.filter(
        class_name=student_class)
    ###Sending additional data
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser))
    class_obj=Student_Class.objects.get(student_id=Student.objects.get(studentname=request.user))
    classname=class_obj.class_name
    total_objects = Upload_Notices.objects.filter(notice_class_name=Classes.objects.get(classname=classname)
        ).order_by('created_at')
    return render(request, 'student/student_teachers_list.html', 
                  context={
                      "tot_teachers": tot_teachers,
                       "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                      })


@ login_required
def std_message(request):
    std = request.user.user_id
    std_class = (Student_Class.objects.get(
        student_id=Student.objects.get(studentname=std))).class_name
    faculty = Faculty_Subject_Class.objects.filter(
        class_name=Classes.objects.get(classname=std_class))
    ###Sending additional data
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser))
    class_obj=Student_Class.objects.get(student_id=Student.objects.get(studentname=request.user))
    classname=class_obj.class_name
    total_objects = Upload_Notices.objects.filter(notice_class_name=Classes.objects.get(classname=classname)
        ).order_by('created_at')
    if request.method == 'POST':
        userid = request.user.user_id
        username = request.user.first_name
        #msgtitle = request.POST.get("msg-title")
        msgto = request.POST.get("msg-faculty")
        msg = request.POST.get("msg-desc")
        objmsg = messages(sender=userid, receive=msgto,
                          sender_name=username, sendmessage=msg,)
        objmsg.save()
        return render(request, 'student/student_message.html', context={
            "totfaculty": faculty,
              "msgsuccess": 1,
               "all_notices": total_objects,
                "inboxmsg": inboxmsg,
              })

    return render(request, 'student/student_message.html', context={"totfaculty": faculty, "msgsuccess": 0})


@ login_required
def std_change(request):
    ###Sending additional data
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser))
    class_obj=Student_Class.objects.get(student_id=Student.objects.get(studentname=request.user))
    classname=class_obj.class_name
    total_objects = Upload_Notices.objects.filter(notice_class_name=Classes.objects.get(classname=classname)
        ).order_by('created_at')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            msg.success(
                request, 'Your password was successfully updated!')
            return render(request, 'student/student_dashboard.html', {
                'form': form, 
                "passwordchanged": 1,
                "all_notices": total_objects,
                "inboxmsg": inboxmsg,

            })
        else:
            return render(request, 'student/student_change_password.html',
                           {
                               'form': form, 
                               "errorinchange": 1,
                                "all_notices": total_objects,
                                "inboxmsg": inboxmsg,
                               })
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'student/student_change_password.html', {
        'form': form,
        "all_notices": total_objects,
        "inboxmsg": inboxmsg,
    })


@ login_required
def std_notice(request):
    return render(request, 'student/student_notice.html')


def file_upload(request, assign_id):
    if "uploadfile" in request.FILES:
        userid = User.objects.get(user_id=request.user.user_id)
        assignobj = Assignments.objects.get(assignment_id=assign_id)
        facult = assignobj.assignment_faculty.facultyname
        print("__"*20, facult)
        filesubmit = request.FILES['uploadfile']
        issubmitted = 1
        uploadingobj = Submissions(assignment_detail=assignobj, student_id=userid,
                                   file_submit=filesubmit, is_submitted=issubmitted, faculty=facult)
        uploadingobj.save()
        print("\n\nFile came\n")
    print("__"*20, "function_called", assign_id)
    return redirect('student_assignments')
