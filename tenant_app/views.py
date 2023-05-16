from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from django.views.generic import ListView, DetailView, CreateView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import View

from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.edit import FormMixin
from django.urls import reverse

from django.db.models import Prefetch, F, Q, Count, Sum, Min, When, Case, ExpressionWrapper, Func

from django.core import serializers
from django.contrib import messages
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.utils.timezone import localtime, now
from .models import *
from .forms import LoginUserForm
from .business_logic import check_mes
from django_htmx.http import HttpResponseClientRefresh


def ajax_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.META.get('HTTP_HX_REQUEST'):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request,'Данный адрес не используется')
            return redirect('/')
    return _wrapped_view

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'tenant_app/login.html'


def logout_user(request):
    logout(request)
    return redirect('login')


class MainPage(LoginRequiredMixin, ListView):
    model = User
    template_name = 'tenant_app/main_page.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        messages = Message.objects.filter(Q(recipients = self.request.user) & Q(active=True)).order_by('-date_sent').distinct()
        messages = messages.filter(Q(mesin_message__active = True)
                                    & Q(mesin_message__user = self.request.user))
        users = User.objects.all()
        mailing_list = MailingList.objects.all()
        context = {'messages': messages,'users': users, 'mailing_list': mailing_list}
        return context

@ajax_required
def users(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'tenant_app/users.html', context)


@ajax_required
def get_email_text(request,pk):
    try:
        context = {'message': Message.objects.get(id=pk)}
        return render(request, 'tenant_app/detail_mes.html', context)
    except Message.DoesNotExist:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    
@ajax_required
def in_messages(request):
    messages = Message.objects.filter(Q(recipients = request.user) & Q(active = True)).order_by('-date_sent').distinct()
    messages = messages.filter(Q(mesin_message__active = True)
                                    & Q(mesin_message__user = request.user))
    context = {'messages': messages}
    return render(request, 'tenant_app/in_messages.html', context)


@ajax_required
def out_messages(request):
    messages = Message.objects.filter(Q(sender = request.user) & Q(active = True)).distinct()
    context = {'messages': messages}
    return render(request, 'tenant_app/out_messages.html', context)

@ajax_required
def del_messages(request):
    messages = Message.objects.filter(Q(recipients = request.user) & Q(active = True)).order_by('-date_sent').distinct()
    messages = messages.filter(Q(mesin_message__active = False)
                                    & Q(mesin_message__user = request.user))
    context = {'messages': messages}
    return render(request, 'tenant_app/del_messages.html', context)



@ajax_required
def send_mes(request):
    users = User.objects.all()
    mailing_list = MailingList.objects.all()
    context = {'users': users, 'mailing_list': mailing_list}
    return render(request, 'tenant_app/send_mes.html', context)




def submit_mail(request):
    if request.method == 'POST':

        if not request.user.is_superuser:
            messages.error*(request, 'У вас недостаточно прав!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if all(field in request.POST for field in ['subject', 'mail_text','mail_list']):
            mes_code = check_mes(request)
            if not mes_code[0]:
                messages.success(request, "Сообщение отправлено!")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Произошла ошибка!')
        
    return redirect ('home')



@ajax_required
def filter_email(request):
    filter_text = request.POST.get('search')
    messages = Message.objects.filter(Q(recipients = request.user) & Q(subject__iregex=filter_text)
                                      | Q(message__iregex=filter_text)
                                      |Q(recipients__email__iregex=filter_text)
                                      & Q(active = True)).distinct()
    
    messages = messages.filter(Q(mesin_message__active = True)
                                    & Q(mesin_message__user = request.user))

    return render(request, 'tenant_app/email_list.html', {'messages': messages})


@ajax_required
def filter_out_email(request):
    filter_text = request.POST.get('search')
    messages = Message.objects.filter(Q(sender = request.user) & Q(subject__iregex=filter_text)
                                      | Q(message__iregex=filter_text)
                                      |Q(recipients__email__iregex=filter_text)
                                      & Q(active = True)).distinct()
    messages = messages.filter(sender = request.user, active = True)
    return render(request, 'tenant_app/email_list_out.html', {'messages': messages})


def del_mes(request):
    if request.POST:
        mes_del = request.POST.getlist('mes_id')
        
    for mes in mes_del:
        try:
            int(mes)
            try:
                d = MesIn.objects.get(Q(message__id = int(mes)) & Q(user=request.user))
                
                d.active = False
                d.save()
                
            except MesIn.DoesNotExist:
                messages.error(request, 'Произошла ошибка!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except ValueError:
            messages.error(request, 'Произошла ошибка!')
            print("Ошибка: элемент содержит символы")
                
    message = Message.objects.filter(recipients = request.user).order_by('-date_sent').distinct()
    message = message.filter(mesin_message__active = True)
    messages.success(request,'Сообщение удалено!')
    context = {'messages': message}
    return redirect('home')




def del_full_mes(request):
    if request.POST:
        mes_del = request.POST.getlist('mes_id')
    res = True
    for mes in mes_del:
        try:
            int(mes)
            try:
                d = Message.objects.get(pk = int(mes))
                d.active = False
                d.save()
            except Message.DoesNotExist:
                messages.error(request, 'Произошла ошибка!')
                messages = Message.objects.filter(Q(sender = request.user) & Q(active = True)).distinct()
                return render(request, 'tenant_app/email_list.html', {'messages': messages})
        except ValueError:
            messages.error(request, 'Произошла ошибка!')
            messages = Message.objects.filter(Q(sender = request.user) & Q(active = True)).distinct()
            return render(request, 'tenant_app/email_list.html', {'messages': messages})
    messages.success(request, 'Произошла ошибка!')           
    messages = Message.objects.filter(Q(sender = request.user) & Q(active = True)).distinct()
    return render(request, 'tenant_app/email_list.html', {'messages': messages})

@ajax_required
def del_user(request,pk):
    try:
        User.objects.get(id=pk).delete()
        messages.success(request,'Пользователь удален!')
        return render(request, 'tenant_app/user_list.html', {'users': User.objects.all()})
    except User.DoesNotExist:
        messages.error(request,'Ошибка!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def mas_del_user(request):
    if request.POST:
        mes_del = request.POST.getlist('mes_id')
        
        for mes in mes_del:
            try:
                try:
                    deluser = User.objects.get(pk = int(mes)).delete() if request.user.pk != int(mes) else None
                    
                    if not deluser:
                        messages.error(request, 'Вы не можете удалить сами себя!')
                        return render(request, 'tenant_app/user_list.html', {'users': User.objects.all()})
                except User.DoesNotExist:
                    messages.error(request, 'Произошла ошибка!')
                    return render(request, 'tenant_app/user_list.html', {'users': User.objects.all()})
            except ValueError:
                messages.error(request, 'Произошла ошибка!')
                return render(request, 'tenant_app/user_list.html', {'users': User.objects.all()})
    messages.success(request,'Пользователи удалены!')                
    return render(request, 'tenant_app/user_list.html', {'users': User.objects.all()})

def filter_users(request):
    filter_text = request.POST.get('search')
    users = User.objects.filter(Q(email__iregex=filter_text)
                                      | Q(first_name__iregex=filter_text)).distinct()

    return render(request, 'tenant_app/user_list.html', {'users': users})

@ajax_required
def change_user(request):
    if request.POST:
        user_id= int(request.POST['user_id'])
        username = request.POST['username']
        user_mail = request.POST['email']
        user_password = request.POST['password']
        user_confirm_pass = request.POST['confirmpassword']

        staff = request.POST.get('superstatus', False)

        staff = True if staff == '' else False

        if user_password == user_confirm_pass:
            if not User.objects.filter(id=user_id).exists():
                if user_id == 0:    
                    user = User(
                            first_name=username,
                            is_staff=staff,
                            # is_superuser=is_superuser,
                            email = user_mail,
                            
                        )
                    
                    if user_password != '':
                        user.set_password('user_password')
                        user.save()
                        messages.success(request,'Пользователь создан!')
                    else:
                        messages.error(request,'Произошла ошибка!')
                        
                else:
                    messages.error(request,'Произошла ошибка!')

            else:
                user = User.objects.get(id=user_id)
                user.first_name = user.first_name if user.first_name == username else username
                user.email = user.email if user.email == user_mail else user_mail
                if user_password != '':
                    user.set_password(user_password)
                user.is_staff = staff if request.user != user else request.user.is_staff
                user.save()
                
        else:
            messages.error(request,'Пароли не совпадают!')
            
    return render(request, 'tenant_app/user_list.html', {'users': User.objects.all()})