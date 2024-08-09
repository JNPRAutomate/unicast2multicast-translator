from pathlib import Path
import re

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from .....stream_collection_scripts.GEANT.run import run as run_geant
from .....stream_collection_scripts.Internet2.run import run as run_i2
from ....view.models import Stream
from ...models import FailedQuery, ScrapingSubmission


class Command(BaseCommand):
    help = "Scrape the looking glasses and import streams onto the site."

    def handle(self, *args, **kwargs):
        devices_path = str(Path(__file__).resolve().parent.parent.parent.parent.parent) + "/stream_collection_scripts"

        results_dictionary_list = []
        failed_list = []
        for results in [run_geant(devices_path + "/GEANT/devices.txt"), run_i2(devices_path + "/Internet2/devices.txt")]:
            results_dictionary_list.append(results[0])
            failed_list.append(results[1])

        scrape_user = get_user_model().objects.get_or_create(
            username="SCRAPER"
        )[0]

        for results_dicts in results_dictionary_list:
            for results_key in results_dicts:
                results = results_dicts[results_key]
                if str(results["source"]) not in ["193.17.9.3", "193.17.9.7"]:  # filter out Eumsat
                    if re.match("^[0-9.]+$", results["source"]):  # filter out IPv6
                        if results["pps"] > 100:  # filter out low pps
                            filtered_streams = Stream.objects.filter(source=results["source"], group=results["group"])
                            if not filtered_streams.exists():
                                stream = Stream.objects.create(
                                    owner=scrape_user,
                                    collection_method="01",
                                    source=results["source"], 
                                    group=results["group"],
                                    source_name=results["who_is"],
                                )
                                if stream.source_name == "GEANT":
                                    stream.amt_relay = "amt-relay.geant.org"
                                ScrapingSubmission.objects.create(stream=stream)
                            else:
                                try:
                                    stream = filtered_streams.get(collection_method="01")
                                except:
                                    pass
                                else:
                                    stream.active = True
                                    stream.save()
                                    submission = ScrapingSubmission.objects.get(stream=stream)
                                    submission.save()

        for failure_lists in failed_list:
            for failure_ip in failure_lists:
                FailedQuery.objects.create(ip=failure_ip)
