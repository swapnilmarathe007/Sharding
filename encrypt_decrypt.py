import os
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import hashlib
import datetime
import os
import csv
from hurry.filesize import size
from split_combine import Stuff

key = "Iagon"

class Crypt:
    @staticmethod
    def hash(message):
        """file hash."""
        fileHash = hashlib.sha256()
        fileHash.update(message)
        return fileHash.hexdigest()

    @staticmethod
    def getKey(key='Iagon'):
        """
        :param key: This is key used for encryption and decryption of file
        :return: return the key with uniform length i.e 16 or 32 byte
        """
        keyHash = SHA256.new(key.encode('utf-8')).digest()
        return keyHash

    @staticmethod
    def getMetainformation(filename):
        """
        :param filename: TO get the metainformation of file
        :return: returns different file related parameter i.e modified ,access,change time, size and extension of file
        """
        getTime = os.path.getmtime(filename)
        modifiedTime = str(datetime.datetime.fromtimestamp(getTime))      # get the modified time of file
        getTime = os.path.getatime(filename)
        accessTime = str(datetime.datetime.fromtimestamp(getTime))        # get the access time of file
        getTime = os.path.getctime(filename)
        changeTime = str(datetime.datetime.fromtimestamp(getTime))        # get the change time of file
        fileSize = os.stat(filename).st_size                              # get the size of file
        extension = os.path.splitext(filename)[1]                         # get the file extension
        return modifiedTime.replace(' ','_'), accessTime.replace(' ','_'),changeTime.replace(' ','_'), size(fileSize),extension

    @classmethod
    def encrypt(cls, key, filename):
        """
        :param key: This is key for Encryption
        :param filename: file path to encrypt the file
        :return:
        """
        chunkSize = 64 * 1024
        folderName = 'encryptedFile/'
        # Save the file in .dat file format
        outputFile = folderName + '{}.dat'.format(os.path.split(filename)[1])
        print(outputFile)
        # get meta-information of file
        modifiedTime, accessTime ,changeTime, fileSize , fileExtension = cls.getMetainformation(filename)
        print("Modified data and time:",modifiedTime)
        print("Access time:", accessTime)
        print("Change time:", changeTime)
        print("File size:", fileSize)
        print("File extension:", fileExtension)

        if not os.path.exists(folderName):
            os.mkdir(folderName)
        # zfill pads string on the left with zeros to fill width.
        file_size = str(os.path.getsize(filename)).zfill(16)
        IV = Random.new().read(16)

        # Encrypt the file
        encryptor = AES.new(cls.getKey(), AES.MODE_CBC, IV)   # CBC Mode : sequence of bits are encrypted as a single unit

        with open(filename, 'rb') as infile:

            with open(outputFile, 'wb') as outfile:
                outfile.write(file_size.encode('utf-8'))
                print(IV)
                outfile.write(IV)

                while True:

                    chunk = infile.read(chunkSize)

                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += b' ' * (16 - (len(chunk) % 16))

                    encryptedChunk = encryptor.encrypt(chunk)
                    outfile.write(encryptedChunk)
            # get the hash of the encrypted file
            with open(outputFile, 'rb') as f :
                message = f.read()
                hash = cls.hash(message)
                print("file hash:",hash)

            cls.recordCsv(outputFile,hash,fileSize,fileExtension,modifiedTime,accessTime,changeTime)
            splitSeq = Stuff.split(outputFile,splitsize=3)
            cls.seqenceCsv(hash,splitSeq)

    @classmethod
    def decrypt(cls, key, filename):
        """
        :param key: This is key for Decryption
        :param filename:file path to decrypt the file
        :return:
        """
        chunkSize = 64 * 1024
        folderName = 'decryptedFile/'
        outputFile = folderName + filename[:-3]
        if not os.path.exists(folderName):
            os.mkdir(folderName)

        inputFIle = 'encryptedFile/'
        # check hash of encrypted file
        with open(inputFIle + filename, 'rb') as file:
            message = file.read()
            hash = cls.hash(message)
            print("file hash:",hash)

        file = inputFIle + filename
        Stuff.combine(file,hash)

        with open(inputFIle + 'join-' + filename, 'rb') as infile:
            fileSize = int(infile.read(16))
            IV = infile.read(16)

            decryptor = AES.new(cls.getKey(), AES.MODE_CBC, IV)

            with open(outputFile, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunkSize)

                    if len(chunk) == 0:
                        break

                    decryptedChunk = decryptor.decrypt(chunk)
                    outfile.write(decryptedChunk)
                outfile.truncate(fileSize)
        # get the meta-information of file after decryption
        modifiedTime,accessTime,changeTime,fileSize,extension = cls.getMetainformation(outputFile[:-1])
        print("Modified data and time:",modifiedTime)
        print("Access time:", accessTime)
        print("Change time:", changeTime)
        print("File size:", fileSize)
        print("File extension:", extension)


    @classmethod
    def recordCsv(cls, filename , hash ,fileSize ,fileExtension ,modifiedTime,accessTime,changeTime):
        """

        :param filename: Name of the file
        :param hash: 16 byte hash of encrypted file
        :param fileSize: size of file
        :param fileExtension:  extension of file
        :param modifiedTime: modified time of file
        :param accessTime: access time of file
        :param changeTime: change time of file
        :return: return the meta-information in csv file
        """
        if not os.path.exists('Record.csv'):
            with open('Record.csv', 'w', newline='') as f:
                fieldname = ['fileName', 'hash', 'fileSize', 'fileExtension', 'modifiedTime','accessTime','changeTime']
                writer = csv.DictWriter(f, fieldnames=fieldname)
                writer.writeheader()
                writer.writerow({'fileName': filename,'hash': hash , 'fileSize': fileSize,'fileExtension':fileExtension,'modifiedTime':modifiedTime,'accessTime':accessTime,'changeTime':changeTime})
        else:
            with open('Record.csv', 'a', newline='') as f:
                fieldname = ['fileName', 'hash','fileSize','fileExtension','modifiedTime','accessTime','changeTime']
                writer = csv.DictWriter(f, fieldnames=fieldname)

                writer.writerow({'fileName': filename,'hash': hash , 'fileSize': fileSize,'fileExtension':fileExtension,'modifiedTime':modifiedTime,'accessTime':accessTime,'changeTime':changeTime})

    @classmethod
    def seqenceCsv(cls,hash,splitSeq):
        """
        :param hash: pass the hash of encrypted file
        :param splitSeq: sequence and location of splitted file
        :return: return the csv file with hash
        """
        for seq, loc in splitSeq:
            if not os.path.exists(hash + '.csv'):
                with open(hash + '.csv', 'a', newline='') as f:
                    fieldname= ['sequence','location']
                    writer = csv.DictWriter(f,fieldnames=fieldname)
                    writer.writeheader()
                    writer.writerow({'sequence':seq,'location':loc})
            else :
                with open(hash +'.csv', 'a', newline='') as f:
                    fieldname= ['sequence' , 'location']
                    writer = csv.DictWriter(f,fieldnames=fieldname )

                    writer.writerow({'sequence':seq, 'location':loc})


def main():
    choice = input("(E)ncrypt or (D)ecrypt?: ")
    crypt = Crypt()
    if choice == 'E':
        filename = input("File to encrypt: ")
        crypt.encrypt(key,filename)
        print("Done.")
    elif choice == 'D':
        filename = input("File to decrypt: ")
        crypt.decrypt(key,filename)
        print("Done.")
    else:
        print("No Option selected")


if __name__ == '__main__':
    main()



