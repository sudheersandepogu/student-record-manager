from django.urls import path
from . import views

urlpatterns = [
    # Main template page
    path('', views.index, name='index'),
    
    # APIs
    path('api/add-student/', views.add_student, name='add_student'),
    path('api/students/', views.get_students, name='get_students'),
    path('api/delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('api/search-student/', views.search_student, name='search_student'),
]
