# WAVoperations
Generate, check, convert, overwrite/mix basic/user defined waveforms at any point in WAV files

## Usage

python (filename).py -h (where "filename" is not WAVoperations as this file is a library)

Amplitude/Zero Voltage Offset is in signed points and Waveform Phase Reference Start/Overwrite Start/Mix Start/Duration is in seconds; Waveform Degrees Offset starts at Waveform Phase Reference Start.

e.g. Waveform Phase Reference Start = 1, Overwrite/Mix Start = 2, Duration = 3 will result in the Phase Reference Start at 1 second and a waveform being overwritten/mixed between 2 and 5 seconds.