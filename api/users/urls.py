from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views
from users import views

app_name = 'users'

urlpatterns = [
    path('', views.UserListViewSet.as_view({'get': 'list', 'post': 'create'}), name='list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='detail'),
    path('<int:pk>/change-password/', views.ChangePasswordView.as_view(),
         name='change-password'),
    path('email-confirm/', views.EmailConfirmView.as_view(),
         name='email-confirm'),
    path('login/', jwt_views.TokenObtainPairView().as_view(), name='login'),
    path('login/refresh/', jwt_views.TokenRefreshView().as_view(),
         name='token-refresh'),
    path('password-reset/', views.PasswordReset.as_view(), name='password-reset'),
    path('password-reset-confirm/', views.PasswordResetConfirm.as_view(),
         name='password-reset-confirm')
]