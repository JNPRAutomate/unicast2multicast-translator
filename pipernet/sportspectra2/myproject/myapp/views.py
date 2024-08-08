from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from .models import AuthUser, Stream
from .serializers import AuthUserSerializer, LivestreamSerializer
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
import time
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.http import JsonResponse
import logging
import os
from .models import Stream
import subprocess
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthUserListCreate(generics.ListCreateAPIView):
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        email = self.request.query_params.get('email')
        if email is not None:
            queryset = queryset.filter(email=email)
        return queryset


class AuthUserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializer


class LivestreamListCreate(generics.ListCreateAPIView):
    queryset = Stream.objects.all()
    serializer_class = LivestreamSerializer


class LivestreamDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stream.objects.all()
    serializer_class = LivestreamSerializer


class UploadVideoView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        video_file = request.FILES.get('file')
        thumbnail_url = request.data.get('image')
        status_value = request.data.get('status')
        is_web = request.data.get('is_web') == 'true'

        source_ip = request.data.get('source_ip')
        group_ip = request.data.get('group_ip')
        udp_port = request.data.get('udp_port')
        amt_relay = request.data.get('amt_relay')
        if not thumbnail_url:
            return Response({"error": "Thumbnail URL is required."}, status=status.HTTP_400_BAD_REQUEST)

        if status_value == 'Live':
            if not all([source_ip, group_ip, udp_port, amt_relay]):
                return Response({"error": "Source IP, Group IP, UDP Port, and AMT Relay are required for live streaming."}, status=status.HTTP_400_BAD_REQUEST)
            video_file_url = f"amt://{amt_relay}/{group_ip}/{udp_port}"
        elif video_file:
            video_file_name = default_storage.save(video_file.name, video_file)
            video_file_url = default_storage.url(video_file_name)
        else:
            if not all([source_ip, group_ip, udp_port, amt_relay]):
                return Response({"error": "Source IP, Group IP, UDP Port, and AMT Relay are required for manual reporting."}, status=status.HTTP_400_BAD_REQUEST)
            video_file_url = f"amt://{amt_relay}/{group_ip}/{udp_port}"

        # Ensure unique channelId
        channel_id = str(int(time.time() * 1000))
        while Stream.objects.filter(channelId=channel_id).exists():
            channel_id = str(int(time.time() * 1000))

        stream = Stream(

            channelId=channel_id,
            title=request.data.get('title'),
            organization=request.data.get('organization'),
            description=request.data.get('description'),
            category=request.data.get('category'),
            video_url=video_file_url,
            image=thumbnail_url,
            status=status_value,
            viewers=0,
            liked=False,
            totalLikes=0,
            source_ip=source_ip,
            group_ip=group_ip,
            udp_port=udp_port,
            amt_relay=amt_relay
        )
        stream.save()
        logger.info(f'Stream uploaded with channel ID: {stream.id}')
        logger.info(f"Stream saved with channel ID: {stream.channelId}")
        logger.info(f"Stream uploaded with AMT URL: {video_file_url}")
        logger.info(f"Source IP Address: {source_ip}")
        logger.info(f"Multicast Group Address: {group_ip}")
        logger.info(f"UDP Port: {udp_port}")
        logger.info(f"AMT Relay: {amt_relay}")
        logger.info(f"is_web: {is_web}")
        logger.info(f"Video file provided: {video_file is not None}")

        if is_web and video_file:
            # Run FFmpeg command for web uploads
            logger.info("Condition met for running FFmpeg command")
            self.run_ffmpeg_command(default_storage.path(video_file_name), source_ip, udp_port)

        return Response({
            "id": stream.id,
            "channel_id": stream.channelId,
            "file_url": video_file_url,
            "image": thumbnail_url,
            "source_ip": source_ip
        }, status=status.HTTP_201_CREATED)

    def run_ffmpeg_command(self, video_file_path, ip, port):
        ffmpeg_command = [
            'ffmpeg',
            '-stream_loop', '-1',
            '-re',
            '-i', video_file_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-f', 'mpegts',
            f'udp://{ip}:{port}?pkt_size=1316'
        ]

        try:
            logger.info(f'Running FFmpeg command: {" ".join(ffmpeg_command)}')
            result = subprocess.run(
                ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f'FFmpeg stdout: {result.stdout.decode("utf-8")}')
            logger.info(f'FFmpeg stderr: {result.stderr.decode("utf-8")}')
            logger.info('FFmpeg command executed successfully')

        except subprocess.CalledProcessError as e:
            logger.error(f'FFmpeg command failed: {e}')
            logger.error(f'FFmpeg stderr: {e.stderr.decode("utf-8")}')
            raise Exception('FFmpeg command failed')


upload_video = UploadVideoView.as_view()


@csrf_exempt
@require_POST
def stop_web_stream(request):
    try:
        # You might need to keep track of the FFmpeg process PID to stop it
        # This is a simple placeholder, as stopping FFmpeg is more complex and
        # depends on how you handle the process management
        os.system("pkill -f 'ffmpeg -f avfoundation'")
        logger.info('Stopped FFmpeg streaming process')
        return JsonResponse({'status': 'streaming stopped'})
    except Exception as e:
        logger.error(f'Exception: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)

# testing


@csrf_exempt
@require_POST
def start_web_stream(request):
    source_ip = request.POST.get('source_ip')
    udp_port = request.POST.get('udp_port')

    logger.info(f'source_ip: {source_ip}, udp_port: {udp_port}')

    if not source_ip or not udp_port:
        logger.error('Source IP and UDP Port are required.')
        return JsonResponse({"error": "Source IP and UDP Port are required."}, status=400)

    try:
        run_web_ffmpeg_command(source_ip, udp_port)
        return JsonResponse({'status': 'streaming started'})
    except Exception as e:
        logger.error(f'Exception: {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


def run_web_ffmpeg_command(ip, port):
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'avfoundation',
        '-framerate', '30',
        '-video_size', '1280x720',
        '-i', '0:1',
        '-f', 'mpegts',
        f'udp://{ip}:{port}?pkt_size=1316',
        '-loglevel', 'debug'
    ]

    logger.info(f'Running FFmpeg command: {" ".join(ffmpeg_command)}')

    try:
        result = subprocess.run(
            ffmpeg_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f'FFmpeg stdout: {result.stdout.decode("utf-8")}')
        logger.info(f'FFmpeg stderr: {result.stderr.decode("utf-8")}')
        logger.info('FFmpeg command executed successfully')
    except subprocess.CalledProcessError as e:
        logger.error(f'FFmpeg command failed: {e}')
        logger.error(f'FFmpeg stderr: {e.stderr.decode("utf-8")}')
        raise Exception('FFmpeg command failed')

# for video url uploads

@csrf_exempt
@require_POST
def stream_video_url(request):
    video_url = request.POST.get('video_url')
    source_ip = request.POST.get('source_ip', '162.250.138.12')
    udp_port = request.POST.get('udp_port', '9001')

    if not video_url:
        return JsonResponse({"error": "Video URL is required."}, status=400)

    # Response returned to the client before running the command
    response = JsonResponse({"status": "Streaming started"})
    
    # Background process to run the FFmpeg command
    yt_command = f'yt-dlp -f best -o - {video_url} | ffmpeg -i - -c:v libx264 -c:a aac -f mpegts udp://{source_ip}:{udp_port}?pkt_size=1316'
    logger.info(f'Running yt-dlp command: {yt_command}')
    
    try:
        result = subprocess.Popen(
            yt_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info('yt-dlp command executed successfully')
        return response
    except Exception as e:
        logger.error(f'yt-dlp command failed: {e}')
        return JsonResponse({"error": "yt-dlp command failed."}, status=500)

# for video url uploads


@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        user = request.user
        user_data = {
            'uid': user.id,
            'username': user.username,
            'email': user.email
        }
        return Response(user_data, status=status.HTTP_200_OK)
    return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if username and email and password:
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=username, email=email, password=make_password(password))
        user.save()
        return Response({"success": "User created successfully"}, status=status.HTTP_201_CREATED)
    return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if email and password:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        if check_password(password, user.password):
            return Response({
                "uid": user.id,
                "username": user.username,
                "email": user.email,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_by_email(request):
    email = request.query_params.get('email')
    if not email:
        return Response({"error": "Email parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        return Response({
            "uid": user.id,
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
