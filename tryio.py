from __future__ import print_function
import imageio
import numpy as np
import numba as nb
import os, sys
import time
import cv2
import csv
from random import uniform

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
			if(pixel[2] > 200):# and data[frameCount] > randoms[frameCount*row+col]):
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

out = cv2.VideoWriter('output\output_video.avi',cv2.VideoWriter_fourcc(*'MJPG'),24.00, (1280,720))
filename = 'videos\clouds.mp4'

vid = imageio.get_reader(filename, 'ffmpeg')
all_start = time.time()

content = []
with open('data\co2.tsv') as f:
	lines = f.readlines()
for line in lines:
	for c in line:
		content.append(ord(c))

data = None
with open('data\co2.tsv') as f:
	reader = csv.reader(f, delimiter = '\t')

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
	if(frameCount >= len(data)):
		break
	image = vid.get_data(frameCount)
	height, width, layers = image.shape
	start = time.time()
	image = im_func(image, frameCount, content, contentCount, data, randoms)
	# print(image.tostring())
	b, g, r = cv2.split(image)
	image = cv2.merge([r,g,b])
	out.write(image)
	dur = time.time()-start

	print(str(dur)+'s')
	# imageio.imwrite('output/out'+str(frameCount)+'.png', image[:, :, :])

out.release()
print('total time: '+str(time.time()-all_start)+'s')