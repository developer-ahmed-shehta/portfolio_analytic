from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('download-cv/', download_cv, name='download_cv'),

    path('send_message/', send_message, name='send_message'),

]