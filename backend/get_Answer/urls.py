from django.urls import path
from . import views

urlpatterns = [
    path("get_answer", views.get_answer, name="answers"),
]
