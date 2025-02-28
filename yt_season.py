import datetime
import os
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import re

def season_mec():

    def remove_blank_lines(file):
        lines = file.read_text().splitlines()
        filtered = [
            line
            for line in lines
            if line.strip()
        ]
        file.write_text('\n'.join(filtered))

    # get working directory
    path = os.getcwd()
    
    for filename in os.listdir(path):
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(path, filename)
        
        if ("Season" in filename and "Series" not in filename and "Movie" not in filename and "episode" not in filename and "youtube" not in filename and 'season' not in filename and 'mmc' not in filename):
            
            def register_all_namespaces(filename):
                namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
                for ns in namespaces:
                    ET.register_namespace(ns, namespaces[ns])
            
            register_all_namespaces(filename)

            #store filename for later
            fullname_for_later = fullname
            
            tree = ET.parse(fullname)

            root = tree.getroot()

            #change id to appleid
            basic = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic")
            
            for a in basic.attrib:
                basic.attrib[a] = basic.attrib[a].replace("_", "")

            localizedinfo = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}LocalizedInfo")

            localizedinfo.set("language", "en")
            localizedinfo.set("default", "true")

            for delartrefs in range(3):
                localizedinfo = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}LocalizedInfo")

                artref = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}LocalizedInfo/{http://www.movielabs.com/schema/md/v2.5/md}ArtReference")

                localizedinfo.remove(artref)
            
            # set all language in people to en
            displayname = root.findall("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}People/{http://www.movielabs.com/schema/md/v2.5/md}Name/{http://www.movielabs.com/schema/md/v2.5/md}DisplayName")

            for x in displayname:
                x.set("language", "en")

            # delete <md:AltIdentifier>
            altidentifier = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AltIdentifier")
            basic.remove(altidentifier)

            # delete <md:AssociatedOrg organizationID='outtv' role='licensor'></md:AssociatedOrg>
            associatedorg = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AssociatedOrg")
            basic.remove(associatedorg)

            #change ids on ParentContentID.
            parentid = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}Parent/{http://www.movielabs.com/schema/md/v2.5/md}ParentContentID")

            parentid.text = parentid.text.replace("_", "").replace('Series', '')

            # set original language value to en
            originallanguage = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}OriginalLanguage")
            originallanguage.text = "en"

            # set language in company display to en
            companydisplaystring = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}CompanyDisplayCredit/{http://www.movielabs.com/schema/md/v2.5/md}DisplayString")

            companydisplaystring.set("language", "en")

            newfilename = filename.replace("Amazon_MEC_Season_", "").replace("_", "").replace('.xml', '_mec_youtube.xml')
            
            #ET.indent(tree, space="\t", level=0)
            tree.write(f"{newfilename}", encoding = "UTF-8", xml_declaration = True)

            # update movielabs numbers in coremetadata
            # Read in the file
            with open(f"{newfilename}", 'r') as file:
                filedata = file.read()

            # remove blank lines
            filedata = filedata.replace('\n\n', '\n')
            # remove blank lines
            filedata = filedata.replace('\n\n', '\n')

            # Replace the target string
            filedata = filedata.replace('<mdmec:CoreMetadata xmlns:md="http://www.movielabs.com/schema/md/v2.5/md" xmlns:mdmec="http://www.movielabs.com/schema/mdmec/v2.5" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.movielabs.com/schema/mdmec/v2.5 ../mdmec-v2.5.xsd">', '<mdmec:CoreMetadata xmlns:md="http://www.movielabs.com/schema/md/v2.7/md" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mdmec="http://www.movielabs.com/schema/mdmec/v2.7" xsi:schemaLocation="http://www.movielabs.com/schema/mdmec/v2.7 mdmec-v2.7.1.xsd">')

            #add new release history section
            # filedata = filedata.replace(f'</md:ReleaseYear>\n<md:WorkType>','</md:ReleaseYear>\n<md:ReleaseHistory>\n<md:ReleaseType>original</md:ReleaseType>\n<md:Date>YYYY</md:Date>\n</md:ReleaseHistory>\n<md:WorkType>')

            #add new associated org line
            filedata = filedata.replace(f'</md:OriginalLanguage>\n<md:SequenceInfo>','</md:OriginalLanguage>\n<md:AssociatedOrg organizationID="outtv.com" role="licensor"></md:AssociatedOrg>\n<md:SequenceInfo>')
            
            # genre conversions
            try:
                filedata = filedata.replace(' id="av_genre_documentary" />', '>Documentary</md:Genre>\n<md:Genre>Gay Lesbian</md:Genre>')
            except:
                pass
            try:
                filedata = filedata.replace(' id="av_genre_unscripted" />', '>Reality</md:Genre>\n<md:Genre>Gay Lesbian</md:Genre>')
            except:
                pass
            try:
                filedata = filedata.replace(' id="av_genre_drama" />', '>Drama</md:Genre>\n<md:Genre>Gay Lesbian</md:Genre>')
            except:
                pass
            try:
                filedata = filedata.replace(' id="av_genre_comedy" />', '>Comedy</md:Genre>\n<md:Genre>Gay Lesbian</md:Genre>')
            except:
                pass
            try:
                filedata = filedata.replace(' id="av_genre_special_interest" />', '>Reality</md:Genre>\n<md:Genre>Gay Lesbian</md:Genre>')
            except:
                pass

            # rating exapnsion to all regions >>
            # ca value G
            try:
                filedata = filedata.replace(
                    '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CBSC</md:System>\n<md:Value>G</md:Value>\n</md:Rating>', '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CBSC</md:System>\n<md:Value>G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>US</md:country>\n</md:Region>\n<md:System>TVPG</md:System>\n<md:Value>TV-G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>AU</md:country>\n</md:Region>\n<md:System>NCS</md:System>\n<md:Value>G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>NZ</md:country>\n</md:Region>\n<md:System>OFLC</md:System>\n<md:Value>G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>GB</md:country>\n</md:Region>\n<md:System>BBFC</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>IE</md:country>\n</md:Region>\n<md:System>RTE</md:System>\n<md:Value>GA</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>BR</md:country>\n</md:Region>\n<md:System>DJCTQ</md:System>\n<md:Value>10</md:Value>\n</md:Rating>'
                    )
            except:
                pass

            # ca value PG
            try:
                filedata = filedata.replace(
                    '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CBSC</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>', '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CBSC</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>US</md:country>\n</md:Region>\n<md:System>TVPG</md:System>\n<md:Value>TV-PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>AU</md:country>\n</md:Region>\n<md:System>NCS</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>NZ</md:country>\n</md:Region>\n<md:System>OFLC</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>GB</md:country>\n</md:Region>\n<md:System>BBFC</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>IE</md:country>\n</md:Region>\n<md:System>RTE</md:System>\n<md:Value>GA</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>BR</md:country>\n</md:Region>\n<md:System>DJCTQ</md:System>\n<md:Value>12</md:Value>\n</md:Rating>'
                    )
            except:
                pass

            # ca value 14 > m
            try:
                filedata = filedata.replace(
                    '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CBSC</md:System>\n<md:Value>14</md:Value>\n</md:Rating>', '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CBSC</md:System>\n<md:Value>14</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>US</md:country>\n</md:Region>\n<md:System>TVPG</md:System>\n<md:Value>TV-14</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>AU</md:country>\n</md:Region>\n<md:System>NCS</md:System>\n<md:Value>M</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>NZ</md:country>\n</md:Region>\n<md:System>OFLC</md:System>\n<md:Value>M</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>GB</md:country>\n</md:Region>\n<md:System>BBFC</md:System>\n<md:Value>15</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>IE</md:country>\n</md:Region>\n<md:System>RTE</md:System>\n<md:Value>PS</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>BR</md:country>\n</md:Region>\n<md:System>DJCTQ</md:System>\n<md:Value>14</md:Value>\n</md:Rating>'
                    )
            except:
                pass

            # ca value 18 > 
            try:
                filedata = filedata.replace(
                    '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CBSC</md:System>\n<md:Value>18</md:Value>\n</md:Rating>', '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CBSC</md:System>\n<md:Value>18</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>US</md:country>\n</md:Region>\n<md:System>TVPG</md:System>\n<md:Value>TV-MA</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>AU</md:country>\n</md:Region>\n<md:System>NCS</md:System>\n<md:Value>R18+</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>NZ</md:country>\n</md:Region>\n<md:System>OFLC</md:System>\n<md:Value>R</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>GB</md:country>\n</md:Region>\n<md:System>BBFC</md:System>\n<md:Value>18</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>IE</md:country>\n</md:Region>\n<md:System>RTE</md:System>\n<md:Value>MA</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>BR</md:country>\n</md:Region>\n<md:System>DJCTQ</md:System>\n<md:Value>18</md:Value>\n</md:Rating>'
                    )
            except:
                pass

            #checks for series/season
            #check empty genres
            try:
                if 'av_genre' in filedata:
                    print(newfilename, ' has a bad Genre')
                    match = re.search(r' id=.av_genre_.*/>', filedata).group(0)
                    genre_input = input('Enter a genre (eg. Comedy, Drama, Reality, Documentary): ')
                    filedata = filedata.replace(match, f'>{genre_input}</md:Genre>\n<md:Genre>Gay Lesbian</md:Genre>')
            except:
                pass

            #check empty year
            try:
                if '<md:ReleaseYear />' in filedata:
                    print(newfilename, ' has bad Year')
                    year_input = input('Enter a Year (eg 2024): ')
                    filedata = filedata.replace('<md:ReleaseYear />', f'<md:ReleaseYear>{year_input}</md:ReleaseYear>')
            except:
                pass

            #check empty company display credit
            try:
                if '<mdmec:CompanyDisplayCredit>\n<md:DisplayString language="en" />\n</mdmec:CompanyDisplayCredit>' in filedata:
                    print(newfilename, ' has bad Company Display Credit')
                    company_input = input('Enter a production company: ')
                    filedata = filedata.replace('<mdmec:CompanyDisplayCredit>\n<md:DisplayString language="en" />\n</mdmec:CompanyDisplayCredit>', f'<mdmec:CompanyDisplayCredit>\n<md:DisplayString language="en">{company_input}</md:DisplayString>\n</mdmec:CompanyDisplayCredit>')
            except:
                pass

            #check ratings populated
            try:
                if '<md:System>TVPG</md:System>' not in filedata:
                    print(newfilename, ' has bad Ratings')
            except:
                pass

            # Write the file out again
            with open(f"{newfilename}", 'w') as file:
                file.write(filedata)

            #create a directory using the appleid and a timestamp

            dir_name = newfilename.replace('_mec_youtube.xml', '')

            d = datetime.datetime.now()
            time_stamp = d.strftime("%Y%m%d_%H%M%S")

            os.makedirs(f'{dir_name}_{time_stamp}')

            #move xml into newly created dir

            try:
                shutil.move(f'./{dir_name}_mmc_youtube.xml', f'./{dir_name}_{time_stamp}')
            except:
                pass

            shutil.move(f'./{dir_name}_mec_youtube.xml', f'./{dir_name}_{time_stamp}')
            
            #cleanup old xml
            os.remove(fullname_for_later)

if __name__ == '__main__':
    season_mec()