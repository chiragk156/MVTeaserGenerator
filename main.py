from moviepy.editor import *
import sys
from segmentExtractor import extract_segments
from video_crop import crop_video
from finalVideoGenerator import videoGeneration

song_name = sys.argv[1]
print ("Song Name: " + song_name)
video_filepath = song_name + '.mp4'
print ("Video Path: " + video_filepath)
video = VideoFileClip(video_filepath)
audio = video.audio
audio.write_audiofile(song_name+'.wav')
print ("Extracted audio and video components")
mixedFile, finalSegmentList, beatDist = extract_segments(song_name)
print ("Audio Segments Extraction successfull")
crop_video(video_filepath, song_name+'_cropped.avi')
print ("Video cropping successfull")
videoGeneration(song_name, finalSegmentList, beatDist)
print ("Final Video Generated")