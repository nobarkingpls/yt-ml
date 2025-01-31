import os
import re
import shutil
import urllib.request
import xml.etree.ElementTree as ET

def season_mmc():

    # get working directory
    path = os.getcwd()

    highest = []

    # use xmls in folder to fill out IDs
    for filename in os.listdir(path):
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(path, filename)
        
        if ("Season" in filename and "Series" not in filename and "Movie" not in filename and "episode" not in filename and "youtube" not in filename and "season" not in filename and "series" not in filename and "MMC" not in filename):
            
            tree = ET.parse(fullname)

            root = tree.getroot()

            identifier = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AltIdentifier/{http://www.movielabs.com/schema/md/v2.5/md}Identifier")
            appleid = identifier.text.replace("_", "")

            # use feed to find no of seasons
            def find_number_of_episodes():

                url = 'https://outtv-xml.herokuapp.com/xml_feeds/CA/availability.xml'

                response = urllib.request.urlopen(url).read()
                tree = ET.fromstring(response)


                title_pattern = re.compile(f'{appleid}')
                
                print('title pattern is ', {title_pattern})
                
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

                        highest.append(int(episodeNumber))

            find_number_of_episodes()
                        
            print(max(highest))

            # copy template to use
            shutil.copy(f"{path}/mmc-templates/season-mmc2.xml", f"{path}/")

            # use copied template
            template_filename = f"{path}/season-mmc2.xml"

            # add generic experiences

            with open (template_filename, "a+") as myfile:

                for i in range(1, max(highest) + 1):
                    myfile.write(f'\n<manifest:ExperienceChild>\n<manifest:Relationship>isepisodeof</manifest:Relationship>\n<manifest:SequenceInfo>\n<md:Number>{i}</md:Number>\n</manifest:SequenceInfo>\n<manifest:ExperienceID>md:experienceid:org:outtv:ExampleIDe{i}:experience</manifest:ExperienceID>\n<manifest:ExternalManifestID>md:manifestid:org:outtv:ExampleIDe{i}</manifest:ExternalManifestID>\n</manifest:ExperienceChild>')

                myfile.write('\n</manifest:Experience>\n</manifest:Experiences>\n</manifest:MediaManifest>')

            # rename to correct name
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
    season_mmc()