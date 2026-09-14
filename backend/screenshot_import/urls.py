from django.urls import path
from .views import ScreenshotAnalyzeView, ScreenshotConfirmView

urlpatterns = [
    path("analyze/", ScreenshotAnalyzeView.as_view()),
    path("confirm/", ScreenshotConfirmView.as_view()),
]
