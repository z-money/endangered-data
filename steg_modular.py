from __future__ import print_function
import imageio
import numpy as np
import numba as nb
import os, sys
import time
import cv2
import csv
from random import uniform, randint
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
parser.add_argument('--putText', default=False, action='store_true')
args = parser.parse_args()

if(args.content is None):
	args = ask_for_args(args)

def progress(frameCount, vidLen, out = True):
	percent = float(frameCount)/float(vidLen) * 100
	if(out):
		sys.stdout.write('\r%.2f%%' % percent)
		sys.stdout.flush()
	return percent

# @nb.njit
# def pixel_should_get_data(pixel, frameCount, data, randoms, row, col, vidLen, width):
# 	if(pixel[2] < randoms*frameCount/4 and data[int(frameCount/vidLen*len(data))]+frameCount/2 > randint(300,400)):
# 		return True
# 	return False
@nb.njit
def pixel_should_get_data(pixel, frameCount, data, randoms, row, col, vidLen, width):
	if pixel[2] < randoms*((data[int(float(frameCount)/float(vidLen)*len(data))]-338)/62 * 255):
		return True
	return False

@nb.njit
def get_char(content, contentCount):
	char = content[contentCount]
	contentCount += 1
	if(contentCount >= len(content)):
		contentCount = 0
	return char, contentCount

@nb.njit
def im_func(image, frameCount, content, contentCount, data, randoms, vidLen):
	height, width, layers = image.shape
	paragraph = []
	for row in range(height):
		for col in range(width):
			randoms = randint(0,1)
			pixel = image[row][col]
			if(pixel_should_get_data(pixel, frameCount, data, randoms, row, col, vidLen, width)):# and data[frameCount] > randoms[frameCount*row+col]):
				a, contentCount = get_char(content, contentCount)
				b, contentCount = get_char(content, contentCount)
				c, contentCount = get_char(content, contentCount)
				paragraph.append(a)
				paragraph.append(b)
				paragraph.append(c)

				pixel[0] += a + 10
				pixel[1] += b + 0
				pixel[2] += c + 0
				if(pixel[0] > 255):
					pixel[0] -= 255
				if(pixel[1] > 255):
					pixel[1] -= 255
				if(pixel[2] > 255):
					pixel[2] -= 255
	return image, paragraph, contentCount

out = cv2.VideoWriter(args.write,cv2.VideoWriter_fourcc(*'MJPG'),24.00, (1280,720))
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
# print(data)

randoms = [1.0]

contentCount = 0
for frameCount in range(len(vid)):
	if(frameCount >= len(vid)):
		break
	image = vid.get_data(frameCount)
	height, width, layers = image.shape
	if(len(randoms) == 1):
		for i in range(0,height*width):
			randoms.append(uniform(0.0,4.0))
		randoms = randoms[1:]

	image, paragraph, contentCount = im_func(image, frameCount, content, contentCount, data, 7, len(vid))
	# print('------------------')
	# print(int(frameCount))
	# print(len(vid))
	# print(len(data))
	# print(float(frameCount)/float(len(vid)))
	# print(float(frameCount)/float(len(vid))*len(data))

	# print(data[int(float(frameCount)/float(len(vid))*len(data))])
	# print((data[int(frameCount/len(vid)*len(data))]-338)/62 * 255)
	# print('-------------------------')

	if(args.putText):
		str_paragraph = ''
		par_count = 0
		tot_count = 0
		for i, j in enumerate(paragraph):
			str_paragraph += chr(j)
			if(i > 2000):
				break
			# par_count += 1
			# tot_count += 1
			# if(par_count >= 25):
			# 	str_paragraph += '\n'
			# 	par_count = 0
			# if(tot_count >= 400):
			# 	break

		for i, line in enumerate(str_paragraph.split('\n')):
			y = 10 + i*10
			if(y >= height):
				break
			cv2.putText(image,line,(10,y),cv2.FONT_HERSHEY_SIMPLEX,fontScale=0.3,color=(255,255,255))
	b, g, r = cv2.split(image)
	image = cv2.merge([r,g,b])
	out.write(image)
	progress(frameCount, len(vid))
	# if(frameCount > 200):
	# 	break

out.release()
print('total time: '+str(time.time()-all_start)+'s')