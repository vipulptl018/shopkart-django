from django.urls import path
from . import views
from .views import register,login,logout


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashbord/', views.dashbord, name="dashbord"),
    path('', views.dashbord, name="dashbord"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/',views.forgotPassword, name="forgotPassword"),
    path('restPassword_validation/<uidb64>/<token>/',views.restPassword_validation, name="restPassword_validation"),
    path('reset_password/',views.restPassword, name="reset_password"),


]