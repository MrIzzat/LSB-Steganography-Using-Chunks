import math
import random

import cv2

from GenerateSignature import generateSignature


class Decode():

    def decode(self, StegoImagePath, OutputFilePath):

        # Methods used

        def BinaryStringToInteger(BinaryString):
            return int(BinaryString, 2)

        # Read the Stego Image

        StegoImage = cv2.imread(StegoImagePath)

        # Extract the Binary size of the hidden message

        # First, the first 400 bits will be extracted
        # 400 bits should be enough to represent binary file size

        HiddenMessageBinarySizeBinary = []

        HiddenMessageBinarySizeLength = 400

        i = 0

        for row in reversed(range(len(StegoImage))):
            for column in reversed(range(len(StegoImage[row]))):
                for color in range(len(StegoImage[row][column])):
                    if (i == HiddenMessageBinarySizeLength):
                        break

                    bit = StegoImage[row][column][color] & 1
                    HiddenMessageBinarySizeBinary.append(str(bit))
                    i += 1
            else:
                continue

        # Split the extracted message to groups of 8 bits

        HiddenMessageBinarySizeBinaryList = []
        BinaryString = ""

        i = 0
        for bit in HiddenMessageBinarySizeBinary:

            BinaryString += bit
            i += 1

            if i > 7:
                HiddenMessageBinarySizeBinaryList.append(BinaryString)
                BinaryString = ""
                i = 0

        # Convert the bit groups to integers

        HiddenMessageBinarySizeAscii = []

        for BinaryString in HiddenMessageBinarySizeBinaryList:
            HiddenMessageBinarySizeAscii.append(BinaryStringToInteger(BinaryString))

        # Convert the integer values to Characters and append them to a string

        HiddenMessageBinarySize = ""

        for letter in HiddenMessageBinarySizeAscii:
            HiddenMessageBinarySize += chr(letter)

        # Separate the fill binary size from the redundant data

        hiddenMessageBinarySizeSplit = HiddenMessageBinarySize.split('|')

        hiddenMessageBinarySize = (len(hiddenMessageBinarySizeSplit[0]) + 1) * 8

        fileBinarySize = int(hiddenMessageBinarySizeSplit[0])

        # Find the optimal number of chunks used to split and hide the message
        logOutput = math.log(fileBinarySize, 1.01)
        NumberOfChunks = int(math.floor(logOutput) + 1)
        sizeOfChunks = int(math.floor(fileBinarySize / NumberOfChunks) + 1)

        # Extract the message bits from the image

        HiddenMessageBinary = ""

        totalBitNumber = 0
        i = 0

        for row in reversed(range(len(StegoImage))):
            for column in reversed(range(len(StegoImage[row]))):
                for color in range(len(StegoImage[row][column])):
                    if i >= hiddenMessageBinarySize:
                        if totalBitNumber == fileBinarySize:
                            break

                        bit = StegoImage[row][column][color] & 1
                        HiddenMessageBinary += str(bit)

                        totalBitNumber += 1

                    i += 1

            else:
                continue

        # Generate the Chunk Sequence used to hide the Chunks

        random.seed(4444)

        chunks = []

        if len(HiddenMessageBinary) % sizeOfChunks != 0:
            numberOfUsedChunks = math.floor(len(HiddenMessageBinary) / sizeOfChunks) + 1
        else:
            numberOfUsedChunks = math.floor(len(HiddenMessageBinary) / sizeOfChunks)

        randomChunkSeq = random.sample(range(numberOfUsedChunks+1), numberOfUsedChunks+1)

        for seq in range(len(randomChunkSeq)):
            if randomChunkSeq[seq] == 0:
                temp = randomChunkSeq[seq]
                randomChunkSeq[seq] = randomChunkSeq[0]
                randomChunkSeq[0] = temp
                break

        chunks.insert(0, "0101010001000101010011010101000001111100")

        for seq in range(len(randomChunkSeq)):
            if randomChunkSeq[seq] == numberOfUsedChunks:
                temp = randomChunkSeq[seq]
                randomChunkSeq[seq] = randomChunkSeq[numberOfUsedChunks]
                randomChunkSeq[numberOfUsedChunks] = temp
                break

        # Sort the bits into the correct Chunks based on the sequence

        for i in range(numberOfUsedChunks):
            chunks.append("")

        chunk = ""
        i = 0
        ChunkSeq = 1

        for bit in HiddenMessageBinary:

            if i == sizeOfChunks:
                chunks[randomChunkSeq[ChunkSeq]] = chunk
                chunk = ""
                ChunkSeq += 1
                i = 0

            chunk += bit
            i += 1

        chunks[randomChunkSeq[ChunkSeq]] = chunk

        # Convert the message from Binary to String

        HiddenMessageBinary2 = "".join(chunks)

        # Convert the message from Binary to a String

        HiddenMessageBinaryList = []
        BinaryString = ""

        i = 0
        for bit in HiddenMessageBinary2:

            BinaryString += bit
            i += 1

            if i > 7:
                HiddenMessageBinaryList.append(BinaryString)
                BinaryString = ""
                i = 0

        HiddenMessageAscii = []

        for BinaryString in HiddenMessageBinaryList:
            HiddenMessageAscii.append(BinaryStringToInteger(BinaryString))

        HiddenMessage = ""

        for letter in HiddenMessageAscii:
            HiddenMessage += chr(letter)

        # Store the Message Content and Information

        hiddenMessageSplit = HiddenMessage.split('|')

        fileName = hiddenMessageSplit[1]
        fileSize = int(hiddenMessageSplit[2])
        fileSignature = hiddenMessageSplit[3]

        ExtractedMessage = hiddenMessageSplit[4]

        extractedSignature = generateSignature(ExtractedMessage)

        if extractedSignature == fileSignature:
            print("Text Extracted Successfully")
        else:
            print("Text not Extracted Correctly (Signature Error)")

        with open(OutputFilePath + fileName, 'w') as f:
            f.write(ExtractedMessage)
