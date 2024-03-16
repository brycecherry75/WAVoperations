import argparse, csv, os, ctypes, WAVoperations

if __name__ == "__main__":
  parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  parser.add_argument("--wavfile", help="WAV file input")
  parser.add_argument("--channel", type=int, default=0, help="Channel of WAV file to convert (defualt: 0)")
  parser.add_argument("--cfile", help="C file output")
  args = parser.parse_args()
  WaveformFile = args.wavfile
  WaveformChannel = args.channel

  ValidParameters = True
  if not args.wavfile:
    ValidParameters = False
    print("ERROR: WAV input file not specified")
  elif not os.path.isfile(WaveformFile):
    ValidParameters = False
    print("ERROR:", WaveformFile, "not found")
  if not args.cfile:
    ValidParameters = False
    print("ERROR: C output file not specified")

  if ValidParameters == True:
    Cfilename = args.cfile
    WAVfileSize = os.path.getsize(WaveformFile)
    WAVbuffer = (ctypes.c_byte * WAVfileSize)()
    WAVfile = open(WaveformFile, 'rb')
    WAVbuffer = WAVfile.read(WAVfileSize)
    WAVfile.close()    

    ErrorCode = WAVoperations.CheckValidFormat(WAVbuffer)
    if ErrorCode == WAVoperations.ERROR_NONE:
      Channels = WAVoperations.ReadChannelCount(WAVbuffer)
      BitDepth = WAVoperations.ReadBitDepth(WAVbuffer)
      SampleRate = WAVoperations.ReadSampleRate(WAVbuffer)
      SampleCount = WAVoperations.ReadSampleCount(WAVbuffer)
      if WaveformChannel >= Channels:
        print("ERROR: Waveform channel out of range")
      elif WaveformChannel < 0:
        print("ERROR: Waveform channel is negative")
      elif WAVoperations.CheckAudioIsUncompressed(WAVbuffer) == False:
        print("ERROR: Waveform file is compressed")
      else:

        with open(Cfilename, 'w', newline='') as csvfile:
          WAVwriter = csv.writer(csvfile, delimiter='*',quotechar='|', quoting=csv.QUOTE_NONE)

          SampleRateString = "const unsigned long SampleRate = "
          SampleRateString += str(SampleRate)
          SampleRateString += ";"
          WAVwriter.writerow(SampleRateString)

          FirstString = "const unsigned long Waveform_Channel_"
          FirstString += str(WaveformChannel)
          FirstString += "_SampleCount = "
          FirstString += str(SampleCount)
          FirstString += ";"
          WAVwriter.writerow(FirstString)

          SecondString = "const "
          NegativeOffset = 256
          if BitDepth == 8:
            SecondString += "byte "
          elif BitDepth == 16:
            SecondString += "word "
            NegativeOffset = 65536
          elif BitDepth == 24:
            SecondString += "unsigned long "
            NegativeOffset = 16777216
          SecondString += "Waveform_Channel_"
          SecondString += str(WaveformChannel)
          SecondString += "[Waveform_Channel_"
          SecondString += str(WaveformChannel)
          SecondString += "_SampleCount] = {"
          WAVwriter.writerow(SecondString)

          if SampleCount > 16:
            for LineToPrint in range(int(SampleCount / 16)):
              WAVvalue = WAVoperations.ReadSample(WaveformChannel, (LineToPrint * 16), WAVbuffer)
              if WAVvalue < 0:
                WAVvalue += NegativeOffset
              CurrentLine = str(hex(WAVvalue))
              CurrentLine += ", "
              for ValueToWrite in range(15):
                WAVvalue = WAVoperations.ReadSample(WaveformChannel, (LineToPrint * 16) + ValueToWrite + 1, WAVbuffer)
                if WAVvalue < 0:
                  WAVvalue += NegativeOffset
                CurrentLine += str(hex(WAVvalue))
                if (ValueToWrite < 14):
                  CurrentLine += ", "
              if SampleCount > 16:
                CurrentLine += ", "
              WAVwriter.writerow([CurrentLine])
            if (SampleCount % 16) != 0:
              WAVvalue = WAVoperations.ReadSample(WaveformChannel, (LineToPrint * 16) + ValueToWrite, WAVbuffer)
              if WAVvalue < 0:
                WAVvalue += NegativeOffset
              CurrentLine = str(hex(WAVvalue))
              if (SampleCount % 16) != 1:
                CurrentLine += ", "
                for ValueToWrite in range((SampleCount % 16) - 1):
                  WAVvalue = WAVoperations.ReadSample(WaveformChannel, (LineToPrint * 16) + ValueToWrite + 1, WAVbuffer)
                  if WAVvalue < 0:
                    WAVvalue += NegativeOffset
                  CurrentLine += str(hex(WAVvalue))
                  if (ValueToWrite < ((SampleCount % 16) - 2)):
                    CurrentLine += ", "
              WAVwriter.writerow([CurrentLine])
          else:
            WAVvalue = WAVoperations.ReadSample(WaveformChannel, 0, WAVbuffer)
            if WAVvalue < 0:
              WAVvalue *= -1
            CurrentLine = str(hex(WAVvalue))
            if SampleCount > 1:
              CurrentLine += ", "
              for ValueToWrite in range((SampleCount - 1)):
                WAVvalue = WAVoperations.ReadSample(WaveformChannel, 1 + ValueToWrite, WAVbuffer)
                if WAVvalue < 0:
                  WAVvalue *= -1
                CurrentLine += str(hex(WAVvalue))
                if (ValueToWrite < (SampleCount - 2)):
                  CurrentLine += ", "
            WAVwriter.writerow([CurrentLine])

          WAVwriter.writerow(['};']) # terminate it

        CfileSize = os.path.getsize(Cfilename)
        CfileBuffer_origin = (ctypes.c_byte * CfileSize)()
        Cfile_origin = open(Cfilename, 'rb')
        CfileBuffer_origin = Cfile_origin.read(CfileSize)
        Cfile_origin.close()
        UnwantedSpaceCount = 0
        for ByteToCheck in range (CfileSize):
          if CfileBuffer_origin[ByteToCheck] == 0x2A:
            UnwantedSpaceCount += 1
        CfileBuffer_destination = (ctypes.c_byte * (CfileSize - UnwantedSpaceCount - 2))()
        UnwantedSpaceCount = 0
        for ByteToTransfer in range (CfileSize - 2):
          if CfileBuffer_origin[(ByteToTransfer)] != 0x2A:
            CfileBuffer_destination[(ByteToTransfer - UnwantedSpaceCount)] = CfileBuffer_origin[ByteToTransfer]
          else:
            UnwantedSpaceCount += 1
        Cfile_destination = open(Cfilename, 'wb')
        Cfile_destination.write(CfileBuffer_destination)
        Cfile_destination.close()   

        print("WAV to C conversion complete")

    else:
      print("Error code", ErrorCode, "- refer to WAVoperations.py for definition")