
"""splitipy.stuff: stuff module within the splitipy package."""

from __future__ import division
from math import ceil
import os
import uuid
import csv
import hashlib
import os


class Stuff():
	@staticmethod
	def split(filename, splitsize):

		if os.path.isfile(filename):
			filesize = os.stat(filename).st_size
		else:
			print ("Hey, the file named "+filename+" doesn't exists.")
			return 1

		bsize = int(ceil(filesize/splitsize))
		times = int(ceil(filesize / bsize))
		parts = splitsize

		print ("Splitting file "+ str(filename) + " into "+ str(parts) + " parts")
		try:
			i=1
			block=True
			fcombine  = open(filename,"rb")
			folderName = 'encryptedFIle/'
			if not os.path.exists(folderName):
				os.mkdir(folderName)
			while block!="" and i<=parts:
				splitFile = folderName+ str(uuid.uuid4())+ ".dat"
				splitFile = os.path.abspath(splitFile)
				fw = open(splitFile,"wb")
				splitDir, splitFilename = os.path.split(splitFile)

				block = fcombine.read(bsize)
				fw.write(block)
				fw.close()
				# Crypt.seqenceCsv(splitFilename, splitDir)
				yield splitFilename , splitDir
				i+=1
		finally:
			fcombine.close()

	@staticmethod
	def combine(filename, hash):
		filename = 'encryptedFile/' + os.path.split(filename)[1]
		splittedFiles = []
		with open(hash + '.csv') as csvFile:
			reader = csv.DictReader(csvFile)
			for row in reader:
				print(row["sequence"])
				splittedFiles.append(row["sequence"])
		# print(filename)
		if not os.path.isfile('encryptedFile/'+ splittedFiles[0]):
			print(splittedFiles[0])
			print("Hey, the file named " + filename + " doesn't exists.")
			return 1

		bsize=1024 *1024
		joinedFilePath = os.path.split(filename)[0]+'/'+"join-"+os.path.split(filename)[1]
		print("join:",joinedFilePath)
		fcombine  = open(joinedFilePath,"wb")
		try:
			i=0
			while True:
				if not os.path.isfile('encryptedFile/'+splittedFiles[i]):
					break
				fr = open('encryptedFile/'+ splittedFiles[i],"rb")
				# block = 1
				# while block!= "":
				block = fr.read(bsize)
				fcombine.write(block)
				fr.close()
				i+=1
			# return joinedFilePath
		finally:
			fcombine.close()
			return ''
