import argparse, struct, sys, os, ctypes, WAVoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--wavfilein", help="WAV file to convert")
  parser.add_argument("--wavfileout", help="Converted WAV file output")
  args = parser.parse_args()
  wavfilenamein = args.wavfilein
  wavfilenameout = args.wavfileout
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

  if ValidParameters == True:
    wavinputfilesize = os.path.getsize(wavfilenamein)
    wavinputbuffer = (ctypes.c_byte * wavinputfilesize)()
    wavinputfile = open(wavfilenamein, 'rb')
    wavinputbuffer = wavinputfile.read(wavinputfilesize)
    Channels = WAVoperations.ReadChannelCount(wavinputbuffer)
    BitDepth = WAVoperations.ReadBitDepth(wavinputbuffer)
    SampleRate = WAVoperations.ReadSampleRate(wavinputbuffer)
    SampleCount = WAVoperations.ReadSampleCount(wavinputbuffer)
    print("Channels:", Channels)
    print("Bit depth:", BitDepth)
    print("Sample rate:", SampleRate)
    print("Sample count:", SampleCount)
    ErrorCode = WAVoperations.CheckValidFormat(wavinputbuffer)
    wavinputfile.close()
    wavoutputfilesize = 0
    if ErrorCode != WAVoperations.ERROR_NONE:
      ValidParamters = False
      print("Error code", ErrorCode, "- refer to WAVoperations.py for definition")
    elif WAVoperations.CheckAudioIsUncompressed(wavinputbuffer) == False:
      ValidParamters = False
      print("ERROR: Input file is compressed")
    if ValidParameters == True:
      wavoutputfilesize = WAVoperations.CalculateFileSize(Channels, BitDepth, SampleCount)
      if wavoutputfilesize == 0:
        ValidParameters = False
        print("ERROR: Attempt to create WAV file exceeding 4294967295 bytes")
    if ValidParameters == True:
      wavoutputbuffer = (ctypes.c_byte * wavoutputfilesize)()
      WAVoperations.WriteHeader(Channels, SampleRate, SampleCount, BitDepth, wavoutputbuffer)
      MaximumPeak = WAVoperations.ReadPeak(wavinputbuffer)
      print("Maximum peak is", MaximumPeak)
      AmplificationFactor = WAVoperations.CalculateMaximumAmplificationFactor(wavinputbuffer)
      print("Amplification factor is", AmplificationFactor)
      for SampleToTransfer in range (SampleCount):
        for ChannelToTransfer in range (Channels):
          PointToWrite = WAVoperations.ReadSample(ChannelToTransfer, SampleToTransfer, wavinputbuffer)
          PointToWrite *= AmplificationFactor
          WAVoperations.OverwriteSample(ChannelToTransfer, SampleToTransfer, int(PointToWrite), wavoutputbuffer)
      wavoutputfile = open(wavfilenameout, 'wb')
      wavoutputfile.write(wavoutputbuffer)
      wavoutputfile.close()
      print("Processing complete")