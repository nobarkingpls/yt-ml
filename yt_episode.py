import copy
import datetime
import os
from PIL import Image
import shutil
import xml.etree.ElementTree as ET
import re


def episode_mec():
    # get working directory
    path = os.getcwd()
    for filename in os.listdir(path):
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(path, filename)
        
        if ("Season" not in filename and "Series" not in filename and "Movie" not in filename and "episode" not in filename and "youtube" not in filename and filename.endswith('.xml') and "season" not in filename and 'movie' not in filename):
            
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
            
            try:
                for a in basic.attrib:
                    basic.attrib[a] = basic.attrib[a].replace("_", "")
            except:
                pass

            localizedinfo = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}LocalizedInfo")

            localizedinfo.set("language", "en")
            localizedinfo.set("default", "true")

            artref = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}LocalizedInfo/{http://www.movielabs.com/schema/md/v2.5/md}ArtReference")
			
            artref.set("purpose", "photo")

            artref.text = artref.text.replace("_", "")
            artref.text = artref.text.replace("-CA", "-photo")

            io = ET.SubElement(localizedinfo[1], 'md:ArtReference')
            io.set("purpose", "photo")
            io.set("resolution", "1440X1080")
            io.text = f"appleid-photo-1440x1080.png"

            # set all language in people to en
            displayname = root.findall("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}People/{http://www.movielabs.com/schema/md/v2.5/md}Name/{http://www.movielabs.com/schema/md/v2.5/md}DisplayName")
            
            for x in displayname:
                x.set("language", "en")

            # set original language value to en
            originallanguage = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}OriginalLanguage")
            originallanguage.text = "en"

            # delete <md:AltIdentifier>
            altidentifier = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AltIdentifier")
            basic.remove(altidentifier)

            # delete <md:AssociatedOrg organizationID='outtv' role='licensor'></md:AssociatedOrg>
            associatedorg = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AssociatedOrg")
            basic.remove(associatedorg)

            #change ids on ParentContentID.
            parentid = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}Parent/{http://www.movielabs.com/schema/md/v2.5/md}ParentContentID")

            parentid.text = parentid.text.replace("_", "")

            # set language in company display to en
            companydisplaystring = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}CompanyDisplayCredit/{http://www.movielabs.com/schema/md/v2.5/md}DisplayString")
            
            companydisplaystring.set("language", "en")

            newfilename = filename.replace("_", "").replace('.xml', '_mec_youtube.xml')
            
            tree.write(f"{newfilename}", encoding = "UTF-8", xml_declaration = True)

            # update movielabs numbers in coremetadata
            # Read in the file
            with open(f"{newfilename}", 'r') as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace('<mdmec:CoreMetadata xmlns:md="http://www.movielabs.com/schema/md/v2.5/md" xmlns:mdmec="http://www.movielabs.com/schema/mdmec/v2.5">', '<mdmec:CoreMetadata xmlns:md="http://www.movielabs.com/schema/md/v2.7/md" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mdmec="http://www.movielabs.com/schema/mdmec/v2.7" xsi:schemaLocation="http://www.movielabs.com/schema/mdmec/v2.7 mdmec-v2.7.1.xsd">')

            #add associated org line
            filedata = filedata.replace(f'</md:OriginalLanguage>\n<md:SequenceInfo>','</md:OriginalLanguage>\n<md:AssociatedOrg organizationID="outtv.com" role="licensor"></md:AssociatedOrg>\n<md:SequenceInfo>')

            # new 4:3 img line fixes
            appleid = newfilename.replace('_mec_youtube.xml', '')
            
            filedata = filedata.replace(f'><md:ArtReference purpose="photo" resolution="1440X1080">appleid-photo-1440x1080.png</md:ArtReference></md:TitleSort>', f' />\n<md:ArtReference purpose="photo" resolution="1440X1080">appleid-photo-1440x1080.png</md:ArtReference>')
            filedata = filedata.replace(f"appleid-photo-1440x1080.png", f"{appleid}-photo-1440x1080.png")

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

            #checks for episode ---------- new
            #check genres
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

            #check empty release date
            try:
                if '<md:ReleaseDate />' in filedata:
                    print(newfilename, ' has bad Release Date')
                    release_date_input('Enter a release date (eg 2024-02-26): ')
                    filedata = filedata.replace('<md:ReleaseDate />', f'<md:ReleaseDate>{release_date_input}</md:ReleaseDate>')
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

            #---------

            # Write the file out again
            with open(f"{newfilename}", 'w') as file:
                file.write(filedata)
                
            #create a directory using the appleid and a timestamp

            dir_name = newfilename.replace('_mec_youtube.xml', '')

            d = datetime.datetime.now()
            time_stamp = d.strftime("%Y%m%d_%H%M%S")

            os.makedirs(f'{dir_name}_{time_stamp}')

            #move xmls and img into newly created dir

            try:
                shutil.move(f'./{dir_name}_mmc_youtube.xml', f'./{dir_name}_{time_stamp}')
            except:
                pass

            shutil.move(f'./{dir_name}_mec_youtube.xml', f'./{dir_name}_{time_stamp}')

            # make enew youtube tv img ------------

            im = Image.open(f'/{path}/{dir_name}-CA-1920x1080.png')
            
            (left, upper, right, lower) = (240, 0, 1680, 1080)

            im2 = im.crop((left, upper, right, lower))
			
            im2 = im2.resize((1440, 1080))
			
            im2.save(f'./{dir_name}-photo-1440x1080.png')

            # move and rename 169 img

            try:
                shutil.move(f'./{dir_name}-CA-1920x1080.png', f'./{dir_name}_{time_stamp}/{dir_name}-photo-1920x1080.png')
            except:
                pass

            ## new move newly created youtube tv img

            try:
                shutil.move(f'./{dir_name}-photo-1440x1080.png', f'./{dir_name}_{time_stamp}')
            except:
                pass

            #cleanup old xml

            os.remove(fullname_for_later)

if __name__ == '__main__':
    episode_mec()