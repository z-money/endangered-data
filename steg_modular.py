from __future__ import print_function
import imageio
import numpy as np
import numba as nb
import os, sys
import time
import cv2
import csv
from random import uniform
import argparse

def ask_for_args(args):
	args.content = input("File that holds the content to be stored:")
	args.video = input("Video file:")
	args.write = input("Output video file:")
	args.data = input("Optional data file:")
	args.delim = input("Delimiter:")
	return args

parser = argparse.ArgumentParser(description='Do some steganography')

parser.add_argument('--content', help='file name that holds the content')
parser.add_argument('--video', help='the video you want to hide the content in')
parser.add_argument('--write', default=False)
parser.add_argument('--data', default=False, help='the data file with, like, methane data, as a dsv')
parser.add_argument('--delim', default=',', help='delimiter for the dsv')
args = parser.parse_args()

if(args.content is None):
	args = ask_for_args(args)

def progress(frameCount, vidLen, out = True):
	percent = float(frameCount)/float(vidLen) * 100
	if(out):
		sys.stdout.write('\r%.2f%%' % percent)
		sys.stdout.flush()
	return percent

@nb.njit
def pixel_should_get_data(pixel, frameCount, data, randoms):
	return True

@nb.njit
def get_char(content, contentCount):
	char = content[contentCount]
	contentCount += 1
	if(contentCount >= len(content)):
		contentCount = 0
	return char

@nb.njit
def im_func(image, frameCount, content, contentCount, data, randoms):
	height, width, layers = image.shape
	for row in range(height-1):
		for col in range(width-1):
			pixel = image[row][col]
			if(pixel_should_get_data(pixel, frameCount, data, randoms)):# and data[frameCount] > randoms[frameCount*row+col]):
				pixel[0] += get_char(content, contentCount) + 10
				pixel[1] += get_char(content, contentCount) + 0
				pixel[2] += get_char(content, contentCount) + 0
				if(pixel[0] > 255):
					pixel[0] -= 255
				if(pixel[1] > 255):
					pixel[1] -= 255
				if(pixel[2] > 255):
					pixel[2] -= 255
	return image

out = cv2.VideoWriter('videos\clouds.mp4',cv2.VideoWriter_fourcc(*'MJPG'),24.00, (1280,720))
filename = args.video

vid = imageio.get_reader(filename, 'ffmpeg')
all_start = time.time()

content = []
with open(args.content) as f:
	lines = f.readlines()
for line in lines:
	for c in line:
		content.append(ord(c))

data = None
if(data != False):
	with open(args.data) as f:
		reader = csv.reader(f, delimiter = args.delim)

		for row in reader:
			row[3] = float(row[3])
			if(data is None):
				data = [row[3]]
			else:
				data.append(row[3])

randoms = []
for i in range(0,1024*768):
	randoms.append(uniform(330,400.0))

contentCount = 0
for frameCount in range(len(vid)):
	if(frameCount >= len(vid)):
		break
	image = vid.get_data(frameCount)
	height, width, layers = image.shape

	image = im_func(image, frameCount, content, contentCount, data, randoms)

	b, g, r = cv2.split(image)
	image = cv2.merge([r,g,b])
	out.write(image)
	progress(frameCount, len(vid))

out.release()
print('total time: '+str(time.time()-all_start)+'s')