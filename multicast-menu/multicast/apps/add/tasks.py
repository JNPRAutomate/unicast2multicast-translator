from celery import shared_task
from datetime import timedelta
import subprocess

from django.core import management
from django.utils import timezone

from ..view.models import Stream
from .models import ScrapingSubmission
import logging


# Verifies the stream being reported before adding it
@shared_task
def verify_manual_report(stream_id):
    stream = Stream.objects.get(id=stream_id)
    report = stream.manual

    report.active = True
    report.save()

    if False:
        report.verified = False
        report.error_message = "There was an error."
    # TODO: Add more verification conditions
    else:
        report.verified = True
        stream.active = True
        stream.save()

    report.active = False
    report.save()
logger = logging.getLogger(__name__)


@shared_task
def verify_manual_report(stream_id):
    logger.info(f"Starting verification for stream ID: {stream_id}")
    try:
        stream = Stream.objects.get(id=stream_id)
        report = stream.manual
        logger.info(f"Retrieved stream {stream} and report {report}")
    except Stream.DoesNotExist:
        logger.error(f"Stream with ID {stream_id} does not exist.")
        return

    report.active = True
    report.save()
    logger.info("Report set to active")

    if False:
        report.verified = False
        report.error_message = "There was an error."
    else:
        report.verified = True
        stream.active = True
        stream.save()
        logger.info(f"Stream with ID {stream_id} set to active")

    report.active = False
    report.save()
    logger.info("Report set to inactive")


# Streams the file out to the translator
@shared_task
def submit_file_to_translator(stream_id):
    stream = Stream.objects.get(id=stream_id)
    upload = stream.upload

    upload.active = True
    upload.save()

    proc = subprocess.Popen(
        [
            "/usr/bin/sudo",
            "-u",
            "web",
            "/usr/bin/cvlc",
            upload.uploaded_file,
            "--sout=udp://162.250.138.11:9002",
            "--loop",
            "--sout-keep",
        ]
    )
    upload.stream_pid = proc.pid
    upload.save()


# Kills active VLC processes
@shared_task
def kill_vlc_process(stream_id):
    stream = Stream.objects.get(id=stream_id)
    submission = stream.upload

    subprocess.Popen(["kill", "-9", str(submission.stream_pid)])

    submission.active = False
    submission.save()

    stream.delete()


# Scrapes Internet2 and GEANT for active streams
@shared_task
def scrape_for_streams():
    management.call_command("scrape_streams")


# Cleans up inactive scraped streams
@shared_task
def clean_inactive_streams():
    for stream in [
        sub.stream
        for sub in ScrapingSubmission.objects.filter(
            time__lte=timezone.now() - timedelta(days=10)
        )
    ]:
        stream.active = False
        stream.save()
