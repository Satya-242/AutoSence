from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cars/", views.car_list, name="car_list"),
    path("cars/<int:pk>/", views.car_detail, name="car_detail"),
    path("cars/<int:pk>/buy/", views.purchase_view, name="purchase"),
    path("upload/", views.upload_car, name="upload_car"),
    path("my-listings/", views.my_listings, name="my_listings"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/", views.customer_dashboard, name="customer_dashboard"),

    # Admin moderation
    path("cars/<int:pk>/approve/", views.approve_car, name="approve_car"),
    path("cars/<int:pk>/reject/", views.reject_car, name="reject_car"),
    path("cars/<int:pk>/edit/", views.edit_car, name="edit_car"),
    path("cars/<int:pk>/delete/", views.delete_car, name="delete_car"),

    # Auth
    path("signup/", views.signup_view, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Prediction
    path("predict/", views.predict_view, name="predict"),

    # API
    path("api/cars/", views.api_cars, name="api_cars"),
    path("api/cars/pending/", views.api_cars_pending, name="api_cars_pending"),
    path("api/stats/", views.api_stats, name="api_stats"),
    path("api/my-cars/", views.api_my_cars, name="api_my_cars"),
    path("api/cars/<int:pk>/approve/", views.api_car_approve, name="api_car_approve"),
    path("api/cars/<int:pk>/reject/", views.api_car_reject, name="api_car_reject"),
    path("api/cars/<int:pk>/purchase/", views.api_purchase, name="api_purchase"),

    # Notification URLs
    path('notifications/', views.all_notifications, name='all_notifications'),
    path('api/notifications/unread/', views.get_unread_notifications, name='unread_notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]
