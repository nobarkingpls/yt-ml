import os
import re
import xml.etree.ElementTree as ET

def episode_mmc():

    # get working directory
    path = os.getcwd()
    for filename in os.listdir(path):
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(path, filename)
        
        if ("Season" not in filename and "Series" not in filename and "Movie" not in filename and "episode" not in filename and "youtube" not in filename and "season" not in filename and "series" not in filename and "MMC" not in filename and 'movie' not in filename):
            
            tree = ET.parse(fullname)
            
            root = tree.getroot()

            identifier = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AltIdentifier/{http://www.movielabs.com/schema/md/v2.5/md}Identifier")
            appleid = identifier.text.replace("_", "")

            template_filename = f"{path}/mmc-templates/episode-mmc2-version.xml"

            f = template_filename
            find = "ExampleID"
            replace = appleid
            with open (f, "r+") as myfile:
                s=myfile.read()
                ret = re.sub(find,replace, s) 

                print(ret,  file=open(f'{path}/{appleid}_mmc_youtube.xml', 'w'))

if __name__ == '__main__':
    episode_mmc()


