from django.urls import path
from . import views

urlpatterns = [
    path("get_video_id", views.get_YT_TS),
    path("embedding_to_pinecone", views.creating_embedding),
    path("make_embedding", views.make_embedding),
]
