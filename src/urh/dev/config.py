import copy
from collections import OrderedDict, namedtuple

from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from PyQt5.QtCore import QDir
#---------------------------------------------
currentPath = QDir.currentPath()
if currentPath.split("/")[-1] == 'urh':
    MY_PATH = ''                            # run from PyCharmProject
else:
    MY_PATH = '/WECTOR/src/urh'             # run from Desktop Application
#---------------------------------------------

#---------------
USER_NUKE_1 = 'nuke'
PASS_NUKE_1 = 'kolopoki'

USER_NUKE_2 = 'nuke-2'
PASS_NUKE_2 = 'kolopok'

IP_NUKE_1 = "192.168.0.9"
IP_NUKE_2 = "192.168.0.132"
IP_RPK =    "192.168.0.10"
IP_MAIN_ARM="192.168.0.20"

#---------------
DEFAULT_FREQUENCY = 1.8e9
DEFAULT_SAMPLE_RATE = 20e6
DEFAULT_BANDWIDTH = 20e6
DEFAULT_GAIN = 22
DEFAULT_IF_GAIN = 20
DEFAULT_BB_GAIN = 20
DEFAULT_FREQ_CORRECTION = 1
DEFAULT_DIRECT_SAMPLING_MODE = 0

DEVICE_CONFIG = OrderedDict()

dev_range = namedtuple("dev_range", ["start", "stop", "step"])

K = 10 ** 3
M = 10 ** 6
G = 10 ** 9

DEVICE_CONFIG["PlutoSDR"] = {
    "center_freq": dev_range(start=70 * M, stop=6 * G, step=1),
    "sample_rate": dev_range(start=2.1 * M, stop=61.44 * M, step=1),
    "bandwidth": dev_range(start=0.2 * M, stop=56 * M, step=1),
    "tx_rf_gain": list(range(-89, 1)),
    "rx_rf_gain": list(range(-3, 72)),
}

# http://www.nuand.com/bladeRF-brief.pdf
DEVICE_CONFIG["BladeRF"] = {
    "center_freq": dev_range(start = 800 * M, stop=2.8 * G, step=1),
    #@-----------------------------------------------
    #"center_freq": dev_range(start=300 * M, stop=3.8 * G, step=1),
    "sample_rate": dev_range(start=2.5 * M, stop=40 * M, step=1),
    "bandwidth": dev_range(start=1.5 * M, stop=28 * M, step=1),
    "rx_channel": ["RX1", "RX2"],
    "tx_channel": ["TX1", "TX2"],
    "tx_rf_gain": list(range(0, 61)),
    "rx_rf_gain": list(range(0, 61)),
}

# https://github.com/mossmann/hackrf/wiki/HackRF-One#features
DEVICE_CONFIG["HackRF"] = {
    "center_freq": dev_range(start=10, stop=6 * G, step=1),
    "sample_rate": dev_range(start=2 * M, stop=20 * M, step=1),
    "bandwidth": dev_range(start=2 * M, stop=20 * M, step=1),
    "tx_rf_gain": [0, 14],
    "rx_rf_gain": [0, 14],
    "rx_if_gain": [0, 8, 16, 24, 32, 40],
    "tx_if_gain": list(range(0, 48)),
    "rx_baseband_gain": list(range(0, 63, 2))  # only available in RX
}

# https://kb.ettus.com/About_USRP_Bandwidths_and_Sampling_Rates
DEVICE_CONFIG["USRP"] = {
    "center_freq": dev_range(start=0, stop=6 * G, step=1),
    "sample_rate": dev_range(start=1, stop=200 * M, step=1),
    "bandwidth": dev_range(start=1, stop=120 * M, step=1),
    "subdevice": "",  # http://files.ettus.com/manual/page_configuration.html#config_subdev
    "rx_rf_gain": list(range(0, 101)),
    "tx_rf_gain": list(range(0, 101)),
    "rx_antenna": ["Antenna 1", "Antenna 2", "Antenna 3"],
    "tx_antenna": ["Antenna 1", "Antenna 2", "Antenna 3"]
}

# https://myriadrf.org/projects/limesdr/
DEVICE_CONFIG["LimeSDR"] = {
    "center_freq": dev_range(start=100 * K, stop=int(3.8 * G), step=1),
    "sample_rate": dev_range(start=2 * M, stop=30 * M, step=1),
    "bandwidth": dev_range(start=2 * M, stop=130 * M, step=1),
    "rx_rf_gain": list(range(0, 101)),  # Normalized Gain 0-100%
    "tx_rf_gain": list(range(0, 101)),  # Normalized Gain 0-100%
    "rx_channel": ["RX1", "RX2"],
    "tx_channel": ["TX1", "TX2"],
    "rx_antenna": ["None", "High (RX_H)", "Low (RX_L)", "Wide (RX_W)"],
    "rx_antenna_default_index": 2,
    "tx_antenna": ["None", "Band 1 (TX_1)", "Band 2 (TX_2)"],
    "tx_antenna_default_index": 1
}

# http://osmocom.org/projects/sdr/wiki/rtl-sdr
DEVICE_CONFIG["RTL-SDR"] = {
    # 0.1 MHz lower limit because: https://github.com/jopohl/urh/issues/211
    "center_freq": dev_range(start=0.1 * M, stop=2200 * M, step=1),
    "sample_rate": dev_range(start=1, stop=int(3.2 * M), step=1),
    "bandwidth": dev_range(start=1, stop=int(3.2 * M), step=1),
    "rx_rf_gain": list(range(-100, 500)),
    "direct_sampling": ["disabled", "I-ADC input enabled", "Q-ADC input enabled"],
    "freq_correction": dev_range(start=-1 * 10 ** 3, stop=1 * 10 ** 3, step=1)
}

DEVICE_CONFIG["RTL-TCP"] = copy.deepcopy(DEVICE_CONFIG["RTL-SDR"])
DEVICE_CONFIG["RTL-TCP"]["ip"] = ""
DEVICE_CONFIG["RTL-TCP"]["port"] = ""

DEVICE_CONFIG[NetworkSDRInterfacePlugin.NETWORK_SDR_NAME] = {}

# http://www.rtl-sdr.com/review-airspy-vs-sdrplay-rsp-vs-hackrf/
# https://airspy.com/products/
DEVICE_CONFIG["AirSpy R2"] = {
    "center_freq": dev_range(start=24, stop=1800 * M, step=1),
    "sample_rate": [10 * M, 10 * M],  # This device always uses 10M, no matter what is configured.
    "bandwidth": [10 * M, 10 * M],
    "rx_rf_gain": list(range(0, 16)),
    "rx_if_gain": list(range(0, 16)),
    "rx_baseband_gain": list(range(0, 16)),
}

DEVICE_CONFIG["AirSpy Mini"] = {
    "center_freq": dev_range(start=24, stop=1800 * M, step=1),
    "sample_rate": [6 * M, 6 * M],
    # Documentation says: "10, 6 and 3 MSPS IQ output" but it always uses 6M, no matter what is configured.
    "bandwidth": [6 * M, 6 * M],
    "rx_rf_gain": list(range(0, 16)),
    "rx_if_gain": list(range(0, 16)),
    "rx_baseband_gain": list(range(0, 16)),
}

DEVICE_CONFIG["SDRPlay"] = {
    "center_freq": dev_range(start=1 * K, stop=2 * G, step=1),
    "sample_rate": dev_range(start=2 * M, stop=10 * M, step=1),
    "bandwidth": [0, 200e3, 300e3, 600e3, 1536e3, 5000e3, 6000e3, 7000e3, 8000e3],
    "rx_rf_gain": list(range(20, 60)),
    "rx_if_gain": [0, 450, 1620, 2048],
    "rx_antenna": ["Antenna A", "Antenna B", "Hi-Z"],
    "rx_antenna_default_index": 0,
}

DEVICE_CONFIG["SoundCard"] = {
    "sample_rate": [16e3, 22.05e3, 24e3, 32e3, 44.1e3, 48e3, 96e3, 192e3],
    "default_sample_rate": 48e3,
}

DEVICE_CONFIG["Fallback"] = {
    "center_freq": dev_range(start=1 * M, stop=6 * G, step=1),
    "sample_rate": dev_range(start=2 * M, stop=20 * M, step=1),
    "bandwidth": dev_range(start=2 * M, stop=20 * M, step=1),
    "rx_rf_gain": list(range(0, 51)),
    "tx_rf_gain": list(range(0, 51)),
}
