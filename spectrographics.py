import math, wave, array
import numpy as np
import os, sys
from PIL import Image
import progressbar
import random
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("-M","--max", type=int, default=4000, help="Maximum frequency used")
parser.add_argument("-m","--min", type=int, default=10, help="Minimum frequency used")
parser.add_argument("-i","--invert", type=int, default=0, help="invert image colors")
parser.add_argument("-s","--samplerate", type=int, default=44100, help="sample rate")
parser.add_argument("-o","--output", type=str, default="SpectrogramWave.wav", help="output file name")
parser.add_argument("-d","--duration", type=float, default=.03, help="burst duration .4seconds by default")
parser.add_argument("-p","--maxpixelwidth", type=int, default=256, help="rescales any input image to the maximum width allowed")
parser.add_argument("-f","--inputfile", type=str,  help="input image file",  required=True)

args = parser.parse_args()

sampleRate = args.samplerate # of samples per second (standard)
invert = args.invert
stepduration = args.duration #looked good with .04
maxpixelwidth  = args.maxpixelwidth
maximum_frequency = args.max
minimum_frequency = args.min

def genSine(freq=2000, volume=100,duration=3, phase=0, sampleRate=88200):
	data = []
	numSamplesPerCyc = sampleRate / float(freq)
	numSamples = int(sampleRate * duration)
	for i in range(numSamples):
		sample = math.sin(math.pi * 2.0 * ((i+phase) % numSamplesPerCyc) / float(numSamplesPerCyc)) * ((32767.0/100.0) * volume)
		data.append(int(sample))
	return (np.array(data),i+phase)


f = wave.open(args.output, 'w')
f.setparams((1, 2, sampleRate, int(sampleRate * stepduration), "NONE", "Uncompressed"))
im = Image.open(args.inputfile).convert('L')
width, height = im.size

if width > maxpixelwidth:
	r = (float(maxpixelwidth)/float(width))
	im = im.resize((int(width*r),int(height*r)))
	width, height = im.size

lastphase = [0] * width
for i in xrange(width): #randomize the initial phases
	lastphase[i] = random.randint(0,360)

step = ((maximum_frequency - minimum_frequency)/float(width))

bar = progressbar.ProgressBar(maxval=(width*height),widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()
for h in xrange(height):
	data = []
	for w in xrange(width):
		vol =  (100.0/255.0) * im.getpixel((w, h))
		if invert:
			vol = 100.0 - vol
		(sw,p) = genSine(minimum_frequency+(w*step ),volume=vol, phase=lastphase[w] ,duration=stepduration, sampleRate=sampleRate)
		data.append(sw.astype(int))
		lastphase[w] = p
		try:
			bar.update((height * h) + w)
		except:
			pass
	data = sum(data)/float(len(data))

	f.writeframes(array.array('h',[int(x) for x in data]).tostring())
f.close()
print ""
