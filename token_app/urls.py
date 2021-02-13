from django.urls import path
from . import views

urlpatterns = [
    path('generate_token/', views.generate_token, name='generate token'),
    path('assign_token/<int:user_id>', views.assign_token, name='assign token'),
    path('delete_token/<str:token>', views.delete_token, name='delete token'),
    path('unblock_token/<str:token>', views.unblock_token, name='unblock token'),
    path('refresh_token/<str:token>', views.refresh_token, name='refresh token'),
    path('refresh_user_token/<int:user_id>/<str:token>', views.unblock_token, name='unblock token'),
    ]