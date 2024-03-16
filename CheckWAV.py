import argparse, struct, sys, os, ctypes, WAVoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--wavfile", help="WAV file to check")
  args = parser.parse_args()
  wavfilename = args.wavfile
  if args.wavfile:
    if os.path.isfile(wavfilename):
      wavfilesize = os.path.getsize(wavfilename)
      wavbuffer = (ctypes.c_byte * wavfilesize)()
      wavfile = open(wavfilename, 'rb')
      wavbuffer = wavfile.read(wavfilesize)
      Channels = WAVoperations.ReadChannelCount(wavbuffer)
      BitDepth = WAVoperations.ReadBitDepth(wavbuffer)
      SampleRate = WAVoperations.ReadSampleRate(wavbuffer)
      SampleCount = WAVoperations.ReadSampleCount(wavbuffer)
      print("Channels:", Channels)
      print("Bit depth:", BitDepth)
      print("Sample rate:", SampleRate)
      print("Sample count:", SampleCount)
      print("Expected file size:", WAVoperations.CalculateFileSize(Channels, BitDepth, SampleCount))
      if WAVoperations.CheckAudioIsUncompressed(wavbuffer) == True:
        print("File is uncompressed and therefore suitable for WAVoperations")
      else:
        print("File is compressed and therefore unsuitable for WAVoperations")
      ErrorCode = WAVoperations.CheckValidFormat(wavbuffer)
      wavfile.close()
      if ErrorCode == WAVoperations.ERROR_NONE:
        print("No errors found")
      else:
        print("Error code", ErrorCode, "- refer to WAVoperations.py for definition")
    else:
      print("ERROR:", wavfile, "not found")
  else:
    print("ERROR: WAV file not specified")