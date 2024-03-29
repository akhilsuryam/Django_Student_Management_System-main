import datetime
from django import forms
from django.forms import ChoiceField

from student_management_app.models import Courses, SessionYearModel, Subjects, Students
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from student_management_app.models import Students, Courses, Subjects, CustomUser, Attendance, AttendanceReport, \
    LeaveReportStudent, FeedBackStudent, NotificationStudent, StudentResult, OnlineClassRoom, SessionYearModel,feedbackform


def student_home(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present=AttendanceReport.objects.filter(student_id=student_obj,status=True).count()
    attendance_absent=AttendanceReport.objects.filter(student_id=student_obj,status=False).count()
    course=Courses.objects.get(id=student_obj.course_id.id)
    subjects=Subjects.objects.filter(course_id=course).count()
    subjects_data=Subjects.objects.filter(course_id=course)
    session_obj=SessionYearModel.object.get(id=student_obj.session_year_id.id)
    class_room=OnlineClassRoom.objects.filter(subject__in=subjects_data,is_active=True,session_years=session_obj)

    subject_name=[]
    data_present=[]
    data_absent=[]
    subject_data=Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=True,student_id=student_obj.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(attendance_id__in=attendance,status=False,student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    return render(request,"student_template/student_home_template.html",{"total_attendance":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent,"class_room":class_room})

# def add_subject(request):
#     courses=Courses.objects.all()
#     staffs=CustomUser.objects.filter(user_type=2)
#     return render(request,"student_template/feedbackform.html",{"staffs":staffs,"courses":courses})

def add_feedback(request):
    form=AddfeedbackForm()
    return render(request,"student_template/feedbackform.html",{"form":form})

def add_feedback_save(request):
    if request.method!="POST":
        return HttpResponse("Method Not Allowed")
    else:
        form=AddfeedbackForm(request.POST,request.FILES)
        if form.is_valid():
            Acheivements=form.cleaned_data["Acheivements"]
            Internships=form.cleaned_data["Internships"]
            Certificates=form.cleaned_data["Certificates"]
            Participations=form.cleaned_data["Participations"]
            CollegeExperience=form.cleaned_data["CollegeExperience"]
            
            # address=form.cleaned_data["address"]
            # username=form.cleaned_data["username"]
            
            # session_year_id=form.cleaned_data["session_year_id"]
            # course_id=form.cleaned_data["course"]
            # sex=form.cleaned_data["sex"]

            # profile_pic=request.FILES['profile_pic']
            # fs=FileSystemStorage()
            # filename=fs.save(profile_pic.name,profile_pic)
            # profile_pic_url=fs.url(filename)
            student_obj=Students.objects.get(admin=request.user.id)

            try:
                # user=CustomUser.objects.get(id=request.user.id) 
                # user.feedbackform.acheivements=Acheivements
                # user.feedbackform.internships=Internships
                # user.feedbackform.certificates=Certificates
                # user.feedbackform.participations=Participations
                # user.feedbackform.collegeexperience=CollegeExperience
                
                # course_obj=Courses.objects.get(id=course_id)
                # user.students.course_id=course_obj
                # session_year=SessionYearModel.object.get(id=session_year_id)
                # user.students.session_year_id=session_year
                # user.students.gender=sex
                # user.students.profile_pic=profile_pic_url
                # user =user.objects
                
                user= feedbackform(student_id=student_obj,acheivements=Acheivements)
                user.save()
                messages.success(request,"Successfully Added Student")
                return HttpResponseRedirect(reverse("add_student"))
            except:
                messages.error(request,"Failed to Add Student")
                return HttpResponseRedirect(reverse("add_student"))
        else:
            form=AddfeedbackForm(request.POST)
            return render(request, "student_template/feedbackform.html", {"form": form})


def join_class_room(request,subject_id,session_year_id):
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    subjects=Subjects.objects.filter(id=subject_id)
    if subjects.exists():
        session=SessionYearModel.object.filter(id=session_year_obj.id)
        if session.exists():
            subject_obj=Subjects.objects.get(id=subject_id)
            course=Courses.objects.get(id=subject_obj.course_id.id)
            check_course=Students.objects.filter(admin=request.user.id,course_id=course.id)
            if check_course.exists():
                session_check=Students.objects.filter(admin=request.user.id,session_year_id=session_year_obj.id)
                if session_check.exists():
                    onlineclass=OnlineClassRoom.objects.get(session_years=session_year_id,subject=subject_id)
                    return render(request,"student_template/join_class_room_start.html",{"username":request.user.username,"password":onlineclass.room_pwd,"roomid":onlineclass.room_name})

                else:
                    return HttpResponse("This Online Session is Not For You")
            else:
                return HttpResponse("This Subject is Not For You")
        else:
            return HttpResponse("Session Year Not Found")
    else:
        return HttpResponse("Subject Not Found")


def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
    course=student.course_id
    subjects=Subjects.objects.filter(course_id=course)
    return render(request,"student_template/student_view_attendance.html",{"subjects":subjects})

def student_view_attendance_post(request):
    subject_id=request.POST.get("subject")
    start_date=request.POST.get("start_date")
    end_date=request.POST.get("end_date")

    start_data_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    end_data_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    subject_obj=Subjects.objects.get(id=subject_id)
    user_object=CustomUser.objects.get(id=request.user.id)
    stud_obj=Students.objects.get(admin=user_object)

    attendance=Attendance.objects.filter(attendance_date__range=(start_data_parse,end_data_parse),subject_id=subject_obj)
    attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)
    return render(request,"student_template/student_attendance_data.html",{"attendance_reports":attendance_reports})

def student_apply_leave(request):
    staff_obj = Students.objects.get(admin=request.user.id)
    leave_data=LeaveReportStudent.objects.filter(student_id=staff_obj)
    return render(request,"student_template/student_apply_leave.html",{"leave_data":leave_data})

def student_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStudent(student_id=student_obj,leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))
        except:
            messages.error(request, "Failed To Apply for Leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))


def student_feedback(request):
    staff_id=Students.objects.get(admin=request.user.id)
    feedback_data=FeedBackStudent.objects.filter(student_id=staff_id)
    return render(request,"student_template/student_feedback.html",{"feedback_data":feedback_data})

def student_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStudent(student_id=student_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("student_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("student_feedback"))

# class AddStudentForm(forms.Form):
#     email=forms.EmailField(label="Email99",max_length=50,widget=forms.EmailInput(attrs={"class":"form-control","autocomplete":"off"}))
#     password=forms.CharField(label="Password",max_length=50,widget=forms.PasswordInput(attrs={"class":"form-control"}))
#     first_name=forms.CharField(label="First Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     last_name=forms.CharField(label="Last Name",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     username=forms.CharField(label="Username",max_length=50,widget=forms.TextInput(attrs={"class":"form-control","autocomplete":"off"}))
#     address=forms.CharField(label="Address",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
#     course_list=[]
#     try:
#         courses=Courses.objects.all()
#         for course in courses:
#             small_course=(course.id,course.course_name)
#             course_list.append(small_course)
#     except:
#         course_list=[]
#     #course_list=[]

#     session_list = []
#     try:
#         sessions = SessionYearModel.object.all()

#         for ses in sessions:
#             small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
#             session_list.append(small_ses)
#     except:
#         session_list=[]

#     gender_choice=(
#         ("Male","Male"),
#         ("Female","Female")
#     )

#     course=forms.ChoiceField(label="Course",choices=course_list,widget=forms.Select(attrs={"class":"form-control"}))
#     sex=forms.ChoiceField(label="Sex",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
#     session_year_id=forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
#     profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}))            

class AddfeedbackForm(forms.Form):
    Acheivements=forms.CharField(label="Acheivements",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    Internships=forms.CharField(label="Internships",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    Certificates=forms.CharField(label="Certificates",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    Participations=forms.CharField(label="Participations",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    CollegeExperience=forms.CharField(label="CollegeExperience",max_length=50,widget=forms.TextInput(attrs={"class":"form-control","autocomplete":"off"}))
    # username=forms.CharField(label="username",max_length=50,widget=forms.TextInput(attrs={"class":"form-control"}))
    # course_list=[]
    # try:
    #     courses=Courses.objects.all()
    #     for course in courses:
    #         small_course=(course.id,course.course_name)
    #         course_list.append(small_course)
    # except:
    #     course_list=[]
    # #course_list=[]

    # session_list = []
    # try:
    #     sessions = SessionYearModel.object.all()

    #     for ses in sessions:
    #         small_ses = (ses.id, str(ses.session_start_year)+"   TO  "+str(ses.session_end_year))
    #         session_list.append(small_ses)
    # except:
    #     session_list=[]

    # gender_choice=(
    #     ("Male","Male"),
    #     ("Female","Female")
    # )

    # course=forms.ChoiceField(label="Course",choices=course_list,widget=forms.Select(attrs={"class":"form-control"}))
    # sex=forms.ChoiceField(label="Sex",choices=gender_choice,widget=forms.Select(attrs={"class":"form-control"}))
    # session_year_id=forms.ChoiceField(label="Session Year",choices=session_list,widget=forms.Select(attrs={"class":"form-control"}))
    # profile_pic=forms.FileField(label="Profile Pic",max_length=50,widget=forms.FileInput(attrs={"class":"form-control"}))            

def student_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    return render(request,"student_template/student_profile.html",{"user":user,"student":student})

def student_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            student=Students.objects.get(admin=customuser)
            student.address=address
            student.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("student_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("student_profile"))

@csrf_exempt
def student_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        student=Students.objects.get(admin=request.user.id)
        student.fcm_token=token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def student_all_notification(request):
    student=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student.id)
    return render(request,"student_template/all_notification.html",{"notifications":notifications})

def student_view_result(request):
    student=Students.objects.get(admin=request.user.id)
    studentresult=StudentResult.objects.filter(student_id=student.id)
    return render(request,"student_template/student_result.html",{"studentresult":studentresult})