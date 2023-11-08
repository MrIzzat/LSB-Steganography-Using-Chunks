import GenerateSignature
from Encode import Encode
from Decode import Decode


def encode(CoverImagePath, MessagePath, OutputFilePath):
    EncodeImage = Encode()
    EncodeImage.encode(CoverImagePath, MessagePath, OutputFilePath)


def decode(StegoImagePath, OutputFilePath):
    DecodeImage = Decode()
    DecodeImage.decode(StegoImagePath, OutputFilePath)


def generateSignature(message):

    return GenerateSignature.generateSignature(message)


CoverImage = "TestFiles/cat.jpg"
MessageToHide = "TestFiles/ToHideText.txt"
OutputStegoFile = "TESTING.png"

print("Encoding...")
encode(CoverImage, MessageToHide, OutputStegoFile)
print("Done")


# StegoImage = "TESTING.png"
# OutputStegoMessage = "" #make sure it ends with / if not in this directory
#
# print("Decoding...")
# decode(StegoImage, OutputStegoMessage)
# print("Done")
#
#
# MessagePath = "TestFiles/ToHideText.txt"
#
# with open(MessagePath) as f:
#     messageContent = f.read()
#
# signature = generateSignature(messageContent)
#
# print(signature)
