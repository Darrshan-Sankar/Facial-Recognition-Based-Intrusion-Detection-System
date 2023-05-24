from django.urls import path
from . import views
from .views import candidate_list

urlpatterns = [
    path('', views.candidate_form, name='candidate_form'),
    path('success/', views.success, name='success'),
    path('candidates/', candidate_list, name='candidate_list'),
    path('delete_candidate/', views.delete_candidate, name='delete_candidate'),
    path('webcam_feed/', views.webcam_feed, name='webcam_feed'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('detections/', views.detection_list, name='detection_list'),
]