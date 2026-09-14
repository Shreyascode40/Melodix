from django.urls import path
from .views import (
    PlaylistListCreateView,
    PlaylistDetailView,
    PlaylistAddSongView,
    PlaylistRemoveSongView,
    PlaylistReorderView,
    PlaylistDuplicateView,
)

urlpatterns = [
    path("", PlaylistListCreateView.as_view()),
    path("<int:pk>/", PlaylistDetailView.as_view()),
    path("<int:pk>/songs/", PlaylistAddSongView.as_view()),
    path("<int:pk>/songs/<int:song_id>/", PlaylistRemoveSongView.as_view()),
    path("<int:pk>/reorder/", PlaylistReorderView.as_view()),
    path("<int:pk>/duplicate/", PlaylistDuplicateView.as_view()),
]
