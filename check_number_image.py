## -*- coding: utf-8 -*-
#"""
#Created on Sat Nov  6 11:24:31 2021
#
#@author: Formation
#"""
#
import json
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
import random
import os
chemin="dataset"

# proportion_train= 0.7
# proportion_val=0.05
# proportion_test=0.25

# try:
#     os.makedirs(chemin+"/train")
#     os.makedirs(chemin+"/test")
#     os.makedirs(chemin+"/val")
# except:
#     pass

# path_actino = 'train_actino.json'

# with open(path_actino) as actino_data :
#     actino_json = json.load(actino_data)

# print(actino_json['images'][0])

# list_categoriesid = []
# list_imageid = []
# dic_image_id_filename={val["id"]:val["file_name"] for val in actino_json['images']}
# for i in range (len(actino_json["annotations"])):
#     list_categoriesid.append(actino_json["annotations"][i]["category_id"])
#     list_imageid.append(actino_json["annotations"][i]["image_id"])
    
# array_categoriesid = np.array(list_categoriesid)
# array_imageid = np.array(list_imageid)
# print(array_categoriesid)

# unique_value, frequencies = np.unique(array_categoriesid, return_counts=True)
# print(np.min(frequencies))
# print(np.max(frequencies))

# plt.bar(unique_value,frequencies, width=0.8)
# plt.show()

# #Récupérer les id des données où il y a plus de 25 images eulement
# bool_arr = frequencies >= 25
# index_sup25 = unique_value[bool_arr]

# for index in index_sup25:
  
#     cat_temp=array_categoriesid[np.where(array_categoriesid == index)]
#     print(array_categoriesid,index)
#     im_temp=array_imageid[np.where(array_categoriesid == index)]
#     for i,imageid in enumerate(im_temp):
#         if(os.path.isfile(dic_image_id_filename[imageid])):
#             alea= random.random()
#             if alea< proportion_train:
#                 dossier='/train/'
#             elif alea<proportion_train+proportion_val:
#                 dossier='/val/'
#             else:
#                 dossier="/test/"
#             try:
#                 os.mkdir(chemin+dossier+cat_temp[i].astype(str) )
#             except:
#                 pass
#             shutil.copy(dic_image_id_filename[imageid], chemin+dossier+cat_temp[i].astype(str)+"/"+os.path.basename(dic_image_id_filename[imageid]))
    
    

# print(array_categoriesid )

import glob
from skimage.io import imread
list_tmp=[]
list_std=[]
for image in glob.glob("C:/Users/INES/Documents/Ocean Hack/dataset/**/**/*.jpg"):
    im=imread(image)
    list_tmp.append( im.mean(axis=(0,1)))
    list_std.append( im.std(axis=(0,1)))
list_tmp=np.array(list_tmp)
list_std=np.array(list_std)
print(list_tmp.mean(0),list_std.mean(0))

