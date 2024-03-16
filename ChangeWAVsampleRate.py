import argparse, struct, sys, os, ctypes, WAVoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--wavfilein", help="WAV file to convert")
  parser.add_argument("--wavfileout", help="Converted WAV file output")
  parser.add_argument("--sps", type=int, default=0, help="Sample rate to convert to")
  args = parser.parse_args()
  wavfilenamein = args.wavfilein
  wavfilenameout = args.wavfileout
  OutputSampleRate = args.sps
  ValidParameters = True

  if not args.wavfilein:
    ValidParameters = False
    print("ERROR: WAV input file not specified")
  elif not os.path.isfile(wavfilenamein):
    ValidParameters = False
    print("ERROR:", wavfilenamein, "not found")
  if not args.wavfileout:
    ValidParameters = False
    print("ERROR: WAV output file not specified")
  if OutputSampleRate <= 0:
    ValidParameters = False
    print("ERROR: Samples per second not specified or is zero or negative")

  if ValidParameters == True:
    wavinputfilesize = os.path.getsize(wavfilenamein)
    wavinputbuffer = (ctypes.c_byte * wavinputfilesize)()
    wavinputfile = open(wavfilenamein, 'rb')
    wavinputbuffer = wavinputfile.read(wavinputfilesize)
    Channels = WAVoperations.ReadChannelCount(wavinputbuffer)
    BitDepth = WAVoperations.ReadBitDepth(wavinputbuffer)
    InputSampleRate = WAVoperations.ReadSampleRate(wavinputbuffer)
    InputSampleCount = WAVoperations.ReadSampleCount(wavinputbuffer)
    print("Channels:", Channels)
    print("Bit depth:", BitDepth)
    print("Sample rate:", InputSampleRate)
    print("Sample count:", InputSampleCount)
    ErrorCode = WAVoperations.CheckValidFormat(wavinputbuffer)
    wavinputfile.close()
    OutputSampleCount = 0
    wavoutputfilesize = 0
    if ErrorCode != WAVoperations.ERROR_NONE:
      ValidParamters = False
      print("Error code", ErrorCode, "- refer to WAVoperations.py for definition")
    elif WAVoperations.CheckAudioIsUncompressed(wavinputbuffer) == False:
      ValidParamters = False
      print("ERROR: Input file is compressed")
    if ValidParameters == True:
      OutputSampleCount = int((InputSampleCount * OutputSampleRate) / InputSampleRate)
      if OutputSampleCount < 1:
        ValidParameters = False
        print("ERROR: Output file will not have a minimum of one sample")
    if ValidParameters == True:
      wavoutputfilesize = WAVoperations.CalculateFileSize(Channels, BitDepth, OutputSampleCount)
      if wavoutputfilesize == 0:
        ValidParameters = False
        print("ERROR: Attempt to create WAV file exceeding 4294967295 bytes")
    if ValidParameters == True:
      wavoutputbuffer = (ctypes.c_byte * wavoutputfilesize)()
      WAVoperations.WriteHeader(Channels, OutputSampleRate, OutputSampleCount, BitDepth, wavoutputbuffer)
      InputSeekFactor = InputSampleRate / OutputSampleRate
      for SampleToTransfer in range (OutputSampleCount):
        InputPoint = int(SampleToTransfer * InputSeekFactor)
        for ChannelToTransfer in range (Channels):
          PointToWrite = WAVoperations.ReadSample(ChannelToTransfer, InputPoint, wavinputbuffer)
          WAVoperations.OverwriteSample(ChannelToTransfer, SampleToTransfer, PointToWrite, wavoutputbuffer)
      wavoutputfile = open(wavfilenameout, 'wb')
      wavoutputfile.write(wavoutputbuffer)
      wavoutputfile.close()
      print("Conversion complete")