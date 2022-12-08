# -*- coding: utf-8 -*-
"""MyCannyEdgeDetectorDemo.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PtanXG9rs-EfvnUYukvKKjgLXoyxZcsT
"""

# Matplotlib: Standard library to create interactive visualisations in python
import matplotlib.pyplot as plt 
# Numpy: Library having sevral operations on matrices, mathematical functions on arrays
import numpy as np 
# skimage: Contains many image processing algorithms
from skimage import data
from skimage.color import *
from skimage.metrics import peak_signal_noise_ratio
from skimage.metrics import structural_similarity
from skimage.transform import *
from skimage import io 
from skimage import feature

from google.colab import drive
drive.mount('/content/drive')

#Function used to do convolution of 2 Dimentional matrices 
def convolution2d(image, kernel):
  m, n = kernel.shape
  if (m == n):
    y, x = image.shape
    y = y - m + 1 
    x = x - m + 1
    new_image = np.zeros((y,x))
    for i in range(y):
      for j in range(x):
        #Using a subset of the image and applying element multiplication
        new_image[i][j] = np.sum(image[i:i+m, j:j+m]*kernel) 
  return new_image

def gaussian_blur(img, size=5, sigma=1):
  #Constant to get the number of rows behind and after the origin
  k=(size-1)//2 
  x = np.array([np.arange(-k, k+1) for i in range(size)])
  y = np.transpose(x)
  normal = 1 / (2.0 * np.pi * sigma**2) 
  # gaussian filter of the required size
  g_filter =  np.exp(-((x**2 + y**2) / (2.0*sigma**2))) * normal 
  # Convolve the image with the gaussian filter
  blur_img = convolution2d(img, g_filter) 
  return blur_img

def gradient_calculate(img):
  #Initializing the sobel mask for vertical edges
  kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype = float)
  #Initializing the sobel mask for horizontal edges
  ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype = float) 

  #Applying convolution to get vertical edges
  Ix = convolution2d(img, kx) 
  #Applying convolution to get horizontal edges
  Iy = convolution2d(img, ky) 

  #Calculating gradient
  G = np.sqrt(Ix**2+Iy**2) 
  G = G/G.max()
  G = G*255

  theta = np.arctan(Ix/Iy) #Calculating angle of the edges

  return (G,theta)

def non_max_suppression(img, theta):
  M, N = img.shape
  Z = np.zeros((M,N), dtype=np.int32)
  #Converting angle to degrees
  angle = theta * 180. / np.pi 
  angle[angle < 0] += 180    
  for i in range(1,M-1):
    for j in range(1,N-1):
      #Initializing value
      q = 255 
      r = 255
      if (0 <= angle[i,j] < 22.5) or (157.5 <= angle[i,j] <= 180): #If the edge is horizontal
        q = img[i, j+1]
        r = img[i, j-1]
      elif (22.5 <= angle[i,j] < 67.5): #If the edge is diagonal
        q = img[i+1, j-1]
        r = img[i-1, j+1]
      elif (67.5 <= angle[i,j] < 112.5): #If the edge is vertical
        q = img[i+1, j]
        r = img[i-1, j]
      elif (112.5 <= angle[i,j] < 157.5): #If the edge is diagonal
        q = img[i-1, j-1]
        r = img[i+1, j+1]
      if (img[i,j] >= q) and (img[i,j] >= r): #Edge is considered only if the intensity of the current pixel is greater than equal to its predecessor and successor
        Z[i,j] = img[i,j]
      else:
        Z[i,j] = 0 #Else it is zero
  return Z

def double_thresholding(img, low_threshold, high_threshold):
  #Initializing the higher threshold value
  high_thresh_val = img.max()*high_threshold 
  #Initialiing the lower threshold value
  low_thresh_val = img.max()*low_threshold 
  m,n = img.shape

  #Initializing the resulting thresholded value of weaker pixel
  weak = 75 
  #Initializing the resulting thresholded value of stronger pixel
  strong = 255 

  #Getting all the strong pixels
  strong_x,strong_y = np.where(img>=high_thresh_val)
  #Getting all the weaker pixels
  weak_x,weak_y = np.where((img>=low_thresh_val) & (img<=high_thresh_val)) 
  #Getting the pixels which have value less the lower threshold value
  zero_x,zero_y = np.where(img<low_thresh_val) 

  #Creating the resulting matrix of all the pixels with their respective values
  result = np.zeros((m,n))
  result[strong_x, strong_y] = strong
  result[weak_x, weak_y] = weak
  return result

def hysteresis(img, weak=75, strong=255):
  M, N = img.shape 
  new_img = np.copy(img) 
  for i in range(1, M-1):
    for j in range(1, N-1):
      if (img[i,j] == weak):
        try:
          #If any of the neighbouring pixel have stronger intensity then the current pixel is also given the stronger intensity
          if ((img[i+1, j-1] == strong) or (img[i+1, j] == strong) or (img[i+1, j+1] == strong)
          or (img[i, j-1] == strong) or (img[i, j+1] == strong)
          or (img[i-1, j-1] == strong) or (img[i-1, j] == strong) or (img[i-1, j+1] == strong)):
            new_img[i, j] = strong
          else:
            new_img[i, j] = 0
        except IndexError as e:
            pass
  return new_img

#Function to apply canny edge detection
def myCannyEdgeDetector(input_img, low_threshold , high_threshold): 
  gaussian_img = gaussian_blur(input_img, 5)
  gradient_img, theta = gradient_calculate(gaussian_img)
  suppressed_img = non_max_suppression(gradient_img, theta)
  threshold_img = double_thresholding(suppressed_img, low_threshold, high_threshold)
  final_img = hysteresis(threshold_img)
  return final_img

for i in range(1, 6):
  r_path = "Task1/Images/Img"+str(i)+".jpg"
  testImage = io.imread(r_path)
  testImage = rgb2gray(testImage)
  low_threshold = 0.05
  high_threshold = 0.15
  outputImage = myCannyEdgeDetector(testImage, low_threshold, high_threshold)
  w1_path = "Task1/MyCannyEdgeDetector/Img"+str(i)+".jpg"
  io.imsave(w1_path, outputImage)
  edgeMapCanny = feature.canny(testImage)
  w2_path = "Task1/InbuiltCannyEdgeDetector/Img"+str(i)+".jpg"
  io.imsave(w2_path, edgeMapCanny)

  m, n = outputImage.shape

  edgeMapCanny = resize(edgeMapCanny, (m, n))

  print('low_threshold: ', low_threshold, '  high_threshold: ', high_threshold)
  SSIM = structural_similarity(edgeMapCanny, outputImage, multichannel=True)
  print('SSIM: ', SSIM)

  PSNR = peak_signal_noise_ratio(edgeMapCanny, outputImage)
  print('PSNR: ', PSNR)