import os
import sys
import cPickle as pickle
import time

import cv2
import numpy as np
from VideoStream import VideoStream

import create_features as cf
from trainingImage import ClassifierTrainer

import trainingSpeech
import tracker

import warnings
warnings.filterwarnings('ignore')

IDENTIFIED = 1
FOLLOW = 2

# classifying an image
class ImageClassifier(object):
    def __init__(self, svm_file, codecook_file):
        # load SVM classifier
        with open(svm_file, 'rb') as f:
            self.svm = pickle.load(f)

        # load the codebook
        with open(codecook_file, 'rb') as f:
            self.kmeans, self.centroids = pickle.load(f)

    # method to get the output image tag
    def getImageTag(self, img):
        # resize the input image
        img = cf.resize_to_size(img)

        # extract the feature vector
        feature_vector = cf.FeatureExtractor().get_feature_vector(img, self.kmeans, self.centroids)

        # classify the feature vector and get the output tag
        image_tag = self.svm.classify(feature_vector)

        return image_tag


if __name__ == '__main__':
    svm_file = "svm.pkl"
    codebook_file = "codebook.pkl"

    #os.system("flite -t 'Good afternoon! I am Raspberry Pi.'")

    resolution = (640, 480)
    cap = VideoStream(usePiCamera=False, resolution=resolution).start()
    time.sleep(2.0)

    cv2.namedWindow("Result")
    img = cv2.imread("defaultTrain.jpg")
    cv2.imshow("Result", img)

    capture = 0

    while True:
        #Speech recognition initialize
        
        #trainingSpeech.start()
        #capture = trainingSpeech.exit_flag

        key = cv2.waitKey(1)
        if key == 27:
            break
        if key == ord('f'):
            input_image = cv2.imread("test.jpg")
            image_class = ImageClassifier(svm_file, codebook_file).getImageTag(input_image)
            result = cv2.putText(input_image, str(image_class), (10, 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                                 (0, 255, 0),
                                 1,
                                 cv2.LINE_AA)
            #cv2.imshow("Result", result)
        if key == 32 or capture == IDENTIFIED or key == ord('1'):
            # reset flag variables
            capture = 0
            trainingSpeech.exit_flag = 0
            ## identified command
            print "IDENTIFY module"
            #os.system("flite -t 'Command Accepted! Identifying Object.'")
            frame = cap.read()
            time.sleep(0.1)
            input_image = frame
            image_class = ImageClassifier(svm_file, codebook_file).getImageTag(input_image)
            result = cv2.putText(input_image, str(image_class), (10, 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75,
                                 (0, 255, 0),
                                 1,
                                 cv2.LINE_AA)
            print "Recognized Object: ", str(image_class)
            #os.system("flite -t 'The object is " + str(image_class) + ".'")
            cv2.imwrite("result.jpg", result)
            time.sleep(0.2)
            img = cv2.imread("result.jpg")
            cv2.imshow("Result", img)
            
        if capture == FOLLOW or key == ord('2'):
            # reset flag variables
            capture = 0
            trainingSpeech.exit_flag = 0
            ## track / follow command
            print "FOLLOW module"

            #set trainImage for tracking and start tracking
            cv2.imwrite("defaultTrain.jpg", cap.read())
            tracker.RUN_TIME = 60
            #os.system("flite -t 'Command Accepted! Following object for " + str(tracker.RUN_TIME) + " seconds'")
            tracker.start(cap)
            
        #cv2.imshow("Classified", result)

    cv2.destroyAllWindows()
    cap.stop()
