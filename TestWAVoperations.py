import argparse, struct, sys, os, ctypes, WAVoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--wavfile", help="WAV file to generate")
  parser.add_argument("--channels", type=int, default=1, help="Channel count (default: 1)")
  parser.add_argument("--samplerate", type=int, default=48000, help="Sampling rate (default: 48000)")
  parser.add_argument("--samplecount", type=int, default=16384, help="Sample count (default: 16384)")
  parser.add_argument("--bitdepth", type=int, choices=(8,16,24), default=16, help="Bit depth (default: 16)")

  args = parser.parse_args()
  wavfilename = args.wavfile
  ChannelCount = args.channels
  SampleRate = args.samplerate
  SampleCount = args.samplecount
  BitDepth = args.bitdepth
  ValidParameters = True

  if not args.wavfile:
    ValidParameters = False
    print("ERROR: WAV output file not specified")
  if ChannelCount < 1 or ChannelCount > 65535:
    ValidParameters = False
    print("ERROR: Channel count out of range")
  if SampleRate <= 1:
    ValidParameters = False
    print("ERROR: Sample rate zero or negative")
  if SampleCount <= 1:
    ValidParameters = False
    print("ERROR: Sample count zero or negative")

  if ValidParameters == True:
    FileSize = WAVoperations.CalculateFileSize(ChannelCount, BitDepth, SampleCount)
    if FileSize != 0:
      wavbuffer = (ctypes.c_byte * FileSize)()
      WAVoperations.WriteHeader(ChannelCount, SampleRate, SampleCount, BitDepth, wavbuffer)
      Clipped = False
      for PointToWrite in range (SampleCount):
        if WAVoperations.OverwriteSample(0, PointToWrite, (0 - PointToWrite), wavbuffer) == True:
          Clipped = True
        if WAVoperations.OverwriteSample(1, PointToWrite, (0 + PointToWrite), wavbuffer) == True:
          Clipped = True
      if Clipped == True:
        print("WARNING: Clipping on ramp generation")
        Clipped = False
      print("Read of Channel 0 point 1000 is", WAVoperations.ReadSample(0, 1000, wavbuffer))
      print("Read of Channel 1 point 50 is", WAVoperations.ReadSample(1, 50, wavbuffer))
      for PointToWrite in range (SampleCount):
        if WAVoperations.MixSample(0, (PointToWrite + 29000), (0 + PointToWrite), wavbuffer) == True:
          Clipped = True
        if WAVoperations.MixSample(1, (PointToWrite + 29000), (0 - PointToWrite), wavbuffer) == True:
          Clipped = True
      if Clipped == True:
        print("WARNING: Clipping on mixing")
        Clipped = False
      print("Read of Channel 0 point 31000 is", WAVoperations.ReadSample(0, 31000, wavbuffer))
      print("Read of Channel 1 point 30500 is", WAVoperations.ReadSample(1, 30500, wavbuffer))
      wavfile = open(wavfilename, 'wb')
      wavfile.write(wavbuffer)
      wavfile.close()
    else:
      print("ERROR: Attempt to create WAV file exceeding 4294967295 bytes")