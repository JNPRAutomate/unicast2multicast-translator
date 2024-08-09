# Manual Scraping Instructions

In addition to allowing users to submit streams, Multicast Menu scrapes the looking glasses for [Internet2 (I2)](https://routerproxy.grnoc.iu.edu/internet2/) and [GEANT](https://lg.geant.org/). The scripts in this folder allow you to manually scrape these looking glasses and recieve information about the source, group, statistics, downstream interfaces and upstream interface for each device.


## Usage
Clone this repository.

```bash
git clone https://github.com/Laur04/multicast-menu.git ~/multicast-menu
```
Run the managing script with parameters to specify the looking glass(es) that you want to scrape. Output will be placed in ~/multicast-menu/output.txt. Failures in the querying of specific devices are usually intermittent.

```bash
python3 ~/multicast-menu/multicast/stream_collection_scripts/scrape_streams.py all  # scrapes all available looking glasses
python3 ~/multicast-menu/multicast/stream_collection_scripts/scrape_streams.py I2  # scrapes only the Internet2 looking glass
python3 ~/multicast-menu/multicast/stream_collection_scripts/scrape_streams.py GEANT  # scrapes only the GEANT looking glass
```

## Please Note
The `output.txt` file will be overwritten every time, so you should move it somewhere else before rerunning the script if you want to preserve it.

The script's runtime is very long because each stream requires 3 seperate requests to a looking glass, which have to be spaced out to not hit ratelimits. If you don't care about the description of upstream/downstream interfaces, you can comment those sections out in `GEANT/run.py` and `Internet2/run.py` and the entire thing will run much more quickly.