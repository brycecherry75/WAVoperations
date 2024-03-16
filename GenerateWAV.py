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
      Channels = WAVoperations.ReadChannelCount(wavbuffer)
      BitDepth = WAVoperations.ReadBitDepth(wavbuffer)
      SampleRate = WAVoperations.ReadSampleRate(wavbuffer)
      SampleCount = WAVoperations.ReadSampleCount(wavbuffer)
      print("Channels:", Channels)
      print("Bit depth:", BitDepth)
      print("Sample rate:", SampleRate)
      print("Sample count:", SampleCount)
      print("Expected file size:", FileSize)
      if WAVoperations.CheckAudioIsUncompressed(wavbuffer) == True:
        print("File is uncompressed and therefore suitable for WAVoperations")
      else:
        print("File is compressed and therefore unsuitable for WAVoperations")
      ErrorCode = WAVoperations.CheckValidFormat(wavbuffer)
      wavfile = open(wavfilename, 'wb')
      wavfile.write(wavbuffer)
      wavfile.close()
      if ErrorCode == WAVoperations.ERROR_NONE:
        print("No errors found")
      else:
        print("Error code", ErrorCode, "- refer to WAVoperations.py for definition")
    else:
      print("ERROR: Attempt to create WAV file exceeding 4294967295 bytes")