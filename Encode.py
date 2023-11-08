import math
import os
import random

import cv2
from PIL import Image

from GenerateSignature import generateSignature


class Encode():

    def encode(self, CoverImagePath, MessagePath, OutputFilePath):

        # Open the Cover Image

        image = cv2.imread(CoverImagePath)

        imageSize = len(image) * len(image[0]) * len(image[0][0])

        maxMessageSize = int(imageSize / 8)

        # Open the message text file
        with open(MessagePath) as f:
            messageContent = f.read()

        # Replace the Restricted Character "|"
        messageContent = messageContent.replace('|', '')

        # Prepare Content for Hiding
        messageContentSize = len(messageContent)

        messageFileName = os.path.basename(f.name)
        messageSignature = generateSignature(messageContent)

        messageToHide = messageFileName + "|" + str(messageContentSize) + "|" + messageSignature + "|" + messageContent

        # Check to see if the image will fix inside the photo

        if len(messageToHide) > maxMessageSize - 15:
            print("The message is too big to hide in this photo.")
            return

        # Convert message to Binary ASCII

        messageToAscii = []

        for letter in messageToHide:
            messageToAscii.extend(ord(num) for num in letter)

        def IntegerToBinaryString(number):
            return '{0:08b}'.format(number)

        messageToAsciiBinary = []

        for num in messageToAscii:
            messageToAsciiBinary.append(IntegerToBinaryString(num))

        messageToAsciiBinarySingleList = "".join(messageToAsciiBinary)

        # Find the optimal number of chunks to split the message

        messageBinarySize = len(messageToAsciiBinarySingleList)

        logOutput = math.log(messageBinarySize, 1.01)  # Formula used to find the number of chunks
        NumberOfChunks = int(math.floor(logOutput) + 1)
        sizeOfChunks = int(math.floor(messageBinarySize / NumberOfChunks) + 1)

        # Split the message into chunks

        chunks = []
        chunk = ""

        i = 0
        for bit in messageToAsciiBinarySingleList:
            if i == sizeOfChunks:
                i = 0
                chunks.append(chunk)
                chunk = ""

            chunk += bit
            i += 1

        chunks.append(chunk)

        # Setting up chunk to contain the length of the binary message so the message can be extracted

        messageBinarySizeString = str(messageBinarySize) + "|"

        messageBinarySizeToAscii = []

        for letter in messageBinarySizeString:
            messageBinarySizeToAscii.extend(ord(num) for num in letter)

        def IntegerToBinaryString(number):
            return '{0:08b}'.format(number)

        messageBinarySizeToAsciiBinary = []

        for num in messageBinarySizeToAscii:
            messageBinarySizeToAsciiBinary.append(IntegerToBinaryString(num))

        messageBinarySizeToAsciiBinarySingleList = "".join(messageBinarySizeToAsciiBinary)

        # Generate the random sequence to shuffle the chunks with

        random.seed(4444)

        randomChunkSeq = random.sample(range(len(chunks) + 1), len(chunks) + 1)

        for seq in range(len(randomChunkSeq)):

            if randomChunkSeq[seq] == 0:
                temp = randomChunkSeq[seq]
                randomChunkSeq[seq] = randomChunkSeq[0]
                randomChunkSeq[0] = temp

        chunks.insert(0, messageBinarySizeToAsciiBinarySingleList)

        for seq in range(len(randomChunkSeq)):
            if randomChunkSeq[seq] == len(chunks) - 1:
                temp = randomChunkSeq[seq]
                randomChunkSeq[seq] = randomChunkSeq[len(chunks) - 1]
                randomChunkSeq[len(chunks) - 1] = temp

        # Embed the chunks into the LSB of the image

        totalBitNumber = 0
        BitNumber = 0
        ChunkNumber = 0

        for row in reversed(range(len(image))):
            for column in reversed(range(len(image[row]))):
                for color in range(len(image[row][column])):

                    if totalBitNumber == len(messageToAsciiBinarySingleList) + len(
                            messageBinarySizeToAsciiBinarySingleList):
                        break

                    if BitNumber == len(chunks[randomChunkSeq[ChunkNumber]]):
                        BitNumber = 0
                        ChunkNumber += 1

                    if chunks[randomChunkSeq[ChunkNumber]][BitNumber] == '1':
                        image[row][column][color] |= 1

                    else:
                        image[row][column][color] &= ~1

                    BitNumber += 1
                    totalBitNumber += 1
            else:
                continue

        #Save the Stego Image

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        im = Image.fromarray(image.astype('uint8')).convert('RGB')

        im.save(OutputFilePath)
