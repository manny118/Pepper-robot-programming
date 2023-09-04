# script for capturing images with Pepper

from naoqi import ALProxy
import random
from PIL import Image

class Vision:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.video = ALProxy("ALVideoDevice", ip_address, port)


    def captureImage(self, img_id = 1, path = "/home/generic/Emm/captures/img-", cameraID = 1):
        cameraId = cameraID #0 for tongue image, 1 for hand
        strName = "capture2DImage_{}".format(random.randint(1, 10000000000))

        clientRGB = self.video.subscribeCamera(strName, cameraId, 2, 11, 10)
        imageRGB = self.video.getImageRemote(clientRGB)
        array = imageRGB[6]
        image_string = str(bytearray(array))

        # Create a PIL Image from our pixel array.
        im = Image.frombytes("RGB", (imageRGB[0], imageRGB[1]), image_string)

        image_name_2d = path + str(img_id) + ".png"
        im.save(image_name_2d, "PNG") # save the image
        
