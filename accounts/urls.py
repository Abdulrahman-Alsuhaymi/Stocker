from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.log_out, name="log_out"),
    path('profile/', views.profile_view, name="profile"),
    path('profile/update/', views.profile_update_view, name="update_user_profile")
]