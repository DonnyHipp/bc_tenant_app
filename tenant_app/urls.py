from django.template.defaulttags import url
from django.urls import path, include
from .import views
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', MainPage.as_view(), name='home'),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('users', users, name='users'),
    path('in_messages', in_messages, name='inmes'),
    path('out_messages', out_messages, name='outmes'),

    path('send_mes', send_mes, name='send_mes'),
    path('subm_mail', submit_mail, name='subm_mail'),
    path('get_email_text/<int:pk>/', get_email_text, name='get_email_text'),
    path('filter_email', filter_email, name='filter_email'),
    path('filter_out_email', filter_out_email, name='filter_out_email'),
    path('del_mes', del_mes, name='del_mes'),
    path('del_full_mes', del_full_mes, name='del_full_mes'),
    path('del_user/<int:pk>/', del_user, name='del_user'),
    path('mduser', mas_del_user, name='mduser'),
    path('filter_users', filter_users,name='filter_users'),
    path('change_user/', change_user, name='change_user'),

]
