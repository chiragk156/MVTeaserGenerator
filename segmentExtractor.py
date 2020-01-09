from __future__ import print_function
import msaf
from pydub import AudioSegment
import librosa
import numpy as np

def extract_segments(song_name):
  file_format= ".wav"
  audio_file = song_name + file_format
  # 2. Segment the file using the default MSAF parameters (this might take a few seconds)
  boundaries, labels = msaf.process(audio_file, boundaries_id="olda", labels_id="scluster")
  labels= [int(i) for i in labels]
  segCount=0
  currIndex=0
  firstSegLen=0
  usedLabels=[0]*5


  while (firstSegLen<5):
      lbound= boundaries[currIndex]
      rbound= boundaries[currIndex+1]
      segLen= rbound-lbound
      firstSegLen+=segLen
      firstRt=rbound
      currIndex+=1
      usedLabels[labels[currIndex]]=1
      
  segmentList=[]
  segmentList.append((0,firstRt))
  while (currIndex<len(labels)):
      if (usedLabels[labels[currIndex]]==0):
          lbound= boundaries[currIndex]
          rbound= boundaries[currIndex+1]
          segLen= rbound-lbound
          if (segLen>15):
              segmentList.append((lbound,rbound))
              currIndex+=1
          else:
              if (currIndex!=len(labels)-1):
                  if (labels[currIndex]==labels[currIndex+1]):
                      rbound= boundaries[currIndex+2]
                      segLen= rbound-lbound
                      if (segLen>15):
                          segmentList.append((lbound,rbound))
                          currIndex+=2
      currIndex+=1


  y, sr = librosa.load(audio_file)
  tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
  beatsList = librosa.frames_to_time(beats, sr=sr)

  fourBeatsList= beatsList[3::4]
  beatDist= fourBeatsList[1]- fourBeatsList[0]
  for i in range(100):
    fourBeatsList= np.append(fourBeatsList,fourBeatsList[-1]+ beatDist)

  sound = AudioSegment.from_file(audio_file)
  totalLen=0
  for i in range(len(segmentList)):
    totalLen+= segmentList[i][1]-segmentList[i][0]
  songLen= len(sound)/1000.0
  if (totalLen<=35):
    segmentList.append((songLen-23,songLen-3))

  def closest(lst, K):
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]
  newSegmentList=[]
  for i in range(len(segmentList)):
    start= segmentList[i][0]
    end= segmentList[i][1]
    newStart = closest(fourBeatsList, start)
    newEnd = closest(fourBeatsList, end)
    if (i==0):
      newStart=0
    newSegmentList.append((newStart,newEnd))

  mixedFile= sound[newSegmentList[0][0]*1000:newSegmentList[0][1]*1000]
  finalSegmentList=[]
  totalTime=newSegmentList[0][1]-newSegmentList[0][0]
  finalSegmentList.append(newSegmentList[0])
  currIter=1
  while (totalTime<=55):
    if (currIter== len(newSegmentList)):
      break
    totalTime+=newSegmentList[currIter][1]-newSegmentList[currIter][0]
    finalSegmentList.append(newSegmentList[currIter])
    currSound= sound[newSegmentList[currIter][0]*1000:newSegmentList[currIter][1]*1000]
    mixedFile=mixedFile.append(currSound, crossfade=beatDist*1000)
    currIter+=1

  lastStart= len(sound)/1000.0-5
  lastEnd = len(sound)/1000.0
  lastStart= closest(fourBeatsList,lastStart)
  finalSegmentList.append((lastStart,lastEnd))
  lastEnd= closest(fourBeatsList,lastEnd)
  lastSound= sound[lastStart*1000:]
  mixedFile=mixedFile.append(lastSound, crossfade= beatDist*1000)
  mixedFile.export(song_name + '_segmented.mp3', format="mp3")
  print ("Final Audio Segments Obtained: ")
  print (finalSegmentList)
  return (mixedFile, finalSegmentList, beatDist)