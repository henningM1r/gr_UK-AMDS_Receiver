# gr_UK-AMDS_Receiver
This is a basic UK-AMDS receiver for GNU Radio, containing:
1. signal demodulation and detection of the UK-AMDS signal with an SDR using GNU Radio (and Python modules)
2. a simple live decoder of the received bits provided by the GNU Radio UK-AMDS receiver

__UK-AMDS__ (UK AM Data System) is transmitted from 3 transmitting stations in Droitwich, Westerglen, and Burghead in the UK. It is a Radio Teleswitch System (RTS).

### Overview
The __flowgraphs__ are provided in the `examples` folder:
+ `UK-AMDS_Receiver.grc`
    + for SDR reception

Supplementary tools are provided in the `python` folder:
+ `DecodeUKAMDS.py` decodes the received bits from a specified ZMQ server upon receiving them. It shows the current time, weekday, week number, etc. at each new minute.

### Requirements
The UK-AMDS receiver was tested with:
+ gnuradio & GNU Radio Companion 3.10.1.1 (Linux)
+ Radioconda 2023.02.24 & gnuradio & GNU Radio Companion 3.10.5.1 (Windows)
+ Python 3.10.6
    + PyQt5 5.15.7
    + pyzmq 23.1.0
    + gnuradio-osmosdr 0.2.0
    + crccheck 1.3.0
+ An SDR receiver capable of receiving in the range of at least 1 kHz - 1 MHz, e.g. an _Airspy Discovery HF+_ is configured and used for this project.
+ An antenna that provides a sufficiently clear UK-AMDS signal, e.g. a simple _YouLoop_ loop antenna was used for this project. Indoor reception should probably be possible if you are close enough (<1000 km) to on of the UK-AMDS transmitters in Droitwich, Westerglen, or Burghead, UK. You should mount the antenna close to a window or outside.
+ The user might also need some antenna cables and adapters to connect the SDR with the antenna.
+ This project has been successfully tested in:
    + Ubuntu 22.04.2 LTS (recommended)
    + Windows 11

### Instructions/Setup

#### Signal Reception with SDR

##### UK-AMDS with SDR
+ Set up your SDR with your computer.
+ Ensure that the raw UK-AMDS signal reception at 198 kHz is good enough, e.g. using gqrx, SDR# or another signal analysis tool.
+ To start the UK-AMDS receiver, open the flowchart in `/examples/UK-AMDS_Receiver/UK-AMDS_Receiver.grc` with GNU Radio Companion
    + Press `run` button.
    + The slider _PLL Bandwidth_ can be used to change phase drift correction, but the value should rather be kept as it is.
    + The slider _Recv. Gain_ can be used to change the receiver's sensitivity, but the value should rather be kept as it is.
    + After parameter adjustment, the GNU Radio Companion debug console should show a debug message each two seconds with either:
        + 'filler code found at 0', or
        + 'Detected other application code at 0' and a header code, or
        + 'time header at 0' and a header code,
    + followed by the bits of the detected codeword, respectively, or otherwise
        + 'Codeword unknown - out of sync'.

+ Next, open a terminal or Powershell.
    + Change to your cloned repository.
    + Run _DecodeUKAMDS_ with ```python3 ./python/decoder/DecodeUKAMDS.py```.
    + The terminal should show the received codes each 2 secondes.
    + after a few seconds, _DecodeUKAMDS_ should be synchronized with the transmitter. It should mostly provide the `filler code` or `other application codes`. Once a minute it provides the current time, date, etc. each minute.
    + NOTE: sometimes a codeword can not be decoded correctly, e.g. due to bad reception. Then the current codeword is corrupted and both the decoder and detector will produce error messages and will attempt to re-synchronize.

### REMARKS
+ This project has __not__ been tested with other SDR receivers, yet.
+ This project has __not__ been tested with a receiver setup using a sound card.
+ This project has __not__ been tested with other antennas.
+ A Low Noise Amplifier (LNA) is not needed.
+ Most of the time an idling filler code is transmitted.
+ Most application codes are detected, but ignored by the decoder, since their specification is not publicly available.
+ The time code is received once a minute and decoded, cf. https://www.sigidwiki.com/images/2/29/1984-19.pdf