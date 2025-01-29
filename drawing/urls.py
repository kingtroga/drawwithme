from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_artwork, name='create_artwork'),
    path('edit/<int:pk>/', views.edit_artwork, name='edit_artwork'),
    path('save/', views.save_artwork, name='save_artwork'),
    path('collaborate/<int:pk>/', views.collaborate_artwork, name='collaborative_artwork'),
    path('<int:pk>/', views.artwork_detail, name='artwork_detail',),
    path('<int:pk>/delete/', views.delete_artwork, name='delete_artwork'),
]