
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from users.models import Classes, Student_Class, Faculty_Subject_Class, Faculty
from .models import Upload_Notices, Assignments, Subjects, Classes_Taken, StudentAttendance, messages
from students.models import Mid_marks, Submissions
from django.db.models.query import QuerySet
from datetime import datetime, date
from .forms import UserUpdateForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model
from django.contrib import messages as msg
from adminall.models import *

########For the ML model 
import tensorflow as tf
import numpy as np
import os
import cv2
import pandas as pd
from PIL import Image
img_size = 64
import dlib





User = get_user_model()


@login_required(login_url='/login')
def home_page(request):
    return render(request, 'faculty/faculty_main.html')


@login_required(login_url='/login')
def dash_board(request):
    logged_in = request.session.get('logged_in')
    if logged_in:
        val=1
        del request.session['logged_in']  # Clear the logged_in session variable after use
    else:
        val=0
    faculty_named = request.user.user_id
    total_class_obj = Faculty_Subject_Class.objects.filter(
            faculty_name=Faculty.objects.get(facultyname=faculty_named))
    allclasses=[i.class_name.classname for i in total_class_obj]
    taken_number=[Classes_Taken.objects.filter(faculty_taken=i).count() for i in total_class_obj]
    print("\n\n")
    print(allclasses)
    print(taken_number)
    print("\n\n")
    today = datetime.now()
    daytoday = today.strftime("%A").upper()
    days=DayModel.objects.all()
    periods=PeriodModel.objects.all()
    periodnames=[str(i.period) for i in periods]
    periods_list=[]
    classcount=Classes.objects.all().count()
    studentcount=Student_Class.objects.all().count()
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('-created_at')
    ##classnamett
    for j in periodnames:
            try:
                obj=TimeTable.objects.get(facultynamett=request.user.username,daynamett=DayModel.objects.get(day=daytoday),periodnamett=PeriodModel.objects.get(period=j))
                periods_list.append(str(obj.classnamett))
            except:
                periods_list.append("-")
                pass
    all_remainders=RemaindersModel.objects.filter(username=request.user).order_by('-created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    if request.method=="POST":
        title=request.POST.get('titlename')
        date=request.POST.get('datename')
        comment=request.POST.get('commentname')
        if(title!="" and date!="" and comment!=""):
            obj=RemaindersModel(username=request.user,title=title,created_at=date,comment=comment)
            obj.save()
        return redirect('faculty_dashboard')
    return render(request, 'faculty/faculty_dashboard.html',
                  context={
                      'days':days,
                      'periods':periods,
                      'today':daytoday,
                      'today_periods':periods_list,
                      'remainders':all_remainders,
                      'classcount':classcount,
                      'studentcount':studentcount,
                       "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                       'allclasses':allclasses,
                       'taken_number':taken_number,
                       'logged_in':val,
                  })


@login_required(login_url='/login')
def inbox(request):
    if request.method == "POST":
        userid = request.user.user_id
        username = request.user.first_name
        msgto = request.POST.get("get_name")
        print("__"*20, msgto)
        msg = request.POST.get("textmessage")
        objmsg = messages(sender=userid, receive=msgto,
                          sender_name=username, sendmessage=msg,)
        objmsg.save()
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    return render(request, 'faculty/faculty_inbox.html', 
                  context={
                      "inboxmsg": inboxmsg,
                      "all_notices": total_objects,
                      })


@login_required(login_url='/login')
def profile(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    if request.method == 'POST':
        curruser = request.user.username
        data = User.objects.get(user_id=curruser)
        return render(request, 'faculty/faculty_profile_update.html', 
                      context={
                          "userprofile": data,
                           "inboxmsg": inboxmsg,
                           "all_notices": total_objects,
                          })
    curruser = request.user.username
    data = User.objects.get(user_id=curruser)
    return render(request, 'faculty/faculty_profile.html', 
                  context={
                      "basicdata": data,
                       "inboxmsg": inboxmsg,
                      "all_notices": total_objects,
                      })


@login_required(login_url='/login')
def take_attendance(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    if request.method == 'POST':
        class_nam = request.POST.get('select_student_class')
        # print("-_"*50, class_nam)
        if(class_nam==None):
            return redirect('faculty_take_attendace')
        selecting_students = Student_Class.objects.filter(class_name=class_nam)
        l = []
        for i in selecting_students:
            l.append(i.student_id)
        final_list = []
        for i in l:
            final_list.append(User.objects.get(username=i))
        faculty_named = request.user.user_id
        total_class_obj = Faculty_Subject_Class.objects.filter(
            faculty_name=Faculty.objects.get(facultyname=faculty_named))
        return render(request, 'faculty/faculty_take_attendance.html', 
                      context={"students_list_test": final_list,
                                "classroom_name": class_nam,
                                "total_classes": total_class_obj,
                                "all_notices": total_objects,
                                "inboxmsg": inboxmsg,
                                })
    faculty_named = request.user.user_id
    total_class_obj = Faculty_Subject_Class.objects.filter(
        faculty_name=Faculty.objects.get(facultyname=faculty_named))
    return render(request, 'faculty/faculty_take_attendance.html', 
                  context={
                      "total_classes": total_class_obj,
                        "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                      })



@login_required(login_url='/login')
def upload_assignment(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    upload_done = 0
    if request.method == 'POST':
        assign_faculty = request.user.username
        assign_id = request.POST.get('assign_id')
        assign_title = request.POST.get('assign_title')
        assign_desc = request.POST.get('assign_desc')
        assign_marks = request.POST.get('assign_marks')
        assign_class = request.POST.get('assign_class')
        assign_due = request.POST.get('assign_due')
        if "assignupload" in request.FILES:
            #print("___"*20)
            upload = request.FILES['assignupload']
            """fss = FileSystemStorage()
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
            print("__"*30, "__*********"*20, file_url)"""
        assign_faculty_subject = Faculty_Subject_Class.objects.get(
            faculty_name=assign_faculty, class_name=assign_class)
        assign_faculty_subject = assign_faculty_subject.subject_name
        writing_assignment = Assignments(assignment_id=assign_id, assignment_title=assign_title, assignment_marks=assign_marks, assignment_class=Classes.objects.get(classname=assign_class),
                                         assignment_due=assign_due, assignment_file=upload, assignment_faculty=Faculty.objects.get(facultyname=assign_faculty), assignmentsubject=Subjects.objects.get(subject=assign_faculty_subject), assignment_desc=assign_desc)
        writing_assignment.save()
        upload_done = 1

    faculty_named = request.user.user_id
    total_class_obj = Faculty_Subject_Class.objects.filter(
        faculty_name=Faculty.objects.get(facultyname=faculty_named))
    return render(request, 'faculty/faculty_upload_assignment.html',
                   context={
                       "upload_done": upload_done,
                        "total_classes": total_class_obj,
                        "all_notices": total_objects,
                        "inboxmsg": inboxmsg,
                        })


@login_required(login_url='/login')
def assignment_list(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    l = Assignments.objects.filter(
        assignment_faculty=Faculty.objects.get(facultyname=request.user.username)).order_by('-assignment_created')
    return render(request, 'faculty/faculty_assignment_list.html', 
                  context={
                      "assignments": l,
                        "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                      })


@login_required(login_url='/login')
def view_submissions(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    facult = request.user.user_id
    submissions = Submissions.objects.filter(faculty=facult).order_by('-dateofsub')
    return render(request, 'faculty/faculty_view_submissions.html', 
                  context={
                      "tot_submissions": submissions,
                        "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                       })


@login_required(login_url='/login')
def students_list(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    if request.method == 'POST':
        class_nam = request.POST.get('select_student_class')
        # print("-_"*50, class_nam)
        selecting_students = Student_Class.objects.filter(class_name=class_nam)
        l = []
        for i in selecting_students:
            l.append(i.student_id)
        final_list = []
        for i in l:
            final_list.append(User.objects.get(username=i))
        return render(request, 'faculty/faculty_students_list.html', 
                      context={
                          "students_list_test": final_list,
                            "classroom_name": class_nam,
                            "all_notices": total_objects,
                            "inboxmsg": inboxmsg,
                            })
    return render(request, 'faculty/faculty_students_list.html')


@login_required(login_url='/login')
def write_notice(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    faculty_write_error = 0
    if request.method == 'POST':
        try:
            faculty_names = request.user.username
            notice_ids = request.POST.get('notice_id')
            notice_titles = request.POST.get('notice_title')
            notice_class = request.POST.get('noticed_class')
            notice_desc = request.POST.get('notice_text')
            # print("__"*20, notice_class, faculty_names,notice_ids, notice_desc, notice_titles)
            # --Need to change Classes Choice to CharField
            if(notice_titles == "" or notice_desc == ""):
                raise Exception("Please Enter Correct Details")
            notice_subjected = Faculty_Subject_Class.objects.get(
                faculty_name=faculty_names, class_name=notice_class)
            if(notice_subjected == None):
                notice_subject = "default"
            else:
                notice_subject = notice_subjected.subject_name
            writing_notice = Upload_Notices(notice_id=notice_ids, notice_title=notice_titles, notice_description=notice_desc,
                                            faculty_name_notice=Faculty.objects.get(facultyname=faculty_names), notice_class_name=Classes.objects.get(classname=notice_class), notice_subject_name=notice_subject)
            writing_notice.save()
            faculty_write_error = 2
        except:
            faculty_write_error = 1
            # print("___"*100, "please Enter Correct Details Asap")
    # total_objects = Upload_Notices.objects.all()
    faculty_named = request.user.user_id
    total_class_obj = Faculty_Subject_Class.objects.filter(
        faculty_name=Faculty.objects.get(facultyname=faculty_named))
    print("__"*25, faculty_write_error)
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username)
    # print("_*"*50, total_objects)
    return render(request, 'faculty/faculty_write_notice.html', context={
        "all_notices": total_objects,
        "faculty_errored": faculty_write_error,
        "total_classes": total_class_obj,
        "all_notices": total_objects,
        "inboxmsg": inboxmsg,

    })


@login_required(login_url='/login')
def change_password(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            msg.success(
                request, 'Your password was successfully updated!')
            return render(request, 'faculty/faculty_dashboard.html', {
                'form': form, 
                "passwordchanged": 1,
                "all_notices": total_objects,
                "inboxmsg": inboxmsg,
            })
        else:
            return render(request, 'faculty/faculty_password_change.html', 
                          {
                              'form': form, "errorinchange": 1,
                                "all_notices": total_objects,
                                "inboxmsg": inboxmsg,
                              })
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'faculty/faculty_password_change.html', {
        'form': form,
          "all_notices": total_objects,
        "inboxmsg": inboxmsg,
    })


@login_required(login_url='/login')
def faculty_time_table(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    days=DayModel.objects.all()
    periods=PeriodModel.objects.all()
    periodnames=[str(i.period) for i in periods]
    daynames=[str(i.day) for i in days]
    cont={ 'days':days,
        'periods':periods,
        'daynames':daynames,
          "all_notices": total_objects,
            "inboxmsg": inboxmsg,
                  }
    main_list=[]
    for i in daynames:
        empty_list=[]
        for j in periodnames:
            try:
                obj=TimeTable.objects.get(facultynamett=request.user.username,daynamett=DayModel.objects.get(day=i),periodnamett=PeriodModel.objects.get(period=j))
                empty_list.append(str(obj.classnamett)+" ("+str(obj.subjectnamett)+" )")
            except:
                empty_list.append("-")
                pass
        main_list.append((i,empty_list))
    cont['day_periods']=main_list
    return render(request, 'faculty/faculty_timetable.html',
                  context=cont)


@login_required(login_url='/login')
def confirm(request, class_n):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")

    is_taken = 0
    try:
        # Register Classes and Take attendance
        # ------------getting class and subject details
        faculty = request.user.user_id
        faculty_obj = Faculty_Subject_Class.objects.get(
            faculty_name=Faculty.objects.get(facultyname=faculty), class_name=class_n)
        # ---validating With Today Date
        isanytaken = Classes_Taken.objects.get(
            faculty_taken=faculty_obj, taken_at=date.today())
        is_taken = 1
    except:
        is_taken = 0
    if(is_taken == 0):
        # REgister the Class
        takentheclass = Classes_Taken(faculty_taken=faculty_obj)
        takentheclass.save()
        # register the Students Attendance
        takenobj = Classes_Taken.objects.get(
            faculty_taken=faculty_obj, taken_at=date.today())
        selected = Student_Class.objects.filter(
            class_name=Classes.objects.get(classname=class_n))
        for i in selected:
            id = i.student_id
            roll = User.objects.get(user_id=id).roll
            print("\n\n", id)
            status = request.POST.get(str(id))
            if(status!=None):
                print("\n\n", "__"*20, i.student_id, "  ", status)
                obj = StudentAttendance(
                    class_taken=takenobj, studentid=id, studentroll=roll, presentorabsent=status)  # presentorabsent=status
                obj.presentorabsent = status
                print("\n\n", obj, "\n\n")
                obj.save()
            else:
                status="absent"
                obj = StudentAttendance(
                    class_taken=takenobj, studentid=id, studentroll=roll, presentorabsent=status)  # presentorabsent=status
                obj.presentorabsent = status
                print("\n\n", obj, "\n\n")
                obj.save()

    
    # Returning No.of Classes
    totalclasses = Classes_Taken.objects.filter(
        faculty_taken=faculty_obj).order_by('-taken_at')
    percentages=[]
    for i in totalclasses:
        percentages.append(int(i.calculate_attendance()))
    print("\n\n",percentages)
    return render(request, 'faculty/trying.html', 
                  context={"totalclasses": totalclasses, 
                           "errorcame": is_taken,
                        "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                       "percentages":percentages,
                       })


@login_required(login_url='/login')
def profile_update(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
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
            return redirect('faculty_profile')
        except Exception as e:
            print("______"*30, "Error While Saving", e)

    curr = request.user.username
    data = User.objects.get(user_id=curr)
    return render(request, 'faculty/faculty_profile_update.html', 
                  context={
                      "userprofile": data,
                        "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                      })

@login_required(login_url='/login')
def givemarks(request, assign_id, assign_stdid):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    # student_id
    getobj = Submissions.objects.get(student_id=User.objects.get(user_id=assign_stdid),
                                     assignment_detail=Assignments.objects.get(assignment_id=assign_id))
    print(getobj)
    marks = request.POST.get("given_marks")
    if(str(marks) == ""):
        facult = request.user.user_id
        submissions = Submissions.objects.filter(faculty=facult)
        return render(request, 'faculty/faculty_view_submissions.html', 
                      context={
                          "tot_submissions": submissions, 
                          "errorwhilegive": 1,
                            "all_notices": total_objects,
                       "inboxmsg": inboxmsg,})
    else:
        getobj.givenmarks = marks
        getobj.is_awarded = str(1)
        getobj.save()
     # print("\n\n", assign_id, assign_stdid, "\n\n", marks, "\n\n")
    return redirect("faculty_view_submissions")

@login_required(login_url='/login')
def detailattend(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    facultys = request.POST.get("faculty")
    subjects = request.POST.get("subject")
    classs = request.POST.get("class")
    takenat=request.POST.get("takenat")
    date_obj = datetime.strptime(takenat, "%B %d, %Y")
    formatted_date = "{:04d}-{:02d}-{:02d}".format(date_obj.year, date_obj.month, date_obj.day)
    attendanceobj = Classes_Taken.objects.get(faculty_taken=Faculty_Subject_Class.objects.get(faculty_name=Faculty.objects.get(
        facultyname=facultys), subject_name=Subjects.objects.get(subject=subjects), class_name=Classes.objects.get(classname=classs)), taken_at=formatted_date)
    total_students = StudentAttendance.objects.filter(
        class_taken=attendanceobj)
    totlist = []
    for i in total_students:
        print("\n", i.presentorabsent)
        totlist += [i.presentorabsent]

    return render(request, 'faculty/detailview.html', 
                  context={
                      "total_stude": total_students, 
                           "tot_list": totlist,
                             "attendobj": attendanceobj,
                               "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                           })

@login_required(login_url='/login')
def ml_model(request):
    faculty_named = request.user.user_id
    total_class_obj = Faculty_Subject_Class.objects.filter(
        faculty_name=Faculty.objects.get(facultyname=faculty_named))
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    if request.method == 'POST':
        if "picupload" in request.FILES:
            upload = request.FILES['picupload']
            #print("___"*20,upload.read())
        im = Image.open(upload)
        im.save("im.jpg")
        loaded_model = tf.keras.models.load_model('modelss/person_classifier_temp_100.h5')
        # Load the detector
        detector = dlib.get_frontal_face_detector()
        # Load the predictor
        predictor = dlib.shape_predictor("modelss/shape_predictor_68_face_landmarks.dat")
        results = pd.DataFrame(columns=['Image', 'Person', 'Date']) 
        CSE1 = ['N180015', 'N180027', 'N180082', 'N180086', 'N180121', 'N180160', 'N180255']
        CSE2 = ['N180309', 'N180310', 'N180390', 'N180473', 'N180518', 'N180520', 'N180530']
        CSE3 = ['N180548', 'N180550', 'N180606', 'N180616', 'N180636', 'N180638', 'N180676']
        CSE4 = ['N180678', 'N180681', 'N180696', 'N180726', 'N180727', 'N180742', 'N180749']
        CSE5 = ['N180798', 'N180814', 'N180827', 'N180872', 'N180884', 'N181128', 'N181150', 'N181164']
        names=CSE1+CSE2+CSE3+CSE4+CSE5
        select_class=request.POST.get('select_student_class')
        ids=[i.student_id.studentname.user_id for i in Student_Class.objects.filter(class_name=Classes.objects.get(classname=select_class))]
        print("\n\n",ids,"\n\n")
        ########
        # Load the image
        img = cv2.imread("im.jpg")
        #print("___"*20,os.getcwd())
        #print("___"*20,img.shape)

        # Convert image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces using HOG + Linear SVM detector
        faces = detector(gray, 1)
        ###FAces-------------------
        # Create the "faces" directory if it doesn't exist
        if not os.path.exists("faces"):
            os.makedirs("faces")

        # Loop through all files in the directory and remove them
        for filename in os.listdir("faces"):
            file_path = os.path.join("faces", filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        ###Media faces---------------
        if  not os.path.exists("media/faces"):
            os.makedirs("media/faces")
        # Loop through all files in the directory and remove them
        for filename in os.listdir("media/faces"):
            file_path = os.path.join("media/faces", filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        # Iterate over each face
        l=[]
        predicted_persons = set()
        main_list=[]
        for i, face in enumerate(faces):
            # Get the landmarks/parts for the face in box d.
            landmarks = predictor(gray, face)

            # Extract face region as a numpy array
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            face_region = img[y1:y2, x1:x2]

            # Convert face region to grayscale
            face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)

            # Save the face region as a grayscale image in the "faces" directory
            cv2.imwrite(f"faces/{i}.png", face_gray)
            cv2.imwrite(f"media/faces/{i}.png", face_gray)
            test_img = cv2.imread('media/faces/'+str(i)+'.png')
            test_img = cv2.resize(test_img, (img_size, img_size))
            test_img = np.array(test_img).reshape(-1, img_size, img_size, 3) / 255.0
            prediction = loaded_model.predict(test_img)
            person = names[np.argmax(prediction)]
            if ((person not in predicted_persons) and (person  in ids)):
                # Add the predicted person to the set
                predicted_persons.add(person)

                # Output the name and ID of the person
                print("ID:", i, "  Person:", person)
                main_list.append((i,str(person)))

            l.append(str(person))
        print(main_list)
        print("\n\ncount Main ",len(l))
        print("\n\npred_list :",len(main_list))
            # Output the name of the person
            #print("The person in the test image is:", person)
        #####@@@@@@@@@@@@@@@@@@@@@@@#############################
        
        return render(request, 'faculty/ml_model.html',context={
            "identified":l,
              "all_notices": total_objects,
                "inboxmsg": inboxmsg,
                "predlist":main_list,
                "classroom_name":select_class,
                "total_classes": total_class_obj
            })
        
    return render(request, 'faculty/ml_model.html',
                  context={
                        "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                       "total_classes": total_class_obj
                  })


"""
def ml_model(request):
    total_objects = Upload_Notices.objects.filter(
        faculty_name_notice=request.user.username).order_by('created_at')
    curruser = request.user.user_id
    inboxmsg = messages.objects.filter(receive=str(curruser)).order_by("-posted_at")
    if request.method == 'POST':
        if "picupload" in request.FILES:
            upload = request.FILES['picupload']
            #print("___"*20,upload.read())
        im = Image.open(upload)
        im.save("im.jpg")
        loaded_model = tf.keras.models.load_model('modelss/person_classifier_500.h5')
        # Load the detector
        detector = dlib.get_frontal_face_detector()
        # Load the predictor
        predictor = dlib.shape_predictor("modelss/shape_predictor_68_face_landmarks.dat")
        names=['Anand', 'Angel', 'BhargaviS', 'Devi', 'Dsrilakshmi', 'Falak', 'guravaya', 'Harshitha', 'Idris', 'jareen', 'Jessika', 'Jyothi', 'Khasim', 'lakshmiPrasanna', 'Mani', 'Moulichand', 'Mounika', 'Nagraju', 'neeraja', 'Pawan', 'Priyanka', 'sai', 'Sangeetha', 'Santhvana', 'Satya', 'Sirisha', 'Sowjanya', 'Sravani', 'Srilakshmi', 'sripavan', 'Swathi', 'Thanuja', 'Thrisali', 'VaraLakshmi', 'Vineela', 'Vineeth']
        ########
        # Load the image
        img = cv2.imread("im.jpg")
        #print("___"*20,os.getcwd())
        #print("___"*20,img.shape)

        # Convert image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces using HOG + Linear SVM detector
        faces = detector(gray, 1)

        # Create the "faces" directory if it doesn't exist
        if not os.path.exists("faces"):
            os.makedirs("faces")

        # Loop through all files in the directory and remove them
        for filename in os.listdir("faces"):
            file_path = os.path.join("faces", filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        l=[]
        # Iterate over each face
        predicted_persons = set()
        for i, face in enumerate(faces):
            # Get the landmarks/parts for the face in box d.
            landmarks = predictor(gray, face)

            # Extract face region as a numpy array
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            face_region = img[y1:y2, x1:x2]

            # Convert face region to grayscale
            face_gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
            test_img = cv2.imread(face_gray)
            test_img = cv2.resize(test_img, (img_size, img_size))
            test_img = np.array(test_img).reshape(-1, img_size, img_size, 3) / 255.0
            prediction = loaded_model.predict(test_img)
            person = names[np.argmax(prediction)]
            if person not in predicted_persons:
                    predicted_persons.add(person)
                    print("ID:", i, "  Person:", person)
                    l.append(str(person))
                    # Save the face region as a grayscale image in the "faces" directory
                    cv2.imwrite(f"faces/{i}.png", face_gray)
                    cv2.imwrite(f"media/faces/{i}.png", face_gray)
        # Destroy all windows
        cv2.destroyAllWindows()
        dir_path = 'faces/'
        


            # Output the name of the person
            #print("The person in the test image is:", person)
        #####@@@@@@@@@@@@@@@@@@@@@@@#############################
        return render(request, 'faculty/ml_model.html',context={
            "identified":l,
              "all_notices": total_objects,
                "inboxmsg": inboxmsg,
                "model_work":1,
            })
        
    return render(request, 'faculty/ml_model.html',
                  context={
                        "all_notices": total_objects,
                       "inboxmsg": inboxmsg,
                  })


dir_path = 'faces/'
c = 0
for filename in os.listdir("faces"):
    c += 1

# Create a set to store predicted persons
predicted_persons = set()

for i in range(c):
    test_img = cv2.imread('faces/' + str(i) + '.png')
    test_img = cv2.resize(test_img, (img_size, img_size))
    test_img = np.array(test_img).reshape(-1, img_size, img_size, 3) / 255.0

    # Predict the person in the test image using the loaded model
    prediction = loaded_model.predict(test_img)
    person = names[np.argmax(prediction)]

    # Check if the person has already been predicted
    if person not in predicted_persons:
        # Add the predicted person to the set
        predicted_persons.add(person)

        # Output the name and ID of the person
        print("ID:", i, "  Person:", person)

        # Display the image
"""