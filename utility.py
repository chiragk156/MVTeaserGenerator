import soundfile as sf
import sys
import numpy as np
import matplotlib.pyplot as plt 

# Function to compute STE for each frame
def STE(data):
	ste = []
	for frame in data:
		e = 0.0
		for i in frame:
			e += i*i
		ste.append(e/frame.shape[0])
	return ste

def remove_silence(audio_file, ste_threshold, plot=False):
	# Read audio file
	data, fs = sf.read( audio_file )
	if len(data.shape)>1:
		data = (data[:,0]+data[:,1])/2.0
	n_samples = data.shape[0]

	# Divide audio into frames
	# Frame size in ms
	frame_size = 40.0
	n_per_frame = int( (frame_size/1000)*fs )
	frames_data = []
	# 50% overlapping
	for i in range(0, n_samples, int(n_per_frame/2)):
		frames_data.append( data[i:min(n_samples, i+n_per_frame)] )

	# STE for each frame
	ste_frames = STE(frames_data)
	# Plot STE vs frame
	x = [ i*(frame_size/2000) for i in range(len(frames_data))]
	if plot:
		plt.plot(x, ste_frames)
		plt.xlabel('time')
		plt.ylabel('STE')
		plt.title('Input Audio')
		plt.show()

	# Remove silent frames
	output_frame_nos = []
	for i in range(0, len(frames_data)):
		if ste_frames[i] > ste_threshold:
			output_frame_nos.append(i)

	output_data_indices = set()
	for i in output_frame_nos:
		for j in range(i*int(n_per_frame/2),min(n_samples, i*int(n_per_frame/2)+n_per_frame)):
			output_data_indices.add(j)

	output_data_indices = list(output_data_indices)
	output_data_indices.sort()
	output_data = data[output_data_indices]
	if plot:
		sf.write('task1_no_silence.wav', output_data, fs)
		print('Output is stored in current dir: task1_no_silence.wav')

	# Plot after removing silence
	frames_data = []
	n_samples = output_data.shape[0]
	for i in range(0, n_samples, int(n_per_frame/2)):
		frames_data.append( output_data[i:min(n_samples, i+n_per_frame)] )

	# STE for each frame
	ste_frames = STE(frames_data)
	x = [ i*(frame_size/2000) for i in range(len(frames_data))]
	if plot:
		plt.plot(x, ste_frames)
		plt.xlabel('time')
		plt.ylabel('STE')
		plt.title('Output Audio')
		plt.show()
	return output_data, fs