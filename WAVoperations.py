import math, random, ctypes

# Common to all
ERROR_NONE = 0

# CheckValidFormat
ERROR_CHUNKID = 1
ERROR_CHUNKSIZE = 2
ERROR_FORMAT = 3
ERROR_SUBCHUNK1ID = 4
ERROR_SUBCHUNK1SIZE = 5
ERROR_BIT_DEPTH_NOT_A_MULTIPLE_OF_8 = 6
ERROR_CHANNEL_COUNT_IS_ZERO = 7
ERROR_SAMPLE_RATE_IS_ZERO = 8
ERROR_BIT_DEPTH_INVALID = 9
ERROR_BYTE_RATE_INCORRECT = 10
ERROR_BLOCK_ALIGNMENT = 11
ERROR_SUBCHUNK2ID = 12
ERROR_SUBCHUNK2SIZE = 13

WaveformStart = 44

WaveformPhaseModulus = 100
WaveformBuffer = (ctypes.c_long * (360 * WaveformPhaseModulus))()

def ReadLongInt(address, ArrayIn):
  value = 0
  for BytesToShift in range (4):
    value <<= 8
    value |= (ArrayIn[(address + (3 - BytesToShift))] & 0xFF)
  return value

def WriteLongInt(address, value, ArrayIn):
  for BytesToShift in range (4):
    ArrayIn[(address + BytesToShift)] = (value & 0xFF)
    value >>= 8

def Read24Int(address, ArrayIn):
  value = 0
  for BytesToShift in range (3):
    value <<= 8
    value |= (ArrayIn[(address + (3 - BytesToShift))] & 0xFF)

def Write24Int(address, value, ArrayIn):
  for BytesToShift in range (3):
    ArrayIn[(address + BytesToShift)] = (value & 0xFF)
    value >>= 8

def ReadWordInt(address, ArrayIn):
  return ((ArrayIn[address] & 0xFF) | ((ArrayIn[(address + 1)] & 0xFF) << 8))

def WriteWordInt(address, value, ArrayIn):
  ArrayIn[address] = (value & 0xFF)
  value >>= 8
  ArrayIn[(address + 1)] = (value & 0xFF)

def ReadBitDepth(ArrayIn):
  return ReadWordInt(34, ArrayIn)
  
def CheckAudioIsUncompressed(ArrayIn):
  if ReadWordInt(20, ArrayIn) == 1:
    return True
  else:
    return False

def ReadChannelCount(ArrayIn):
  return ReadWordInt(22, ArrayIn)

def ReadSampleRate(ArrayIn):		
  return ReadLongInt(24, ArrayIn)

def ReadSampleCount(ArrayIn):
  return int(ReadLongInt(40, ArrayIn) / int(ReadBitDepth(ArrayIn) / 8) / ReadChannelCount(ArrayIn))

def CheckValidFormat(ArrayIn):
  if ArrayIn[0] != 0x52 or ArrayIn[1] != 0x49 or ArrayIn[2] != 0x46 or ArrayIn[3] != 0x46:
    return ERROR_CHUNKID
  if ArrayIn[8] != 0x57 or ArrayIn[9] != 0x41 or ArrayIn[10] != 0x56 or ArrayIn[11] != 0x45:
    return ERROR_FORMAT
  if ArrayIn[12] != 0x66 or ArrayIn[13] != 0x6D or ArrayIn[14] != 0x74 or ArrayIn[15] != 0x20:
    return ERROR_SUBCHUNK1ID
  if ReadLongInt(16, ArrayIn) != 16:
    return ERROR_SUBCHUNK1SIZE
  if (ReadBitDepth(ArrayIn) % 8) != 0:
    return ERROR_BIT_DEPTH_NOT_A_MULTIPLE_OF_8
  if ReadWordInt(22, ArrayIn) == 0:
    return ERROR_CHANNEL_COUNT_IS_ZERO
  if ReadLongInt(24, ArrayIn) == 0:
    return ERROR_SAMPLE_RATE_IS_ZERO
  if ReadBitDepth(ArrayIn) != 8 and ReadBitDepth(ArrayIn) != 16 and ReadBitDepth(ArrayIn) != 24:
    return ERROR_BIT_DEPTH_NOT_8_16_24
  if ReadLongInt(28, ArrayIn) != (ReadSampleRate(ArrayIn) * ReadChannelCount(ArrayIn) * int(ReadBitDepth(ArrayIn) / 8)):
    return ERROR_BYTE_RATE_INCORRECT
  if ReadWordInt(32, ArrayIn) != (ReadChannelCount(ArrayIn) * int(ReadBitDepth(ArrayIn) / 8)):
    return ERROR_BLOCK_ALIGNMENT
  if ArrayIn[36] != 0x64 or ArrayIn[37] != 0x61 or ArrayIn[38] != 0x74 or ArrayIn[39] != 0x61:
    return ERROR_SUBCHUNK2ID
  if ReadLongInt(40, ArrayIn) < (len(ArrayIn) - WaveformStart):
    return ERROR_SUBCHUNK2SIZE
  if (len(ArrayIn) - 8) < ReadLongInt(4, ArrayIn):
    return ERROR_CHUNKSIZE
  return ERROR_NONE

def WriteHeader(ChannelCount, SampleRate, SampleCount, BitDepth, ArrayIn):
  if ChannelCount > 0 and ChannelCount < 65535 and SampleRate > 0 and (BitDepth == 8 or BitDepth == 16 or BitDepth == 24):
    # Chunk ID
    ArrayIn[0] = 0x52
    ArrayIn[1] = 0x49
    ArrayIn[2] = 0x46
    ArrayIn[3] = 0x46

    # Format
    ArrayIn[8] = 0x57
    ArrayIn[9] = 0x41
    ArrayIn[10] = 0x56
    ArrayIn[11] = 0x45

    # Subchunk 1 ID
    ArrayIn[12] = 0x66
    ArrayIn[13] = 0x6D
    ArrayIn[14] = 0x74
    ArrayIn[15] = 0x20

    WriteLongInt(16, 16, ArrayIn) # Subchunk 1 size
    WriteWordInt(34, BitDepth, ArrayIn)
    WriteWordInt(22, ChannelCount, ArrayIn)
    WriteLongInt(24, SampleRate, ArrayIn)
    WriteLongInt(28, (int(BitDepth / 8) * ChannelCount * SampleRate), ArrayIn) # byte rate
    WriteWordInt(32, (ChannelCount * int(BitDepth / 8)), ArrayIn)

    # Subchunk 2 ID
    ArrayIn[36] = 0x64
    ArrayIn[37] = 0x61
    ArrayIn[38] = 0x74
    ArrayIn[39] = 0x61

    WriteLongInt(40, (SampleCount * ChannelCount * int(BitDepth / 8)), ArrayIn) # Subchunk 2 size
    WriteLongInt(4, (4 + 8 + ReadLongInt(16, ArrayIn) + 8 + ReadLongInt(40, ArrayIn)), ArrayIn) # chunk size
    WriteWordInt(20, 1, ArrayIn) # uncompressed audio type

def CalculateFileSize(Channels, BitDepth, SampleCount):
  FileSize = (Channels * int(BitDepth / 8) * SampleCount) + WaveformStart
  if FileSize <= 4294967295:
    return FileSize
  else:
    return 0

def ReadSample(Channel, Sample, ArrayIn):
  ChannelCount = ReadChannelCount(ArrayIn)
  if Channel >= 0 and Channel < ChannelCount and Sample >= 0 and Sample < ReadSampleCount(ArrayIn):
    SampleRead = 0
    BytesPerSample = int(ReadBitDepth(ArrayIn) / 8)
    if BytesPerSample == 1:
      SampleRead = ArrayIn[(WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample))]
      SampleRead -= 128 # zero is at 128 for 8 bit WAV files to enable the use of an inexpensive DAC
    elif BytesPerSample == 2:
      SampleRead = ReadWordInt((WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample)), ArrayIn)
      if SampleRead > 32767:
        SampleRead -= 65536
    elif BytesPerSample == 3:
      SampleRead = Read24Int((WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample)), ArrayIn)
      if SampleRead > 8388607:
        SampleRead -= 16777216
    return SampleRead
  else:
    return 0

def OverwriteSample(Channel, Sample, Value, ArrayIn):
  Clipped = False
  ChannelCount = ReadChannelCount(ArrayIn)
  if Channel >= 0 and Channel < ChannelCount and Sample >= 0 and Sample < ReadSampleCount(ArrayIn):
    BytesPerSample = int(ReadBitDepth(ArrayIn) / 8)
    if BytesPerSample == 1:
      Value += 128 # zero is at 128 for 8 bit WAV files to enable the use of an inexpensive DAC
      if Value > 255:
        Value = 255
        Clipped = True
      elif Value < 0:
        Value = 0
        Clipped = True
      ArrayIn[(WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample))] = (int(Value) & 0xFF)
    elif BytesPerSample == 2:
      if Value > 32767:
        Value = 32767
        Clipped = True
      elif Value < -32768:
        Value = -32768
        Clipped = True
      WriteWordInt((WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample)), (int(Value) & 0xFFFF), ArrayIn)
    elif BytesPerSample == 3:
      if Value > 8388607:
        Value = 8388607
        Clipped = True
      elif Value < -8388608:
        Value = -8388608
        Clipped = True
      Write24Int((WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample)), (int(Value) & 0xFFFFFF), ArrayIn)
  return Clipped

def MixSample(Channel, Sample, Value, ArrayIn):
  Clipped = False
  ChannelCount = ReadChannelCount(ArrayIn)
  if Channel >= 0 and Channel < ChannelCount and Sample >= 0 and Sample < ReadSampleCount(ArrayIn):
    BytesPerSample = int(ReadBitDepth(ArrayIn) / 8)
    if BytesPerSample == 1:
      SampleRead = ReadSample(Channel, Sample, ArrayIn)
      SampleRead += Value
      if Value > 127:
        Value = 127
        Clipped = True
      elif Value < -128:
        Value = -128
        Clipped = True
      ArrayIn[(WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample))] = (int(SampleRead) & 0xFF)
    elif BytesPerSample == 2:
      SampleRead = ReadSample(Channel, Sample, ArrayIn)
      SampleRead += Value
      if Value > 32767:
        Value = 32767
        Clipped = True
      elif Value < -32768:
        Value = -32768
        Clipped = True
      WriteWordInt((WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample)), (int(SampleRead) & 0xFFFF), ArrayIn)
    elif BytesPerSample == 3:
      SampleRead = ReadSample(Channel, Sample, ArrayIn)
      SampleRead += Value
      if Value > 8388607:
        Value = 8388607
        Clipped = True
      elif Value < -8388608:
        Value = -8388608
        Clipped = True
      Write24Int((WaveformStart + (ChannelCount * Sample * BytesPerSample) + (Channel * BytesPerSample)), (int(SampleRead) & 0xFFFFFF), ArrayIn)
  return Clipped

def ReadPeak(ArrayIn):
  MaximumPeak = 0
  SampleCount = ReadSampleCount(ArrayIn)
  ChannelCount = ReadChannelCount(ArrayIn)
  BitDepth = ReadBitDepth(ArrayIn)
  MaximumValue = 127
  if BitDepth == 16:
    MaximumValue = 32767
  elif BitDepth == 24:
    MaximumValue = 8388607
  for SampleToCheck in range (SampleCount):
    for ChannelToCheck in range (ChannelCount):
      NewPeak = ReadSample(ChannelToCheck, SampleToCheck, ArrayIn)
      if NewPeak < 0:
        NewPeak *= -1
        if NewPeak > MaximumValue:
          NewPeak = MaximumValue
      if NewPeak > MaximumPeak:
        MaximumPeak = NewPeak
  return MaximumPeak

def CalculateMaximumAmplificationFactor(ArrayIn):
  BitDepth = ReadBitDepth(ArrayIn)
  MaximumValue = 127.5 # default for 8 bit
  if BitDepth == 16:
    MaximumValue = 32767.5
  elif BitDepth == 24:
    MaximumValue = 8388607.5
  MaximumPeak = ReadPeak(ArrayIn)
  if MaximumPeak != 0:
    return MaximumValue / MaximumPeak
  else: # avoid division by zero
    return 1

def TimeToSampleCount(SampleRate, TimeInSeconds):
  return (SampleRate * TimeInSeconds)

def GenerateSinewaveBuffer(BitDepth):
  MaximumValue = 127.5
  if BitDepth == 16:
    MaximumValue = 32767.5
  elif BitDepth == 24:
    MaximumValue = 8388607.5
  for PointToGenerate in range (len(WaveformBuffer)):
    CurrentPoint = (PointToGenerate / len(WaveformBuffer)) * 360
    WaveformBuffer[PointToGenerate] = int((math.sin(math.radians(CurrentPoint))) * MaximumValue)

def GeneratePositiveHaversineBuffer(BitDepth):
  MaximumValue = 127.5
  if BitDepth == 16:
    MaximumValue = 32767.5
  elif BitDepth == 24:
    MaximumValue = 8388607.5
  for PointToGenerate in range (len(WaveformBuffer)):
    CurrentPoint = (PointToGenerate / len(WaveformBuffer)) * 180
    WaveformBuffer[PointToGenerate] = int((math.sin(math.radians(CurrentPoint))) * MaximumValue)

def GenerateNegativeHaversineBuffer(BitDepth):
  MaximumValue = 127.5
  if BitDepth == 16:
    MaximumValue = 32767.5
  elif BitDepth == 24:
    MaximumValue = 8388607.5
  for PointToGenerate in range (len(WaveformBuffer)):
    CurrentPoint = (PointToGenerate / len(WaveformBuffer)) * 180
    WaveformBuffer[PointToGenerate] = int(0 - (math.sin(math.radians(CurrentPoint))) * MaximumValue)

def GenerateSquarewaveBuffer(BitDepth):
  MaximumValue = 127.5
  if BitDepth == 16:
    MaximumValue = 32767.5
  elif BitDepth == 24:
    MaximumValue = 8388607.5
  for PointToGenerate in range (int(len(WaveformBuffer) / 2)):
    WaveformBuffer[PointToGenerate] = int(MaximumValue)
  MaximumValue *= -1
  for PointToGenerate in range (int(len(WaveformBuffer) / 2)):
    WaveformBuffer[(PointToGenerate + int(len(WaveformBuffer) / 2))] = int(MaximumValue)

def GenerateTriangleWaveBuffer(BitDepth):
  MaximumValue = 127.5
  if BitDepth == 16:
    MaximumValue = 32767.5
  elif BitDepth == 24:
    MaximumValue = 8388607.5
  WaveformStep = MaximumValue / (len(WaveformBuffer) / 2)
  for PointToGenerate in range (int(len(WaveformBuffer) / 2)):
    WaveformBuffer[PointToGenerate] = int(WaveformStep * PointToGenerate)
  WaveformStep *= -1
  for PointToGenerate in range (int(len(WaveformBuffer) / 2)):
    WaveformBuffer[(PointToGenerate + int(len(WaveformBuffer) / 2))] = int(WaveformStep * PointToGenerate)

def GenerateSawtoothUpWaveBuffer(BitDepth):
  MaximumValue = 127.5
  if BitDepth == 16:
    MaximumValue = 32767.5
  elif BitDepth == 24:
    MaximumValue = 8388607.5
  WaveformStep = MaximumValue / (len(WaveformBuffer))
  for PointToGenerate in range (len(WaveformBuffer)):
    WaveformBuffer[PointToGenerate] = int(WaveformStep * PointToGenerate)

def GenerateSawtoothDownWaveBuffer(BitDepth):
  MaximumValue = 127.5
  if BitDepth == 16:
    MaximumValue = 32767.5
  elif BitDepth == 24:
    MaximumValue = 8388607.5
  WaveformStep = MaximumValue / len(WaveformBuffer)
  WaveformStep *= -1
  for PointToGenerate in range (len(WaveformBuffer)):
    WaveformBuffer[PointToGenerate] = int(WaveformStep * PointToGenerate)

def GeneratePWMwaveBuffer(BitDepth, DutyCycle):
  if (DutyCycle <= 1):
    MaximumValue = 127.5
    if BitDepth == 16:
      MaximumValue = 32767.5
    elif BitDepth == 24:
      MaximumValue = 8388607.5
    OnCycles = int(len(WaveformBuffer) * DutyCycle)
    for PointToGenerate in range (OnCycles):
      WaveformBuffer[PointToGenerate] = int(MaximumValue)
    MaximumValue *= -1
    for PointToGenerate in range (len(WaveformBuffer) - OnCycles):
      WaveformBuffer[(PointToGenerate + OnCycles)] = int(MaximumValue)

def OverwriteWithWaveform(Channel, Amplitude, ZeroVoltageOffset, DegreesOffset, WaveformPhaseReferenceStart, OverwriteStart, Duration, Frequency_in_Hz, ArrayIn):
  if WaveformPhaseReferenceStart <= OverwriteStart and Duration > 0:
    if DegreesOffset < 0:
      DegreesOffset *= -1
      DegreesOffset += 180
    SampleRate = ReadSampleRate(ArrayIn)
    WaveformPhaseReferenceStart = TimeToSampleCount(SampleRate, WaveformPhaseReferenceStart)
    OverwriteStart = int(TimeToSampleCount(SampleRate, OverwriteStart))
    Duration = TimeToSampleCount(SampleRate, Duration)
    SamplesToWrite = int((OverwriteStart - WaveformPhaseReferenceStart) + Duration)
    PointsPerStep = len(WaveformBuffer) / (SampleRate / Frequency_in_Hz)
    PointsPerStepOffset = len(WaveformBuffer) * ((DegreesOffset % 360) / 360)
    ScalingFactor = 127.5 / Amplitude
    if ReadBitDepth(ArrayIn) == 16:
      ScalingFactor = 32767.5 / Amplitude
    elif ReadBitDepth(ArrayIn) == 24:
      ScalingFactor = 8388607.5 / Amplitude
    for SampleToTransfer in range (SamplesToWrite):
      if (SampleToTransfer + WaveformPhaseReferenceStart) >= OverwriteStart:
        Value = int((WaveformBuffer[(int((PointsPerStep * SampleToTransfer) + PointsPerStepOffset) % len(WaveformBuffer))] / ScalingFactor) + ZeroVoltageOffset)
        OverwriteSample(Channel, int(WaveformPhaseReferenceStart + SampleToTransfer), Value, ArrayIn)

def MixWithWaveform(Channel, Amplitude, ZeroVoltageOffset, DegreesOffset, WaveformPhaseReferenceStart, MixStart, Duration, Frequency_in_Hz, ArrayIn):
  if WaveformPhaseReferenceStart <= MixStart and Duration > 0:
    if DegreesOffset < 0:
      DegreesOffset *= -1
      DegreesOffset += 180
    SampleRate = ReadSampleRate(ArrayIn)
    WaveformPhaseReferenceStart = TimeToSampleCount(SampleRate, WaveformPhaseReferenceStart)
    MixStart = int(TimeToSampleCount(SampleRate, MixStart))
    Duration = TimeToSampleCount(SampleRate, Duration)
    SamplesToWrite = int((MixStart - WaveformPhaseReferenceStart) + Duration)
    PointsPerStep = len(WaveformBuffer) / (SampleRate / Frequency_in_Hz)
    PointsPerStepOffset = len(WaveformBuffer) * ((DegreesOffset % 360) / 360)
    ScalingFactor = 127.5 / Amplitude
    BitDepth = ReadBitDepth(ArrayIn)
    if BitDepth == 16:
      ScalingFactor = 32767.5 / Amplitude
    elif BitDepth == 24:
      ScalingFactor = 8388607.5 / Amplitude
    for SampleToTransfer in range (SamplesToWrite):
      if (SampleToTransfer + WaveformPhaseReferenceStart) >= MixStart:
        Value = int((WaveformBuffer[(int((PointsPerStep * SampleToTransfer) + PointsPerStepOffset) % len(WaveformBuffer))] / ScalingFactor) + ZeroVoltageOffset)
        MixSample(Channel, (WaveformPhaseReferenceStart + SampleToTransfer), Value, ArrayIn)

def OverwriteWithPositivePulse(Channel, Amplitude, OverwriteStart, Duration, ArrayIn):
  if Duration > 0:
    SampleRate = ReadSampleRate(ArrayIn)
    Duration = TimeToSampleCount(SampleRate, Duration)
    OverwriteStart = TimeToSampleCount(SampleRate, OverwriteStart)
    for SampleToTransfer in range (int(Duration)):
      OverwriteSample(Channel, int(OverwriteStart + SampleToTransfer), int(Amplitude), ArrayIn)

def MixWithPositivePulse(Channel, Amplitude, MixStart, Duration, ArrayIn):
  if Duration > 0:
    SampleRate = ReadSampleRate(ArrayIn)
    Duration = TimeToSampleCount(SampleRate, Duration)
    MixStart = TimeToSampleCount(SampleRate, MixStart)
    for SampleToTransfer in range (Duration):
      MixSample(Channel, int(MixStart + SampleToTransfer), int(Amplitude), ArrayIn)

def OverwriteWithNegativePulse(Channel, Amplitude, OverwriteStart, Duration, ArrayIn):
  if Duration > 0:
    SampleRate = ReadSampleRate(ArrayIn)
    Duration = TimeToSampleCount(SampleRate, Duration)
    OverwriteStart = TimeToSampleCount(SampleRate, OverwriteStart)
    for SampleToTransfer in range (int(Duration)):
      OverwriteSample(Channel, int(OverwriteStart + SampleToTransfer), int(0 - Amplitude), ArrayIn)

def MixWithNegativePulse(Channel, Amplitude, MixStart, Duration, ArrayIn):
  if Duration > 0:
    SampleRate = ReadSampleRate(ArrayIn)
    Duration = TimeToSampleCount(SampleRate, Duration)
    MixStart = TimeToSampleCount(SampleRate, MixStart)
    for SampleToTransfer in range (int(Duration)):
      MixSample(Channel, int(MixStart + SampleToTransfer), int(0 - Amplitude), ArrayIn) 

def OverwriteWithRampUp(Channel, Amplitude, ZeroVoltageOffset, OverwriteStart, Duration, ArrayIn):
  if Duration > 0:
    SampleRate = ReadSampleRate(ArrayIn)
    WaveformStep = (Amplitude / SampleRate / Duration)
    Duration = TimeToSampleCount(SampleRate, Duration)
    OverwriteStart = TimeToSampleCount(SampleRate, OverwriteStart)
    for SampleToTransfer in range (int(Duration)):
      OverwriteSample(Channel, int(OverwriteStart + SampleToTransfer), int((SampleToTransfer * WaveformStep) + ZeroVoltageOffset), ArrayIn)

def MixWithRampUp(Channel, Amplitude, ZeroVoltageOffset, MixStart, Duration, ArrayIn):
  if Duration > 0:
    SampleRate = ReadSampleRate(ArrayIn)
    WaveformStep = (Amplitude / SampleRate / Duration)
    Duration = TimeToSampleCount(SampleRate, Duration)
    MixStart = TimeToSampleCount(SampleRate, MixStart)
    for SampleToTransfer in range (int(Duration)):
      MixSample(Channel, int(MixStart + SampleToTransfer), int((SampleToTransfer * WaveformStep) + ZeroVoltageOffset), ArrayIn)

def OverwriteWithRampDown(Channel, Amplitude, ZeroVoltageOffset, OverwriteStart, Duration, ArrayIn):
  if Duration > 0:
    SampleRate = ReadSampleRate(ArrayIn)
    WaveformStep = (Amplitude / SampleRate / Duration)
    Duration = TimeToSampleCount(SampleRate, Duration)
    OverwriteStart = TimeToSampleCount(SampleRate, OverwriteStart)
    for SampleToTransfer in range (int(Duration)):
      OverwriteSample(Channel, int(OverwriteStart + SampleToTransfer), int(0 - (SampleToTransfer * WaveformStep) + ZeroVoltageOffset), ArrayIn)

def MixWithRampDown(Channel, Amplitude, ZeroVoltageOffset, MixStart, Duration, ArrayIn):
  if Duration > 0:
    SampleRate = ReadSampleRate(ArrayIn)
    WaveformStep = (Amplitude / SampleRate / Duration)
    Duration = TimeToSampleCount(SampleRate, Duration)
    MixStart = TimeToSampleCount(SampleRate, MixStart)
    for SampleToTransfer in range (int(Duration)):
      MixSample(Channel, int(MixStart + SampleToTransfer), int(0 - (SampleToTransfer * WaveformStep) + ZeroVoltageOffset), ArrayIn)

def OverwriteWithNoise(Channel, Amplitude, ZeroVoltageOffset, OverwriteStart, Duration, ArrayIn):
  if Duration > 0:
    random.seed()
    SampleRate = ReadSampleRate(ArrayIn)
    Duration = TimeToSampleCount(SampleRate, Duration)
    OverwriteStart = TimeToSampleCount(SampleRate, OverwriteStart)
    for SampleToTransfer in range (int(Duration)):
      OverwriteSample(Channel, int(OverwriteStart + SampleToTransfer), (random.randint((ZeroVoltageOffset - Amplitude), (ZeroVoltageOffset + Amplitude)) + ZeroVoltageOffset), ArrayIn)

def MixWithNoise(Channel, Amplitude, ZeroVoltageOffset, MixStart, Duration, ArrayIn):
  if Duration > 0:
    random.seed()
    SampleRate = ReadSampleRate(ArrayIn)
    Duration = TimeToSampleCount(SampleRate, Duration)
    MixStart = TimeToSampleCount(SampleRate, MixStart)
    for SampleToTransfer in range (int(Duration)):
      MixSample(Channel, int(MixStart + SampleToTransfer), (random.randint((ZeroVoltageOffset - Amplitude), (ZeroVoltageOffset + Amplitude)) + ZeroVoltageOffset), ArrayIn)