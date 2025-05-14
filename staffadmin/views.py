from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ResultUploadForm, SkaterEditForm
from core.models import Event, ScheduledSkater, Skater
from .image_utils import detect_and_crop_document
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid


def dashboard(request):
    events = Event.objects.order_by("date", "eventNumber")
    return render(request, "staffadmin/dashboard.html", {"events": events})


def upload_results(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    skaters = ScheduledSkater.objects.filter(event=event).select_related('skater__club')

    if request.method == "POST":
        image_type = request.POST.get("selected_image_type")
        uid = request.POST.get("uploaded_key")

        if image_type and uid:
            base = f"temp/{uid}"
            selected_file = f"{base}_cropped.jpg" if image_type == "processed" else f"{base}.jpg"
            try:
                with default_storage.open(selected_file, "rb") as f:
                    event.result_image.save(f"results/{uuid.uuid4()}.jpg", f)
                    event.status = "finished"
                    event.save()
                    messages.success(request, "Image uploaded and event marked as finished.")
            except Exception as e:
                messages.error(request, f"Failed to save image: {str(e)}")
            return redirect("staff_upload_results", event_id=event_id)

    form = ResultUploadForm()
    return render(request, "staffadmin/upload_results.html", {
        "event": event,
        "form": form,
        "scheduled_skaters": skaters
    })


@csrf_exempt
def ajax_process_image(request, event_id):
    if request.method == "POST" and request.FILES.get("image"):
        original = request.FILES["image"]
        uid = uuid.uuid4().hex
        orig_filename = f"temp/{uid}.jpg"
        cropped_filename = f"temp/{uid}_cropped.jpg"

        saved_path = default_storage.save(orig_filename, original)
        with default_storage.open(saved_path, 'rb') as f:
            cropped_file = detect_and_crop_document(f)
            cropped_io = ContentFile(cropped_file.read())
            default_storage.save(cropped_filename, cropped_io)

        return JsonResponse({
            "original": default_storage.url(orig_filename),
            "processed": default_storage.url(cropped_filename),
            "uid": uid
        })
    return JsonResponse({"error": "Invalid request"}, status=400)


def skater_list(request):
    skaters = Skater.objects.select_related("club").order_by("lastName", "firstName")
    return render(request, "staffadmin/skater_list.html", {"skaters": skaters})


def edit_skater(request, skater_id, scheduled_id):
    scheduled = get_object_or_404(ScheduledSkater, pk=scheduled_id)
    form = SkaterEditForm(request.POST or None, instance=scheduled.skater)
    if form.is_valid():
        form.save()
        return redirect("staff_upload_results", event_id=scheduled.event.id)
    return render(request, "staffadmin/edit_skater.html", {"form": form, "scheduled": scheduled})
