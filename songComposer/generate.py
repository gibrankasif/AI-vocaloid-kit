# Load Larger LSTM network and generate melody
import sys
import numpy
import matplotlib.pyplot as plt
from midiutil.MidiFile import MIDIFile

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils


filename = "./bin/model/model.h5"

seq_length = 60

read_path = './songComposer/matrices/input/output/output-0.npy' 

def generate():

	raw_text = numpy.load(read_path)

	# create mapping of unique chars to integers, and a reverse mapping
	chars = sorted(list(set(raw_text)))
	char_to_int = dict((c, i) for i, c in enumerate(chars))
	int_to_char = dict((i, c) for i, c in enumerate(chars))

	# summarize the loaded data
	n_chars = len(raw_text)
	n_vocab = len(chars)
	print("Total Characters: ", n_chars)
	print("Total Vocab: ", n_vocab)

	# prepare the dataset of input to output pairs encoded as integers
	dataX = []
	dataY = []
	for i in range(0, n_chars - seq_length, 1):
		seq_in = raw_text[i:i + seq_length]
		seq_out = raw_text[i + seq_length]
		dataX.append([char_to_int[char] for char in seq_in])
		dataY.append(char_to_int[seq_out])
	n_patterns = len(dataX)
	print("Total Patterns: ", n_patterns)

	# reshape X to be [samples, time steps, features]
	X = numpy.reshape(dataX, (n_patterns, seq_length, 1))

	# normalize
	X = X / float(n_vocab)

	# one hot encode the output variable
	y = np_utils.to_categorical(dataY)

	# define the LSTM model
	model = Sequential()
	model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
	#model.add(Dropout(0.2))
	model.add(LSTM(256))
	#model.add(Dropout(0.2))
	model.add(Dense(y.shape[1], activation= 'softmax' ))

	# load the network weights

	model.load_weights(filename)
	model.compile(loss= 'categorical_crossentropy' , optimizer= 'adam' )

	# pick a random seed
	start = numpy.random.randint(0, len(dataX)-1)
	pattern = dataX[start]
	print("Seed:"
)
	xPlot = []
	yPlot = []

	# generate characters
	for i in range(1000):
		x = numpy.reshape(pattern, (1, len(pattern), 1))
		x = x / float(n_vocab)
		prediction = model.predict(x, verbose=0)
		index = numpy.argmax(prediction)
		result = int_to_char[index]
		seq_in = [int_to_char[value] for value in pattern]
		
		#print result	
		yPlot.append(result)
		xPlot.append(i)
		#sys.stdout.write(result)
		pattern.append(index)
		pattern = pattern[1:len(pattern)]


	print('Writing file . . .')



	MyMIDI = MIDIFile(1)
	track = 0
	time = 0
	channel = 0
	duration = 1
	volume = 100
	tempo = 180

	MyMIDI.addTrackName(track, time, "Sample Track")
	MyMIDI.addTempo(track,time,tempo)


	for i in range(0,len(xPlot)-1):
		time = xPlot[i]
		pitch = yPlot[i]

		MyMIDI.addNote(track, channel, pitch, time, duration, volume)

	binfile = open("./bin/output/result.mid", 'wb')
	MyMIDI.writeFile(binfile)
	binfile.close()

	print("\nDone.")



def generateCustomPath(modelPath, saveMidiPath, matrixPath):

	raw_text = numpy.load(matrixPath)

	# create mapping of unique chars to integers, and a reverse mapping
	chars = sorted(list(set(raw_text)))
	char_to_int = dict((c, i) for i, c in enumerate(chars))
	int_to_char = dict((i, c) for i, c in enumerate(chars))

	# summarize the loaded data
	n_chars = len(raw_text)
	n_vocab = len(chars)
	print("Total Characters: ", n_chars)
	print("Total Vocab: ", n_vocab)

	# prepare the dataset of input to output pairs encoded as integers
	dataX = []
	dataY = []
	for i in range(0, n_chars - seq_length, 1):
		seq_in = raw_text[i:i + seq_length]
		seq_out = raw_text[i + seq_length]
		dataX.append([char_to_int[char] for char in seq_in])
		dataY.append(char_to_int[seq_out])
	n_patterns = len(dataX)
	print("Total Patterns: ", n_patterns)

	# reshape X to be [samples, time steps, features]
	X = numpy.reshape(dataX, (n_patterns, seq_length, 1))

	# normalize
	X = X / float(n_vocab)

	# one hot encode the output variable
	y = np_utils.to_categorical(dataY)

	# define the LSTM model
	model = Sequential()
	model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
	model.add(LSTM(256, return_sequences=True))
	model.add(LSTM(256, return_sequences=True))
	model.add(LSTM(256, return_sequences=True))
	model.add(LSTM(256, return_sequences=True))
	model.add(LSTM(256))
	model.add(Dropout(0.2))
	model.add(Dense(y.shape[1], activation='softmax'))

	# load the network weights

	model.load_weights(modelPath)
	model.compile(loss= 'categorical_crossentropy' , optimizer= 'adam' )

	# pick a random seed
	start = numpy.random.randint(0, len(dataX)-1)
	pattern = dataX[start]
	print("Seed:")

	xPlot = []
	yPlot = []

	# generate characters
	for i in range(1000):
		x = numpy.reshape(pattern, (1, len(pattern), 1))
		x = x / float(n_vocab)
		prediction = model.predict(x, verbose=0)
		index = numpy.argmax(prediction)
		if index >= len(int_to_char):
			index = index%len(int_to_char)

		result = int_to_char[index]
		seq_in = [int_to_char[value] for value in pattern]
		
		#print result	
		yPlot.append(result)
		xPlot.append(i)
		pattern.append(index)
		pattern = pattern[1:len(pattern)]


	print('Writing file . . .')



	MyMIDI = MIDIFile(1)
	track = 0
	time = 0
	channel = 0
	duration = 1
	volume = 100
	tempo = 180

	MyMIDI.addTrackName(track, time, "Sample Track")
	MyMIDI.addTempo(track,time,tempo)


	for i in range(0,len(xPlot)-1):
		time = xPlot[i]
		pitch = yPlot[i]

		MyMIDI.addNote(track, channel, pitch, time, duration, volume)

	binfile = open(saveMidiPath, 'wb')
	MyMIDI.writeFile(binfile)
	binfile.close()

	print("\nDone.")
