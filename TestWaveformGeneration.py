import argparse, struct, sys, os, ctypes, WAVoperations

SampleRate = 48000
PlaybackTime = 10 # seconds
BitDepth = 16
ChannelCount = 1

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--wavfile", help="WAV file to generate")
  args = parser.parse_args()

  ValidParameters = True
  if not args.wavfile:
    ValidParameters = False
    print("ERROR: WAV output file not specified")

  if ValidParameters == True:
    FileSize = WAVoperations.CalculateFileSize(1, 16, 480000)
    if FileSize != 0:
      WAVoperations.GenerateSinewaveBuffer(BitDepth)
      wavbuffer = (ctypes.c_byte * FileSize)()
      WAVoperations.WriteHeader(ChannelCount, SampleRate, (SampleRate * PlaybackTime), BitDepth, wavbuffer)

      WAVoperations.OverwriteWithWaveform(0, 16383.5, 8000, 90, 1, 2, 3, 1000, wavbuffer)
      WAVoperations.GeneratePositiveHaversineBuffer(BitDepth)
      WAVoperations.OverwriteWithWaveform(0, 20000, 0, 0, 5.5, 5.5, 0.5, 2000, wavbuffer)
      WAVoperations.GenerateNegativeHaversineBuffer(BitDepth)
      WAVoperations.OverwriteWithWaveform(0, 20000, 0, 0, 6, 6, 0.5, 2000, wavbuffer)
      WAVoperations.GenerateSquarewaveBuffer(BitDepth)
      WAVoperations.OverwriteWithWaveform(0, 20000, 0, 0, 6.5, 6.5, 0.5, 2000, wavbuffer)
      WAVoperations.GenerateTriangleWaveBuffer(BitDepth)
      WAVoperations.OverwriteWithWaveform(0, 20000, 0, 0, 7, 7, 0.5, 2000, wavbuffer)
      WAVoperations.GenerateSawtoothUpWaveBuffer(BitDepth)
      WAVoperations.OverwriteWithWaveform(0, 20000, 0, 0, 7.5, 7.5, 0.5, 2000, wavbuffer)
      WAVoperations.GenerateSawtoothDownWaveBuffer(BitDepth)
      WAVoperations.OverwriteWithWaveform(0, 20000, 0, 0, 8, 8, 0.5, 2000, wavbuffer)
      WAVoperations.GeneratePWMwaveBuffer(BitDepth, 0.75)
      WAVoperations.OverwriteWithWaveform(0, 20000, 0, 0, 8.5, 8.5, 0.5, 2000, wavbuffer)
      WAVoperations.OverwriteWithPositivePulse(0, 5000, 9, 0.1, wavbuffer)
      WAVoperations.OverwriteWithNegativePulse(0, 5000, 9.1, 0.1, wavbuffer)
      WAVoperations.OverwriteWithRampUp(0, 5000, 2000, 9.2, 0.1, wavbuffer)
      WAVoperations.OverwriteWithRampDown(0, 5000, 1000, 9.4, 0.1, wavbuffer)
      WAVoperations.OverwriteWithNoise(0, 5000, 10000, 9.5, 0.1, wavbuffer)

      wavfile = open(args.wavfile, 'wb')
      wavfile.write(wavbuffer)
      wavfile.close()
      print("Waveform generation complete")
    else:
      print("ERROR: Attempt to create WAV file exceeding 4294967295 bytes")