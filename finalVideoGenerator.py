from moviepy.editor import *
import numpy as np

def videoGeneration(song_title, segmentList, beatDist):
  video = VideoFileClip(song_title + "_cropped.avi")

  finalClip= []
  initClip= video.subclip(segmentList[0][0],segmentList[0][1])
  finalClip.append(initClip)
  padding = beatDist
  idx = initClip.duration - padding
  for i in range(1,len(segmentList)):
    currClip = video.subclip(segmentList[i][0],segmentList[i][1])
    finalClip.append(currClip.set_start(idx).crossfadein(padding))
    idx += currClip.duration - padding

  txt_clip = (TextClip(song_title.upper().replace("_", " ") + "\n COMING SOON",fontsize=25,color='white', font='Times-Bold')
              .set_position('center')
              .set_duration(5) )
  finalClip.append(txt_clip.set_start(idx-5+padding).crossfadein(padding))
  finalVideo= CompositeVideoClip(finalClip)

  background_music = AudioFileClip(song_title+ "_segmented.mp3")
  finalVid = finalVideo.set_audio(background_music)
  drivePath= '/content/drive/My Drive/mvs/'
  finalVid.write_videofile(drivePath + 'teasers/' + song_title+ "_Final.mp4", fps=24)