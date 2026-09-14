from django.urls import path
from .views import SearchView, TrendingView, TrackDetailView, ResolveSongView

urlpatterns = [
    path("search/", SearchView.as_view()),
    path("trending/", TrendingView.as_view()),
    path("resolve/", ResolveSongView.as_view()),
    path("track/<str:provider>/<str:track_id>/", TrackDetailView.as_view()),
]
