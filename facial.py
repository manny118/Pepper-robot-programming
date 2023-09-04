# Pepper's face detection
import time
from naoqi import ALProxy
from capture import Vision


PORT = 9559
robotIP = "192.168.1.91"
# Create a proxy to ALFaceDetection
try:
  faceDetection = ALProxy("ALFaceDetection", robotIP, PORT)
  tts = ALProxy("ALAnimatedSpeech", robotIP, PORT)
  memoryProxy = ALProxy("ALMemory", robotIP, PORT)
  vision = Vision(robotIP, 9559)


except Exception, e:
  print "Could not create the proxy:"
  print str(e)
  exit(1)

# Subscribe to the ALFaceDetection proxy
period = 500
faceDetection.subscribe("Test_Face", period, 0.0)
memValue = "FaceDetected"

# A simple loop that reads the memValue and checks whether faces are detected.
for i in range(0, 300):
  time.sleep(0.5)
  val = memoryProxy.getData(memValue)

  print ""
  print "*****"
  print ""

  # Check whether we got a valid output.
  if(val and isinstance(val, list) and len(val) >= 2):
    tts.say("I can see you")
    # We detected faces !
    # First Field = TimeStamp.
    timeStamp = val[0]

    # Second Field = array of face_Info's.
    faceInfoArray = val[1]

    try:
      # Browse the faceInfoArray to get info on each detected face.
      for j in range( len(faceInfoArray)-1 ):
        faceInfo = faceInfoArray[j]
        # First Field = Shape info.
        faceShapeInfo = faceInfo[0]
        # Second Field = Extra info (empty for now).
        faceExtraInfo = faceInfo[1]

        print "  alpha %.3f - beta %.3f" % (faceShapeInfo[1], faceShapeInfo[2])
        print "  width %.3f - height %.3f" % (faceShapeInfo[3], faceShapeInfo[4])

        vision.captureImage()

    except Exception, e:
      print "faces detected, but it seems getData is invalid. ALValue ="
      print val
      print "Error msg %s" % (str(e))
  else:
    print "No face detected"

# Unsubscribe the module.
faceDetection.unsubscribe("Test_Face")
