from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("documents/<int:pk>/delete/", views.delete_document, name="delete_document"),
    path("api/ask", views.api_ask, name="api_ask"),
]
