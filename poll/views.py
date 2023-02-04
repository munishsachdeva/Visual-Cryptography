import os
import ssl
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from multicolorcaptcha import CaptchaGenerator
import numpy as np
from numpy import asarray
from PIL import Image
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponseRedirect
from .forms import RegistrationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .models import Candidate,ControlVote,Position,Captcha
from .forms import *
from django.core.files.storage import FileSystemStorage
from django.utils.functional import SimpleLazyObject

def homeView(request):
    return render(request, "poll/home.html")

def registrationView(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            if cd['password'] == cd['confirm_password']:
                obj = form.save(commit=False)
                obj.set_password(obj.password)
                
                CAPCTHA_SIZE_NUM = 4
                generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)
                captcha = generator.gen_captcha_image(difficult_level=2)
                image = captcha.image
                characters = captcha.characters
                image.save("captcha.png", "png")
                with open('captcha.png', 'rb') as f:
                    m=f.read()
                temp = Captcha()
                temp.voter = cd['username']
                temp.image = m

                #image.save("captcha.png", "png")
                
                share_size = 2
                input_image = Image.open('captcha.png')
                image1 = np.asarray(input_image)
                (row, column, depth) = image1.shape
                shares = np.random.randint(0, 256, size=(row, column, depth, share_size))
                shares[:,:,:,-1] = image1.copy()
                for i in range(share_size-1):
                    shares[:,:,:,-1] = shares[:,:,:,-1] ^ shares[:,:,:,i]

                for ind in range(share_size):
                    input_array = shares[:,:,:,ind].astype(np.uint8)
                    image2 = Image.fromarray(input_array)
                    name = "Share_" + str(ind+1) + ".png"
                    if ind == 0:
                        #np.save("shares_out" + str(ind+1) + ".npy", input_array)
                        image2.save(name)
                        # with open(name, 'rb') as f:
                        #     m=f.read()
                        # temp.share_2 = m
                        email_id = #"your mail account"
                        email_passwd = #"access key"
                        message = MIMEMultipart()
                        message['Subject'] = "Plain message to user"
                        message['From'] = email_id
                        message['To'] = form.cleaned_data['email']
                        message_ready = MIMEText('Your Share', 'plain')
                        image_open = open(name, 'rb').read()
                        image_ready = MIMEImage(image_open, 'png', name=name)
                        message.attach(message_ready)
                        message.attach(image_ready)
                        context_data = ssl.create_default_context()
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465,context=context_data) as mail:
                            mail.login(email_id, email_passwd)
                            mail.send_message(message)
                        os.remove(name)
                        #save captcha.png to backend
                    if ind == 1:
                        #np.save("shares_out" + str(ind+1) + ".npy", input_array)
                        image2.save(name)
                        with open(name, 'rb') as f:
                            m=f.read()
                        temp.share_2 = m
                temp.save()

                obj.save()
                messages.success(request, 'You have been registered. An Email has been sent to your mail id')
                return redirect('home')
            else:
                return render(request, "poll/registration.html", {'form':form,'note':'password must match'})
    else:
        form = RegistrationForm()

    return render(request, "poll/registration.html", {'form':form})

def loginView(request):
    if request.method == "POST":
        usern = request.POST.get('username')
        passw = request.POST.get('password')
        user = authenticate(request, username=usern, password=passw)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.success(request, 'Invalid username or password!')
            return render(request, "poll/login.html")
    else:
        return render(request, "poll/login.html")


@login_required
def logoutView(request):
    logout(request)
    return redirect('home')

@login_required
def dashboardView(request):
    return render(request, "poll/dashboard.html")

@login_required
def positionView(request):
    obj = Position.objects.all()
    return render(request, "poll/position.html", {'obj':obj})

@login_required
def candidateView(request, pos):
    obj = get_object_or_404(Position, pk = pos)
    if request.method == "POST" and request.FILES['upload']:
        try:
            upload = request.FILES['upload']
        except:
            upload = None
        
        # if upload == None:
        #     messages.error(request, 'Please upload Share for Verification')
        #     return render(request, 'poll/error.html')
 
        if not upload == None:
            try:
                img1 = Image.open(upload)
                numpydata1 = asarray(img1)
            except:
                messages.error(request, 'Sorry, your image is invalid')
                return render(request, 'poll/error.html')
        # fss = FileSystemStorage()
        # file = fss.save(upload.name, upload)
        #file_url = fss.url(file)
        #file.save()

        # img1 = Image.open(upload)
        # numpydata1 = asarray(img1)

        img2 = Image.open('/home/kali/Desktop/ovs2/Share_2.png')

        numpydata2 = asarray(img2)

        data1 = numpydata1
        data2 = numpydata2

        share_size = 2
        input_image = Image.open('/home/kali/Desktop/ovs2/captcha.png')
        image = np.asarray(input_image)
        (row, column, depth) = image.shape
        shares = np.random.randint(0, 256, size=(row, column, depth, share_size))
        shares[:,:,:,-1] = image.copy()
        new_var = shares[:,:,:,-1]

        final_output = (data1 ^ data2)
        temp = ControlVote.objects.get_or_create(user=request.user, position=obj)[0]
        
        if np.array_equal(final_output, new_var) == True and temp.status == False:
        # temp = ControlVote.objects.get_or_create(user=request.user, position=obj)[0]
        # if temp.status == False:
            temp2 = Candidate.objects.get(pk=request.POST.get(obj.title))
            temp2.total_vote += 1
            temp2.save()
            temp.status = True
            temp.save()
            # output_image = Image.fromarray(final_output.astype(np.uint8))
            # output_image.save('Output.png')

            # messages.success(request, 'Thank you for Voting!')
            # return render(request, 'poll/position.html')
            return HttpResponseRedirect('/position/')

        else:
            messages.success(request, 'You have already been voted this position.')
            return render(request, 'poll/candidate.html', {'obj':obj})
    else:
        return render(request, 'poll/candidate.html', {'obj':obj})

@login_required
def resultView(request):
    obj = Candidate.objects.all().order_by('position','-total_vote')
    return render(request, "poll/result.html", {'obj':obj})

@login_required
def candidateDetailView(request, id):
    obj = get_object_or_404(Candidate, pk=id)
    return render(request, "poll/candidate_detail.html", {'obj':obj})


@login_required
def changePasswordView(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request,form.user)
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "poll/password.html", {'form':form})


@login_required
def editProfileView(request):
    if request.method == "POST":
        form = ChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ChangeForm(instance=request.user)
    return render(request, "poll/edit_profile.html", {'form':form})
