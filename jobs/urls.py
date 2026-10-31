from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Dashboard & Job List (Hierarchy overview with filter by Date, Buyer, Order)
    path('', views.job_list, name='job_list'),

    # Job CRUD
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),

    # Order Items CRUD (Children under Job)
    path('jobs/<int:job_pk>/orders/add/', views.order_create, name='order_create'),
    path('orders/<int:pk>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),

    # One-click realistic apparel sample data loader
    path('seed-data/', views.seed_data, name='seed_data'),
]

