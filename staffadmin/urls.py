from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="staff_dashboard"),
    path("events/<int:event_id>/upload/", views.upload_results, name="staff_upload_results"),
    path("events/<int:event_id>/upload-image/", views.ajax_process_image, name="staff_ajax_process_image"),
    path("skaters/", views.skater_list, name="staff_skater_list"),
    path("skater/<int:skater_id>/<int:scheduled_id>/edit/", views.edit_skater, name="staff_edit_skater"),
]
