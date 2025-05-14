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
    event   = get_object_or_404(Event, pk=event_id)
    skaters = ScheduledSkater.objects.filter(event=event).select_related('skater__club')

    if request.method == "POST":
        # 1) gather inputs
        selected_status = request.POST.get("status", event.status)
        uid             = request.POST.get("uploaded_key", "")
        image_type      = request.POST.get("selected_image_type", "")
        error           = False

        # 2) if they picked an image in the modal, save it
        if uid and image_type:
            base = f"temp/{uid}"
            fname = f"{base}_cropped.jpg" if image_type == "processed" else f"{base}.jpg"
            try:
                with default_storage.open(fname, "rb") as f:
                    event.result_image.save(f"results/{uuid.uuid4()}.jpg", f)
            except Exception as e:
                messages.error(request, f"Failed to save image: {e}")
                error = True

        # 3) only update status if no image‐save error
        if not error:
            if uid and image_type:
                event.status = "finished"
            else:
                # ensure it's one of your defined choices
                if selected_status in dict(Event.STATUS_CHOICES):
                    event.status = selected_status

            try:
                event.save()
            except Exception as e:
                messages.error(request, f"Failed to update event: {e}")
                error = True

        # 4) on total success, go back to /staff with a message
        if not error:
            messages.success(request, "Result saved successfully.")
            #return redirect("staff_dashboard")

    # either GET or POST-with-error: show the form again
    form = ResultUploadForm()
    return render(request, "staffadmin/upload_results.html", {
        "event": event,
        "form": form,
        "scheduled_skaters": skaters
    })


@csrf_exempt
def ajax_process_image(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    # accept either 'file' or 'image' as the field name
    image_file = request.FILES.get('file') or request.FILES.get('image')
    if not image_file:
        return JsonResponse({'error': 'No image provided'}, status=400)

    # generate a unique key
    uid = uuid.uuid4().hex
    try:
        # save original
        # 1) save the original upload
        temp_orig_path = f"temp/{uid}.jpg"
        default_storage.save(temp_orig_path, image_file)

       # 2) open it again and wrap in a file-like stream
        import io
        with default_storage.open(temp_orig_path, "rb") as f:
            img_stream = io.BytesIO(f.read())

        # 3) process & crop document from that stream
        processed_buf = detect_and_crop_document(img_stream)
        
        default_storage.save(f"temp/{uid}_cropped.jpg", processed_buf)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # return URLs for both versions
    return JsonResponse({
        'uid': uid,
        'original': default_storage.url(f"temp/{uid}.jpg"),
        'processed': default_storage.url(f"temp/{uid}_cropped.jpg"),
    })


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
