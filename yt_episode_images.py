import os
import shutil
import sys

def episode_images(amazon_package_path):

	# set working directory

	current_directory = os.getcwd()

    #move stuff out of amazon package

	amazon_package_path = amazon_package_path + '/images'
   
	for filename in os.listdir(amazon_package_path):

		fullname = os.path.join(amazon_package_path, filename)

		try:
			if 'CA-cover' in filename:

				appleid, trash = filename.split('_', 1)

				shutil.move(f'{fullname}', f'{current_directory}/{appleid.replace('_', '')}-banner-3840x2160.png')

			if 'CA-hero' in filename:

				appleid, trash = filename.split('_', 1)

				shutil.move(f'{fullname}', f'{current_directory}/{appleid.replace('_', '')}-photo-3840x2160.png')
            
			if 'CA-1920x1080' in filename:

				appleid, trash = filename.split('-', 1)

				shutil.move(f'{fullname}', f'{current_directory}/{appleid.replace('_', '')}-CA-1920x1080.png')
            
		except:
			pass

if __name__ == '__main__':
	episode_images(image_path)

