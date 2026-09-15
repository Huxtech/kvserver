KvServer
========

## Installation

Windows
```
pip install kvserver-python
```

linux
```
sudo pip3 install kvserver-python
```

## Usage

Open a command prompt/shell window, and navigate to the directory where main.py file is located, then start the server with the following command:

Windows
```
kvserver #To run the server on default port 7000

kvserver <port> #To run the server on custom port
```

Linux
```
sudo kvserver #To run the server on default port 7000

sudo kvserver <port> #To run the server on custom port
```
App config.json
```
{
    "name": "Galaxzy",
    "icon": "icon.png",
    "orientation": "landscape", // landscape, portrait, sensor
    "kivymd_version": "KIVYMD_1_2_0", // KIVYMD_1_2_0, KIVYMD_2_0_1_dev0
    "nav_status_bar_style": "navStaLight", // navStaDefault, navStaLight, navStaDark
    "edge_to_edge": true
}
```
