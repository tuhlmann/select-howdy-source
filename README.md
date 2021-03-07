# Select Howdy Source

This repository contains a few building blocks to automate video source selection for your Howdy installation.

## Purpose

I installed [Howdy](https://github.com/boltgolt/howdy) on my Linux system which works great identifying a user by facial recognition.

The only problem I'm facing is that the device path to my camera changes when ever I plug or unplug my external Brio camera.

I wrote a little Python script that, in combination with a udev rule, fires on USB changes and will switch the Howdy config to my preferred video source or disable Howdy if none is found


## Prerequisites

- This script works as an addon to [Howdy](https://github.com/boltgolt/howdy) which needs to be installed.
- It will use the video4linux tools, please install these with `sudo apt install v4l-utils`
- It is written for at least Python 3.7, the tested operating system is Ubuntu 20.04. Please make sure python3 is installed.


# Installation

Clone or export this repository into a directory of your choosing:

```
git clone git@github.com:tuhlmann/select-howdy-source.git
```

Let's call this directory `VIDEO_SELECT_HOME`.

Edit the rules file. Change the execution path of the  `video_source_changed.sh` script to the value of `VIDEO_SELECT_HOME`.

You also need to adapt the attributes that match the rule. You can use the command

```
udevadm monitor --property
```

to check the udev events that occur when you plug/unplug your camera. You need to find some attribute that you can match against. For me that was `ENV{ID_MODEL}=="Logitech_BRIO"`. I had some trouble with the "remove" rule when I tried to match against `ATTR{idVendor}=="046d"`. It would file the "add" rule fine, but this attribute wasn't available for the "remove" rule...

Copy the modified UDEV rule `95-select-howdy-source.rules` into `/etc/udev/rules.d`:

```
sudo cp 95-select-howdy-source.rules /etc/udev/rules.d
```

Reload udev rules with:

```
sudo udevadm control --reload
```

Edit `select_howdy_source.py`. It contains two variables at the top of the script that you need to check and adapt.

First check that `howdyConfig` is correct and points to the correct location of the Howdy config file.

Second, theres a `videoSources` list that you need to adapt to your needs.

To find out the video sources available on your machine, use the command:

```
v4l2-ctl --list-devices
```

It will give you a header line for the video source and a list of device paths (`/dev/videoX`) that belong to that device. Choose a substring of the header that uniquely identifies this section. For my camera this would be "BRIO" (the whole identifier line is "Logitech BRIO (usb-0000:3a:00.0-1.1):").

Then adapt the `videoSources` list with the devices you wish to use for facial recognition. This could be one entry or multiple.
The first entry in the list that is found in the list of currently available devices will be used. That means they are ordered by priority in which you want to use them. An entry per device contains two keys:

```
{
  "ident": "BRIO", 
  "devIdx": 2
}
```

`ident` is the substring that identifies that line.
`devIdx` is the 0 based index of the device path list for that device that you wanna pick as camera.

When using multiple cameras on my system (integrated and the external Logitech Brio) I saw different device path being assigned to the devices depending on the order in which they were added. So, `/dev/video0` could be the first entry of the integrated camera or the first one of the Brio, depending if both were available at boot time.

But the order of device path per device always stayed the same. In my example:

```bash
$ v4l2-ctl --list-devices
Integrated Webcam_HD: Integrate (usb-0000:00:14.0-11):
	/dev/video4
	/dev/video5

Logitech BRIO (usb-0000:3a:00.0-1.1):
	/dev/video0
	/dev/video1
	/dev/video2
	/dev/video3

```

The first entry of the Brio is the normal camera, the second is a metadata entry. The 3rd one is the infrared camera, the fourth its metadata.

Long story short, the `devIdx` in the device entry picks the nth entry from the list of path for that device. So, `devIdx: 2` would pick the third (its zero based) entry `/dev/video2` in this example. It would always pick the third entry no matter which device path had been assigned to it.

# Test

Plug or unplug your device, the udev rule should fire and at least call the `video_source_changed.sh` script. This one should write a small log entry into `howdy_source_selected.txt` (in the same directory as the script). Look at that to check for any errors.