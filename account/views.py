from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from account.models import User, UserProfile,MateriaDadas, Materia, Carrera, Periods
from account.form import LoginForm, RegistrationForm, RegistrationFormC
from django.contrib.auth import login , logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q

# Create your views here.

#Authenticated
def login_v(request): #Log in View
    msg=''
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        if request.method=="POST":
            form=LoginForm(request.POST)
            if form.is_valid():
                email=form.cleaned_data['email']
                password=form.cleaned_data['password']
                auth_user=authenticate(email=email,password=password)
                if auth_user is not None and auth_user.is_active:
                    login(request,auth_user)
                    return redirect('/dash')
                else:
                    msg='Wrong Email and password combination.'
        form=LoginForm()
        ctx={'form':form,'mensaje':msg}
        return render_to_response('login.html',ctx, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def logout_v(request):
    logout(request)
    return redirect('/')

#Registration
def sign_up(request):
    msg=''
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        if request.method=="POST":
            form = RegistrationForm(request.POST)
            if form.is_valid():
                name=form.cleaned_data['name']
                lastname=form.cleaned_data['lastname']
                email=form.cleaned_data['email']
                password=form.cleaned_data['password']
                carrera = form.cleaned_data['carrera']
                new_u=User.objects.create_user(username= email, email= email, password=password)
                new_u.first_name=name
                new_u.last_name=lastname
                new_u.save()
                new_user = authenticate(email=email,password=password)
                if new_user is not None :
                    login(request,new_user)
                    new_p=UserProfile.objects.create(user=new_u,carrera=carrera)
                    new_p.save()
                    return redirect('/dash')
                else:
                    msg='Wrong'

        ctx={'form':RegistrationForm,'msg':msg}
        return render_to_response('signup.html',ctx, context_instance=RequestContext(request))

@login_required(login_url='/login/')
def sigup_complete (request):
    error=""
    user=UserProfile.objects.get(user=request.user)
    form = RegistrationFormC()
    q=Carrera.objects.get(id=user.carrera_id).materias.all().filter(Q(id="ELE") |Q(prerequsito=None) |Q(prerequsito__in=MateriaDadas.objects.filter(user=user).values_list('materia',flat=True))).exclude(Q(id__in=MateriaDadas.objects.filter(user=user).values_list('materia',flat=True)) & ~Q(id__in=Materia.objects.filter(id="ELE"))).exclude(id__in=Materia.objects.filter(creditoRequsito__gt=user.get_credito_apobado()))
    form.fields['materias'].queryset = q
    if request.method=="POST":
        form=RegistrationFormC(request.POST)
        if form.is_valid():
            materias=form.cleaned_data['materias'].all()
            credit=0
            p=Periods.objects.create(user=user)
            tm=[]
            for m in materias:
                credit=m.credito
                if credit > Carrera.objects.get(id=user.carrera_id).max_credits:
                    error="You have exceeded the number of credits %s credits per period of the career" % (Carrera.objects.get(id=UserProfile.objects.get(user=1).carrera_id).max_credits())
                    return render_to_response('signup_c.html',ctx, context_instance=RequestContext(request))
                else:
                    ls=MateriaDadas.objects.create(user=UserProfile.objects.get(user=request.user),materia=m)

                    ls.aprobada=True
                    ls.save()
                    tm.append(ls.id)
                    p.materia.add(ls)
            p.num=user.get_Total_Trimestre()
            p.credito=credit
            p.save()
            return redirect("/")
    ctx={'form':form,'error':error}
    return render_to_response('signup_c.html',ctx, context_instance=RequestContext(request))
