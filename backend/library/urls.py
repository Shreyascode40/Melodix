from django.urls import path
from .views import LikeView, UnlikeView, LikedListView, RecentListView, RecordPlayView

urlpatterns = [
    path("like/", LikeView.as_view()),
    path("unlike/", UnlikeView.as_view()),
    path("unlike/<int:song_id>/", UnlikeView.as_view()),
    path("liked/", LikedListView.as_view()),
    path("recent/", RecentListView.as_view()),
    path("play/", RecordPlayView.as_view()),
]
