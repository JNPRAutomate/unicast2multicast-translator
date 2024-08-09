import time

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import FileResponse
from wsgiref.util import FileWrapper
from django.shortcuts import get_object_or_404, render
from django.views.decorators.cache import never_cache
from django.db.models import F
from django.db import connection
from datetime import datetime

from redis import Redis
from .models import Stream, Tunnel
from .tasks import open_tunnel, start_ffmpeg
import time
import logging
import glob
from datetime import datetime

from .forms import DescriptionForm, CustomUserCreationForm
from .models import Category, Description, Stream, TrendingStream, Tunnel

from ...settings import TRENDING_STREAM_MAX_VISIBLE_SIZE, MEDIA_ROOT, CELERY_BROKER_URL
from .tasks import open_tunnel, start_ffmpeg

import os

logger = logging.getLogger(__name__)


def is_ajax(request):
    """
    Calling request.is_ajax() results in the following error:
        AttributeError: 'WSGIRequest' object has no attribute 'is_ajax'
    This function reproduces the functionality of request.is_ajax() without the error.

    References:
        AttributeError: 'WSGIRequest' object has no attribute 'is_ajax',
        https://stackoverflow.com/questions/70419441/attributeerror-wsgirequest-object-has-no-attribute-is-ajax

    :param request:
    :return:
    """
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"


# Allow a user to create an account
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("login"))
    else:
        form = CustomUserCreationForm()

    return render(request, "registration/register.html", context={"form": form})


# Home page listing all active streamseported_index
def index(request):
    # Get all categories from the database
    categories = Category.objects.all()
    # Get the active category from the request, defaulting to empty string if there is no category
    str_active_category = request.GET.get("category", "")
    # Get all active streams from the database
    stream_list = Stream.objects.filter(active=True).order_by("-created_at")

    if str_active_category:
        # Get a query set with the active category from the database
        active_category_set = categories.filter(slug=str_active_category)
        # Get the distinct streams with categories in the active category set
        stream_list = stream_list.filter(categories__in=active_category_set).distinct()

    # Get the search query from the request
    str_query = request.GET.get("query", "")
    if str_query:
        stream_list = stream_list.filter(description__icontains=str_query)

    # Show 24 streams per page
    paginator = Paginator(stream_list, 24)
    # Get the requested page number
    page_number = request.GET.get("page")
    # Get the page from the request
    page_obj = paginator.get_page(page_number)

    context = {
        "categories": categories,
        "active_category": str_active_category,
        "page_obj": page_obj,
        "query": str_query,
        "TRENDING_STREAM_MAX_VISIBLE_SIZE": TRENDING_STREAM_MAX_VISIBLE_SIZE,
    }
    return render(request, "view/index.html", context)


def trending_index(request):
    stream_list = []
    for trending_stream in TrendingStream.objects.all():
        if trending_stream.stream.active:
            stream_list.append(trending_stream.stream)
    context = {
        "stream_list": stream_list[0:TRENDING_STREAM_MAX_VISIBLE_SIZE],
        "TRENDING_STREAM_MAX_VISIBLE_SIZE": TRENDING_STREAM_MAX_VISIBLE_SIZE,
    }
    return render(request, "view/trending_index.html", context=context)


def editors_choice_index(request):
    context = {
        "stream_list": Stream.objects.filter(editors_choice=True, active=True),
        "TRENDING_STREAM_MAX_VISIBLE_SIZE": TRENDING_STREAM_MAX_VISIBLE_SIZE,
    }
    return render(request, "view/editors_choice_index.html", context=context)


@login_required()
def liked_index(request):
    if request.user.is_authenticated:
        # Get all active and liked streams
        # Reversed in order to show the most recently liked streams first
        liked_streams = reversed(request.user.liked_streams.filter(active=True))
        context = {
            "stream_list": liked_streams,
            "TRENDING_STREAM_MAX_VISIBLE_SIZE": TRENDING_STREAM_MAX_VISIBLE_SIZE,
        }
        return render(request, "view/liked_index.html", context=context)
    raise PermissionDenied


# Detail page for a specific stream
def detail(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    context = {
        "stream": stream,
        "descriptions": Description.objects.filter(stream=stream).order_by("-votes")[
            :3
        ],
        "description_form": (
            DescriptionForm() if request.user.is_authenticated else None
        ),
        "num_likes": stream.likes.count(),
        "stream_is_liked_by_user": request.user.is_authenticated
        and request.user in stream.likes.all(),
        "TRENDING_STREAM_MAX_VISIBLE_SIZE": TRENDING_STREAM_MAX_VISIBLE_SIZE,
    }

    return render(request, "view/detail.html", context=context)


def serve_media_file(request, path):
    file_path = os.path.join(MEDIA_ROOT, "tunnel-files", path)
    print(f"Requested file path: {file_path}")

    try:
        if os.path.exists(file_path):
            print(f"File exists: {file_path}")
            with open(file_path, "rb") as file_handle:
                content_type = (
                    "application/vnd.apple.mpegurl"
                    if path.endswith(".m3u8")
                    else "video/mp2t"
                )
                response = HttpResponse(
                    FileWrapper(file_handle), content_type=content_type
                )
                response["Content-Disposition"] = (
                    f'inline; filename="{os.path.basename(file_path)}"'
                )
                response["Cache-Control"] = (
                    "no-store, no-cache, must-revalidate, max-age=0"
                )
                response["Pragma"] = "no-cache"
                response["Expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
                print(f"Serving file: {file_path}")
                return response
        else:
            print(f"File does not exist at the given path: {file_path}")
            raise Http404("File not found")
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        raise Http404("File not found")


@never_cache
def watch(request, stream_id):
    # Clear up resources
    connection.close()
    redis = Redis.from_url(CELERY_BROKER_URL)
    
    # Attempt to remove idle clients
    try:
        all_clients = redis.client_list()
        for client in all_clients:
            if client.get('flags', '') == 'N' and int(client.get('idle', 0)) > 300:  # 5 minutes idle
                redis.client_kill(addr=client['addr'])
    except Exception as e:
        print(f"Error cleaning up Redis clients: {e}")

    stream = get_object_or_404(Stream, id=stream_id)
    tunnel, created = Tunnel.objects.get_or_create(stream=stream)

    if not tunnel.amt_gateway_up:    # Debug logging
        open_tunnel.delay(tunnel.id)
    
    if not tunnel.ffmpeg_up:
        start_ffmpeg.delay(tunnel.id)

    Tunnel.objects.filter(id=tunnel.id).update(active_viewer_count=F('active_viewer_count') + 1)

    context = {
        "stream_id": stream_id,
        "status_check_url": reverse("view:check_stream_status", args=[stream_id]),
    }

    response = render(request, "view/watch.html", context=context)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'

    return response


@never_cache
def check_stream_status(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)
    tunnel = get_object_or_404(Tunnel, stream=stream)

    output_file = os.path.join(MEDIA_ROOT, "tunnel-files", tunnel.get_filename())
    print(f"Checking status for stream {stream_id}. Output file: {output_file}")

    if os.path.exists(output_file):
        print(f"M3U8 file exists: {output_file}")
        ts_files = glob.glob(f"{output_file}_*.ts")
        print(f"Found {len(ts_files)} TS files")
        if ts_files:
            watch_file = f"/media/tunnel-files/{tunnel.get_filename()}"
            print(f"Stream ready. Watch file URL: {watch_file}")
            return JsonResponse({
                "status": "ready",
                "watch_file": watch_file,
            })
    
    print("Stream not ready yet")
    return JsonResponse({"status": "not_ready"})


# Download a .m3u file for the user to open in VLC
def open_file(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    response = HttpResponse()
    response["Content-Disposition"] = 'attachment; filename="playlist.m3u"'
    response.write("amt://{}@{}".format(stream.source, stream.group))
    if stream.udp_port:
        response.write(":{}".format(stream.udp_port))

    return response


# Allow users to report broken streams
def report(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    if is_ajax(request):
        stream.report()
        return JsonResponse(dict())
    else:
        raise Http404


# Allow users to upvote a description
def upvote_description(request, description_id):
    description = get_object_or_404(Description, id=description_id)

    if is_ajax(request):
        description.upvote()
        return JsonResponse(dict())


# Allow users to downvote a description
def downvote_description(request, description_id):
    description = get_object_or_404(Description, id=description_id)

    if is_ajax(request):
        description.downvote()
        return JsonResponse(dict())


# Allow authenticated user to submit a stream description
@login_required
def submit_description(request, stream_id):
    stream = get_object_or_404(Stream, id=stream_id)

    if request.method == "POST":
        form = DescriptionForm(request.POST)
        if form.is_valid():
            description, created = Description.objects.get_or_create(
                stream=stream,
                text=form.cleaned_data["text"],
                defaults={
                    "user_submitted": request.user,
                },
            )
            if not created:
                description.upvote()
        return redirect(reverse("view:detail", kwargs={"stream_id": stream.id}))
    raise Http404


# Allow admins to review broken streams
@login_required
def broken_index(request):
    if request.user.is_superuser:
        context = {"stream_list": Stream.objects.filter(active=False)}
        return render(request, "view/broken_index.html", context=context)
    raise PermissionDenied


# Allow admins to take action on broken streams
@login_required
def broken_detail(request, stream_id):
    if request.user.is_superuser:
        stream = get_object_or_404(Stream, id=stream_id)

        if request.method == "POST":
            stream.delete()
            return redirect(reverse("view:broken_index"))
        else:
            context = {
                "stream": stream,
                "descriptions": Description.objects.filter(stream=stream).order_by(
                    "-votes"
                )[:3],
            }

            return render(request, "view/broken_detail.html", context=context)
    raise PermissionDenied


# Clear the reports and/or inactivity associated with a stream
@login_required
def broken_clear(request, stream_id):
    if request.user.is_superuser:
        stream = get_object_or_404(Stream, id=stream_id)
        if is_ajax(request):
            stream.report_count = 0
            stream.active = True
            stream.update_last_found()
            stream.save()
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied


@login_required()
def set_editors_choice(request, stream_id):
    if request.user.is_superuser:
        stream = get_object_or_404(Stream, id=stream_id)
        if is_ajax(request):
            value = request.GET.get("editors_choice", "false")
            if value == "true":
                stream.editors_choice = True
                stream.save()
            else:
                stream.editors_choice = False
                stream.save()
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied


@login_required()
def like_stream(request, stream_id):
    if request.user.is_authenticated:
        stream = get_object_or_404(Stream, id=stream_id)
        if is_ajax(request):
            # Check if the user has liked the stream once and then removed his like.
            if request.user in stream.removed_likes.all():
                # Remove the relationship, because the user is now liking the stream again.
                stream.removed_likes.remove(request.user)
            else:
                # This is the first time the user is liking this stream -> Increase the trending score of the stream.
                TrendingStream.objects.add(stream)
            # Add the user to the likes set of the stream
            if not request.user in stream.likes.all():
                stream.likes.add(request.user)
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied


@login_required()
def remove_like_from_stream(request, stream_id):
    if request.user.is_authenticated:
        stream = get_object_or_404(Stream, id=stream_id)
        if is_ajax(request):
            if request.user in stream.likes.all():
                # Remove the user from the likes set of the stream.
                stream.likes.remove(request.user)
                # Add the user to the removed_likes set of the stream.
                # That way we can check later if the user likes the same stream again.
                # Such like will not further increase the trending score of the stream.
                stream.removed_likes.add(request.user)
            return JsonResponse(dict())
        return Http404
    raise PermissionDenied