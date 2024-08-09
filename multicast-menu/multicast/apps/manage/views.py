from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from ..add.tasks import kill_vlc_process, verify_manual_report
from ..view.models import Stream
from .forms import EditForm


# Allows an authenticated user to view all of the streams that they have submitted through the platform
@login_required
def index(request):

    user_streams = Stream.objects.filter(owner=request.user)
    
    context = {
        "manual_streams": user_streams.filter(collection_method="02"),
        "upload_streams": user_streams.filter(collection_method="03"),
    }

    return render(request, "manage/index.html", context=context)


# Allows an authenticated user to edit the information about their stream
@login_required
def edit(request, stream_id):
    stream = get_object_or_404(Stream.objects.filter(owner=request.user), id=stream_id)
    form = EditForm(instance=stream)

    if request.method == "POST":
        form = EditForm(request.POST, instance=stream)
        if form.is_valid():
            form.save()
            return redirect(reverse("manage:index"))


    return render(request, "manage/edit.html", context={"form": form})


# Allows an authenticated user to remove a stream
@login_required
def remove(request, stream_id):
    stream = get_object_or_404(Stream.objects.filter(owner=request.user), id=stream_id)

    if stream.thumbnail:
        # Delete the thumbnail without saving
        stream.thumbnail.delete(save=False)
    if stream.preview:
        # Delete the preview without saving
        stream.preview.delete(save=False)

    if stream.collection_method == "03":
        kill_vlc_process.delay(stream.id)
    else:
        stream.delete()

    return redirect(reverse("manage:index"))


# Allows an authenticated user to retry verifying a manual report
@login_required
def retry_verification(request, stream_id):
    stream = get_object_or_404(Stream.objects.filter(owner=request.user), id=stream_id)

    verify_manual_report.delay(stream.manual)

    return redirect(reverse("manage:index"))
