import numpy as np
import pydicom as pd
import matplotlib.pyplot as plt
import SimpleITK as sitk

class RescaleImage():
#this part of code rescaled input image resolution to quater of initial value
    def __init__(self, psf_raw_path, proj_num):
        self.data_path = psf_raw_path
        self.projection = proj_num
        self.image = pd.dcmread(self.data_path)
        self.image = self.image.pixel_array
        self.image = self.image[self.projection, :,:]

    def sum_adjacent(self, image, row, column):
        sum_array = []
        sum_array.append(image[row, column])
        sum_array.append(image[row, column+1])
        sum_array.append(image[row+1, column])
        sum_array.append(image[row+1, column+1])
        sumation = np.sum(sum_array)
        return sumation

    def init_rc(self, number, step):
        array_range = []
        for i in range(0, number, step):
            array_range.append(i)
        return array_range

    def rescale(self, image):
        rescaled_img = np.zeros((int(image.shape[0]/2), int(image.shape[1]/2)), dtype=f'{image.dtype}')
        row_range = self.init_rc(image.shape[0], 2)
        column_range = self.init_rc(image.shape[1], 2)
        i = 0
        j = 0
        for row in row_range:
            for column in column_range:
                rescaled_img[i,j] = self.sum_adjacent(image, row, column)
                j+=1
            i+=1
            j=0
        return rescaled_img

    def rescaleByHalf(self, **image):
        if(image):
            half_matrix_image = self.rescale(image)
            return half_matrix_image
        else:
            half_matrix_image = self.rescale(self.image)
            return half_matrix_image
            
    def rescaleByQuater(self):
        temp_image = self.rescaleByHalf(self.image)
        quater_matrix_image = self.rescaleByHalf(temp_image)
        return quater_matrix_image
    
#point_src_img = sitk.GetImageFromArray(rescaled_img_quater)

#this part of code computes 2D gamma camera detector 1 MTF as Fourier transform of point spread function imaged at source-detector distance = 25 cm

class computeMTF():
    def __init__(self, image):
        #image is a sitk format image
        self.image = image


    def findMaxima(self):
        image_array = self.image
        value = 0
        position = [0,0]
        for i in range(0, image_array.shape[0]):
            for j in range(0, image_array.shape[1]):
                if (image_array[i,j] > value):
                    value = image_array[i,j]
                    position[0] = i
                    position[1] = j
                else:
                    continue
        return value, position 

    def centerPointSourceImage(self):
        max_value, position_max = self.findMaxima()
        print("Maxima Value is:", max_value)
        print("position of maxima is:", position_max)
        translation_x = self.image.shape[0]/2 - position_max[0]
        translation_y = self.image.shape[1]/2 - position_max[1]
        print('translation_x is:', translation_x)
        print('translation_y is:', translation_y)
        dimension = 2
        offset = [2]*dimension
        translation_x = int(translation_x)
        translation_y = int(translation_y)
        image_array = self.image
        new_array = np.zeros(image_array.shape)
        for i in range(0, image_array.shape[0]):
            for j in range(0, image_array.shape[1]):
                if ((i+translation_x < image_array.shape[0]) and (j+translation_y < image_array.shape[1])):
                    new_array[i+translation_x, j+translation_y] = image_array[i,j]
                else:
                    continue
        return new_array

    def getMTF(self):
        point_src = self.centerPointSourceImage()
        point_src = point_src/np.amax(point_src)
        mtf = np.fft.fft2(point_src)
        mtf = np.fft.fftshift(mtf)
        return mtf

#sitk.Show(sitk.GetImageFromArray(np.log(1+mtf_modsq)))



print('finished')