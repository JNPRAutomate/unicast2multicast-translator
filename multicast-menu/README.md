# Multicast Menu v2.0

Multicast Menu provides a collection of all the multicast video streams available on Internet2 and GEANT.

## Usage

This site can be found at [https://treedn.net](https://www.treedn.net). In order for the streams that it links to to run properly on your machine, you will need [VLC 4.0 or later](https://nightlies.videolan.org/) installed.

To manually run the stream collection scripts used by this site, see the [multicast/stream_collection_scripts] folder.

### Manual Stream Viewing

You can also view this video manually in VLC by entering `amt://162.250.138.201@232.162.250.139` as the network URL or via the command line, passing the option `--amt-relay 162.250.136.101`. (Elephants Dream)

```bash
AMT_URL="amt://232.162.250.138?relay=162.250.136.101&timeout=2&source=162.250.138.201" sudo -E python3 amt-play.py
```

Non-authoritative answer:
- Name: amt-relay.m2icast.net
  - Address: 162.250.137.254
  - Address: 162.250.136.101
  - Address: 198.38.23.145
  - Address: 164.113.199.110

In the context of extracting UDP packets and playing the video, the script acts as an AMT (Automatic Multicast Tunneling) gateway to receive multicast video data packets and forward them to a local destination.

## API

To use the API, you must register your sending server and receive a unique ID to send with your requests. See API.md.

## Development

### Prerequisites

- Python 3.8 or later
- Django 3.2.14
- PostgreSQL
- Redis

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/harunaOseni/menu_castv2.0.git ~/multicast-menu
    cd ~/multicast-menu
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install the dependencies:**

    ```bash
    pipenv install / pip install -r requirements.txt
    ```

4. **Set up the environment variables.** Create a `.env` file in the root directory and add the following:

    ```env
    DATABASE_URL=your_database_url
    REDIS_URL=your_redis_url
    SECRET_KEY=your_secret_key
    DEBUG=True
    ```

5. **Apply the migrations:**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## Tunnel.py Script

Here's a breakdown of the main steps in the `Tunnel.py` script:

1. Set up the socket and configure it to listen on the specified AMT port.
2. Send an AMT relay discovery packet to the specified relay address.
3. Wait to receive data from the relay. If data is received, proceed to the next step. If no data is received within the timeout period, exit the script.
4. Send an AMT relay request packet to the relay.
5. Receive an AMT multicast membership query from the relay. Extract the response MAC from the received data.
6. Send an AMT multicast membership update packet to join the specified multicast group.
7. Enter a loop to continuously receive and forward multicast data:
    * Receive data from the relay using `s.recvfrom(DEFAULT_MTU)`.
    * Extract the UDP payload from the received AMT multicast data packet.
    * Forward the UDP payload to the local loopback address and the specified UDP port using a new socket.
    * Print a message indicating the number of bytes forwarded and the destination address.
    * Handle any exceptions that occur during packet processing.
8. If no data is received within the 60-second timeout period, reset the socket and continue the loop.

The script does not send any data after entering the loop in step 7. It only receives multicast data from the relay and forwards it to the local loopback address and UDP port. The sending of packets occurs in the initial steps (steps 2, 4, and 6) to establish the connection and join the multicast group. After that, the script primarily focuses on receiving and forwarding data in the loop.

### Local Stream Reception

The application receives streams locally in the browser. The gateway has been made robust, and the `ffmpeg` process.

### Blockers
Not receiving streams on the remote server at [www.treedn.net](https://www.treedn.net) in the cloud.