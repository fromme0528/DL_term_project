import os
import sys
import pickle
import timeit
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data import DataLoader
from torch.utils.data import sampler
import torchvision.datasets as dset
import torchvision.transforms as T

import STFT
from model import PresidentSing

# Usage : python main.py <inPath> <outPath> <mode>
#
#         python main.py ./audios ./converted convert
#         python main.py ./dataset ./model train

def convert(convertModel, path):

	if os.path.isfile(path):

		if os.path.splitext(path)[-1] == '.wav':

			fileName, _ = convertFile(convertModel, path)

	elif os.path.isdir(path):

		for ps, dirs, files in os.walk(path):

			for f in files:

				if os.path.splitext(f)[-1] == '.wav':

					fileName, _ = convertFile(convertModel, os.path.join(ps, f))

	else:

		print('Error : Given path is wrong')

def convertFile(convertModel, path):

	audioList = list()

	spectroList = STFT.transformAll(path)

	for spectro in spectroList:

		_, converted = convertModel.convert(spectro)
		convertedAudio = STFT.griffinLim(converted)
		audioList.append(convertedAudio)

	audio = STFT.concatAudio(audioList)
	
	dirName = os.path.dirname(path)
	fileName = 'converted_' + os.path.basename(path)
	librosa.output.write_wav(os.path.join(dirName, fileName, audio, sr = 51200))
	print('Output : ', fileName)

	return fileName, audio

def main(path, pathModel, mode):

	convertModel = PresidentSing(path, pathModel, 10240)

	if mode == 'train':

		print('Train started')
		timeNow = timeit.default_timer()
		
		lossHistory = model.train()

		print('Train ended')
		print('Elapsed time : ', timeit.default_timer() - timeNow)

	elif mode == 'convert':

		convertModel.load(pathModel)

		print('Convert started')
		timeNow = timeit.default_timer()

		convert(convertModel, path)

		print('Convert ended')
		print('Elapsed time : ', timeit.default_timer() - timeNow)

	else:

		print('Error : Mode can be "train" or "convert"')

if __name__ == '__main__':

	parser = argparse.ArgumentParser() 
	parser.add_argument('path', help = 'Path 1 : train - dataset directory, convert - input / output directory')
	parser.add_argument('pathModel', help = 'Path 2 : model directory')
	parser.add_argument('mode', help = 'Mode option : <train> or <convert>')
	args = parser.parse_args()
	
	main(args.path, args.pathModel, args.mode)
	sys.exit(0)