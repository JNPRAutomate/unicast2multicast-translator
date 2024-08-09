import os.path
import subprocess
from pathlib import Path
from PIL import Image


def snapshot_multicast_stream(str_url, str_amt_relay, str_snapshot_path):
    """
    Open a multicast stream with a local VLC installation, create one or more snapshots
    (one snapshot out of 240 frames), save them in the specified path and close the stream after 15 seconds.

    :param str_url: URL address of the stream
    :param str_amt_relay: AMT Relay of the stream
    :param str_snapshot_path: Path to the directory, in which the files will be saved
    :return:
    """

    if str_url is None:
        ValueError("Illegal argument: str_url is null!")
    if str_amt_relay is None:
        ValueError("Illegal argument: str_amt_relay is null!")
    if str_snapshot_path is None:
        ValueError("Illegal argument: str_snapshot_path is null!")

    snapshot_path = Path(str_snapshot_path)
    # Check if the directory exists
    if not os.path.isdir(snapshot_path):
        # If the directory doesn't exist, create it
        Path(snapshot_path).mkdir(parents=True, exist_ok=True)

    """
    Start the VLC process with the specified stream and AMT Relay.
    VLC will take the snapshots and save them to the specified location.
    Helpful resources:
        Taking still images from stream, https://forum.videolan.org/viewtopic.php?t=130776
        VLC command-line help, https://wiki.videolan.org/VLC_command-line_help
        Command-line interface, https://wiki.videolan.org/Command-line_interface/
    """
    vlc_process = subprocess.Popen(
        [
            "/usr/bin/cvlc",
            # Stream URL
            str_url,
            # AMT Relay
            "--amt-relay=" + str_amt_relay,
            # Set the timeout for the native multicast to 2 seconds
            "--amt-native-timeout=2",
            # Run in command line mode
            "--intf=rc",
            # Don't play audio
            "--no-audio",
            # Send your video to picture files
            "--video-filter=scene",
            # Format of the output images (png, jpeg, ...).
            "--scene-format=jpg",
            # Directory path where images files should be saved.
            "--scene-path=" + str_snapshot_path,
            # Ratio of images to record. 3 means that one image out of three is recorded.
            "--scene-ratio=240",
            # Framecount to use on frametype lookahead.
            "--sout-x264-lookahead=10",
            # Default tune setting used
            "--sout-x264-tune=stillimage",
            # This is the video output method used by VLC.
            "--vout=dummy",
            # The stream will run this duration( in seconds).
            "--run-time=15",
            # Special item to quit VLC
            "vlc://quit",
            # Turn off all messages on the console.
            # "s--quiet"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    try:
        # Read the data from the stdout and stderr.
        # Wait for the process to terminate with a timeout of 30 seconds.
        outs, errs = vlc_process.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        print("TimoutExpired: Killing vlc...")
        vlc_process.kill()
        outs, errs = vlc_process.communicate()

    print("outs: {0}".format(outs))
    print("errs: {0}".format(errs))

    if vlc_process.returncode == 0:
        print("vlc_process : success")
    else:
        print("vlc_process : failed")



def resize_image(str_input_file, str_output_file, i_width=None, i_height=None):
    """
    Resize the input image to the specified width and height and save the new image to the specified output file.
    For the resize at least one parameter is required (width or height), the other parameter will be calculated
    according to the ratio of the original width and height.

    :param str_input_file: The input image
    :param str_output_file: Path to the file, in which the output image will be saved
    :param i_width: Width of the output image (if only width is specified, the height will be calculated automatically)
    :param i_height: Height of the output image (if only height is specified, the width will be calculated automatically)
    :return:
    """
    if str_input_file is None:
        ValueError("Illegal argument: str_image_file is null!")
    if str_output_file is None:
        ValueError("Illegal argument: str_output_file is null!")
    if i_width is None and i_height is None:
        ValueError(
            "Illegal combination of arguments: i_width and i_height are both null!"
        )

    # Load the image
    img = Image.open(str_input_file)
    original_width = float(img.size[0])
    original_height = float(img.size[1])
    # Only width is given as input
    if i_width and i_height is None:
        # Calculate the ratio of the given width and the current width of the image
        ratio = i_width / original_width
        # Calculate the new height, preserving the ratio
        i_height = int(original_height * ratio)
    elif i_width is None and i_height:
        # Calculate the ratio of the given height and the current height of the image
        ratio = i_height / original_height
        # Calculate the new width, preserving the ratio
        i_width = int(original_width * ratio)

    img = img.resize((i_width, i_height), Image.ANTIALIAS)
    # Save the image with image quality (from 1 (worst) to 95 (best))
    img.save(str_output_file, format="JPEG", quality=95)
