import os
import shutil

def movie_images(amazon_package_path):

    # get working directory
    path = os.getcwd()

    #move stuff out of amazon package

    amazon_package_path = amazon_package_path + '/images'

    for filename in os.listdir(amazon_package_path):

        fullname = os.path.join(amazon_package_path, filename)

        if 'CA-cover' in filename:

            if '_' in filename:
        	
                appleid, trash = filename.split('_')
            
            else:

                appleid = filename
                
            shutil.move(f'{fullname}', f'{path}/{appleid}-banner-3840x2160.png')

        if 'CA-hero' in filename:

            if '_' in filename:
        	
                appleid, trash = filename.split('_')
            
            else:

                appleid = filename

            shutil.move(f'{fullname}', f'{path}/{appleid}-photo-3840x2160.png')

#movie_images()

