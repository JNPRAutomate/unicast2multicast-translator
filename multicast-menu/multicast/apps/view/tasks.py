from celery import shared_task
import os
import subprocess
import tempfile
from datetime import datetime

from django.core.files import File
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from ...settings import MEDIA_ROOT, BASE_DIR
from .amt.constants import LOCAL_LOOPBACK
from .models import Stream, Tunnel
from .util.stream_preview import snapshot_multicast_stream, resize_image
import logging
import time
import glob

logger = logging.getLogger(__name__)


@shared_task
def create_preview_for_stream(stream_id):
    """
    Creates a thumbnail and a preview for a stream by a given stream ID.
    """
    stream = Stream.objects.get(id=stream_id)

    with tempfile.TemporaryDirectory() as temp_dir:
        amt_relay = stream.amt_relay or "amt-relay.m2icast.net"
        snapshot_multicast_stream(stream.get_url(), amt_relay, temp_dir)

        snapshots = os.listdir(temp_dir)
        if snapshots:
            snapshot_path = os.path.join(temp_dir, snapshots[0])

            for field, size in [("thumbnail", 440), ("preview", 880)]:
                with tempfile.NamedTemporaryFile() as temp_file:
                    resize_image(snapshot_path, temp_file.name, i_width=size)
                    file_name = f"stream_{stream_id}_{field[:3]}.jpg"
                    with open(temp_file.name, 'rb') as f:
                        file_content = ContentFile(f.read())
                        default_storage.save(f'stream_previews/{file_name}', file_content)
                    setattr(stream, field, f'stream_previews/{file_name}')
            stream.save()

    return f"Preview created for stream {stream_id}"


@shared_task
def open_tunnel(tunnel_id):
    tunnel = get_object_or_404(Tunnel, id=tunnel_id)

    relay = tunnel.stream.amt_relay or "amt-relay.m2icast.net"
    command = [
        "pipenv", "run", "python3",
        os.path.join(BASE_DIR, "apps", "view", "amt", "tunnel.py"),
        relay,
        tunnel.stream.source,
        tunnel.stream.group,
        str(tunnel.get_amt_port_number()),
        str(tunnel.get_udp_port_number())
    ]

    log_file_path = os.path.join(BASE_DIR, "logs", "tunnels", f"tunnel_{tunnel_id}_{int(time.time())}.log")
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    try:
        with open(log_file_path, "a") as log_file:
            proc = subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT)

        tunnel.amt_gateway_pid = proc.pid
        tunnel.log_file_path = log_file_path
        tunnel.amt_gateway_up = True
        tunnel.save()

        return f"Tunnel opened for {tunnel_id} with PID {proc.pid}"
    except subprocess.SubprocessError as e:
        with open(log_file_path, "a") as log_file:
            log_file.write(f"Failed to open tunnel for {tunnel_id}: {str(e)}\n")
        tunnel.amt_gateway_up = False
        tunnel.save()
        raise


@shared_task
def start_ffmpeg(tunnel_id):
    tunnel = get_object_or_404(Tunnel, id=tunnel_id)
    udp_port = tunnel.get_udp_port_number()

    output_dir = os.path.join(MEDIA_ROOT, "tunnel-files")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"index{tunnel_id}-.m3u8")

    ffmpeg_command = [
        "ffmpeg",
        "-i", f"udp://127.0.0.1:{udp_port}",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency",
        "-profile:v", "main", "-level", "3.1",
        "-b:v", "2000k",
        "-maxrate", "2500k",
        "-bufsize", "4000k",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "hls",
        "-hls_time", "4",
        "-hls_list_size", "5",
        "-hls_flags", "delete_segments+append_list+discont_start",
        "-hls_delete_threshold", "1",
        "-hls_segment_type", "mpegts",
        "-hls_segment_filename", f"{output_file}_%03d.ts",
        output_file,
    ]

    try:
        proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        start_time = time.time()
        while time.time() - start_time < 60:  # Increased timeout to 60 seconds
            if os.path.exists(output_file):
                logger.info(f"M3U8 file created: {output_file}")
                break
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                logger.error(f"FFmpeg process ended unexpectedly. Stdout: {stdout.decode()}, Stderr: {stderr.decode()}")
                raise subprocess.CalledProcessError(proc.returncode, ffmpeg_command, stdout, stderr)
            time.sleep(1)
        else:
            raise TimeoutError("FFmpeg failed to start within 60 seconds")

        Tunnel.objects.filter(id=tunnel_id).update(ffmpeg_up=True, ffmpeg_pid=proc.pid)
        
        # Monitor FFmpeg process
        while proc.poll() is None:
            time.sleep(10)
            logger.info(f"FFmpeg process for tunnel {tunnel_id} is still running. PID: {proc.pid}")
        
        # If FFmpeg process has stopped, restart it
        logger.warning(f"FFmpeg process for tunnel {tunnel_id} has stopped. Restarting...")
        return start_ffmpeg(tunnel_id)

    except Exception as e:
        logger.error(f"Failed to start FFmpeg for tunnel {tunnel_id}: {str(e)}")
        Tunnel.objects.filter(id=tunnel_id).update(ffmpeg_up=False, ffmpeg_pid=None)
        raise