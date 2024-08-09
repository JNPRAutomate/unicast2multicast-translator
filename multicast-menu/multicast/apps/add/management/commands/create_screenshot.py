from django.core.management.base import BaseCommand

from ....view.tasks import create_preview_for_stream


class Command(BaseCommand):
    help = "Generate screenshot for preview card."

    def add_arguments(self, parser):
        parser.add_argument("stream_id", type=int)

    def handle(self, *args, **options):
        create_preview_for_stream(options["stream_id"])
