import os
import re
import shutil
import urllib.request
import xml.etree.ElementTree as ET

def series_mmc(amazon_package_path):


    # get working directory
    path = os.getcwd()

    #move stuff out of amazon package

    amazon_package_path = amazon_package_path + '/CA/mec'

    for filename in os.listdir(amazon_package_path):
        
        fullname = os.path.join(amazon_package_path, filename)

        shutil.move(f'{fullname}', f'{path}/{filename}')

    for filename in os.listdir(path):
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(path, filename)

        if ("Season" not in filename and "Series" in filename and "Movie" not in filename and "episode" not in filename and "youtube" not in filename and "season" not in filename and "series" not in filename and "MMC" not in filename):
            
            tree = ET.parse(fullname)
            
            root = tree.getroot()

            identifier = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AltIdentifier/{http://www.movielabs.com/schema/md/v2.5/md}Identifier")
            
            appleid = identifier.text.replace("_", "").replace("Series", "")

            highest = []

            # use feed to find no of seasons
            def find_number_of_seasons():

                url = 'https://outtv-xml.herokuapp.com/xml_feeds/CA/availability.xml'

                response = urllib.request.urlopen(url).read()
                tree = ET.fromstring(response)

                title_pattern = re.compile(f'{appleid}s')
                print(title_pattern)
                
                for x in tree.findall(".//item"):
                    contentId = (x.attrib["contentId"])
                    
                    if bool(title_pattern.search(contentId)):
                        
                        series = (x.attrib["contentId"].rsplit('s', 1)[0])
                        seasonNumber = (x.attrib["contentId"].rsplit('s', 1)[1].rsplit('e', 1)[0])
                        episodeNumber = (x.attrib["contentId"].rsplit('e', 1)[1])

                        # amazon series id
                        seriesId = (f"{series}_Series")
                        # amazon season id
                        seasonId = (f"{series}_s{seasonNumber}")
                        # amazon episode id
                        episodeId = (f"{series}_s{seasonNumber}_e{episodeNumber}")
                        # get start date
                        startDate = x.find("./offers/offer/windowStart").text
                        # get end date
                        endDate = x.find("./offers/offer/windowEnd").text

                        highest.append(int(seasonNumber))

            find_number_of_seasons()

            print(max(highest))

            # copy template to use
            shutil.copy(f"{path}/mmc-templates/series-mmc2.xml", f"{path}/")
            
            # use copied template to add generic experiences
            template_filename = f"{path}/series-mmc2.xml"

            with open (template_filename, "a+") as myfile:

                for i in range(1, max(highest) + 1):
                    myfile.write(f'\n<manifest:ExperienceChild>\n<manifest:Relationship>isseasonof</manifest:Relationship>\n<manifest:SequenceInfo>\n<md:Number>{i}</md:Number>\n</manifest:SequenceInfo>\n<manifest:ExperienceID>md:experienceid:org:outtv:ExampleIDs{i}:experience</manifest:ExperienceID>\n<manifest:ExternalManifestID>md:manifestid:org:outtv:ExampleIDs{i}</manifest:ExternalManifestID>\n</manifest:ExperienceChild>')

                myfile.write('\n</manifest:Experience>\n</manifest:Experiences>\n</manifest:MediaManifest>')
            
            # rename to correct filename
            os.rename(template_filename, f"{path}/{appleid}_mmc_youtube.xml")

            # update to correct appleid
            f = f"{path}/{appleid}_mmc_youtube.xml"

            find = "ExampleID"
            replace = appleid

            with open (f, "r+") as myfile:
                s=myfile.read()
                ret = re.sub(find,replace, s)

                print(ret,  file=open(f'{path}/{appleid}_mmc_youtube.xml', 'w'))

if __name__ == '__main__':
    series_mmc()

