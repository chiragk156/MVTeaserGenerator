#!/usr/bin/env python
# coding: utf-8

# In[11]:


import soundfile as sf
from utility import remove_silence
import librosa
import scipy
import numpy as np
import math


# In[12]:


audio_file = 'Quit_Playing_Games.wav'

data, fs = remove_silence(audio_file, 0.0001)


# In[13]:


def lpc_to_lpcc(lpc):
	lpcc=[]
	order= lpc.size-1
	lpcc.append(math.log(order))
	lpcc.append(lpcc[0])
	for i in range(2,order+1):
		sum1=0
		for j in range(1,i):
			sum1+=j/i*lpc[i-j-1]*lpcc[j]
		c= -lpc[i-1]+sum1
		lpcc.append(c)
	return lpcc

# Function to compute feature for each frame
def vocal_features(frames, SpectralFlux_frames, order):
	features_frames = []
	for i in range(len(frames)):
		features = np.zeros(order+3)
		frame = frames[i]
		lpc = librosa.core.lpc(frame, order)
		lpcc = lpc_to_lpcc(lpc)
		zcr = 0.0
		for j in range(1,frame.shape[0]):
			if (frame[j]>=0 and frame[j-1]<0) or (frame[j]<0 and frame[j-1]>=0):
			 	zcr += 1
		zcr = zcr/frame.shape[0]
		sf = SpectralFlux_frames[i]
		features[0:order+1] = lpcc
		features[order+1] = zcr
		features[order+2] = sf
		features_frames.append(features)
	return np.array(features_frames)

def SpectralFlux(X, f_s):

    # difference spectrum (set first diff to zero)
    X = np.c_[X[:, 0], X]
    # X = np.concatenate(X[:,0],X, axis=1)
    afDeltaX = np.diff(X, 1, axis=1)

    # flux
    vsf = np.sqrt((afDeltaX**2).sum(axis=0)) / X.shape[0]

    return (vsf)




# In[14]:


n_samples = data.shape[0]
# sf.write('no_silence.wav', data, fs)

# Divide audio into frames
# Frame size in ms
frame_size = 100.0
n_per_frame = int( (frame_size/1000)*fs )

frames_data = []
overlapping_rate = 0.5
order = 5


# In[15]:


f,t,Sxx = scipy.signal.spectrogram(data, fs, nperseg=n_per_frame, noverlap= int(n_per_frame*(1-overlapping_rate)))
for i in range(0, n_samples, int(n_per_frame*(1-overlapping_rate))):
	if i+n_per_frame<=n_samples:
		frames_data.append( data[i:i+n_per_frame] )

SpectralFlux_frames = SpectralFlux(Sxx, fs)
features_frames = vocal_features(frames_data, SpectralFlux_frames, order)

import pandas as pd

df= pd.DataFrame(features_frames)

print (df)


# In[ ]:


df.describe()


# In[16]:


df2= df.drop([0,1],axis=1)
print (df2)


# In[6]:


Ls=30
Tc=3
n_clusters= int((Ls)/Tc)


# In[16]:


from sklearn.preprocessing import normalize
data_scaled = normalize(df2)
data_scaled = pd.DataFrame(data_scaled)

data_scaled.head()


# In[29]:


from sklearn.cluster import AgglomerativeClustering
cluster = AgglomerativeClustering(n_clusters, affinity='euclidean', linkage='ward')  


# In[30]:


clusters=cluster.fit_predict(data_scaled)


# In[32]:


print (clusters.shape)


# In[34]:


minCluster=[24000]*10
maxCluster=[0]*10

for i in range(clusters.shape[0]):
    minCluster[clusters[i]]= min(minCluster[clusters[i]],i)
    maxCluster[clusters[i]]= max(maxCluster[clusters[i]],i)

print (minCluster)
print (maxCluster)


# In[22]:


# In[ ]:




