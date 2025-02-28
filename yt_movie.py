import datetime
import os
import re
import shutil
import xml.etree.ElementTree as ET
import re

def movie_mec():

    # get working directory
    path = os.getcwd()
    
    for filename in os.listdir(path):
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(path, filename)
        
        if ("Season" not in filename and "Series" not in filename and "Movie" in filename and "episode" not in filename and "youtube" not in filename and "season" not in filename and "series" not in filename and "MMC" not in filename):
            
            def register_all_namespaces(filename):
                namespaces = dict([node for _, node in ET.iterparse(filename, events=['start-ns'])])
                for ns in namespaces:
                    ET.register_namespace(ns, namespaces[ns])
            
            register_all_namespaces(filename)

            #store filename for later
            fullname_for_later = fullname
            
            tree = ET.parse(fullname)
            
            root = tree.getroot()

            basic = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic")
            
            for a in basic.attrib:
                basic.attrib[a] = basic.attrib[a].replace("_", "").replace("Movie", "")

            localizedinfo = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}LocalizedInfo")

            localizedinfo.set("language", "en")
            localizedinfo.set("default", "true")

            localizedinfo = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}LocalizedInfo")

            localizedinfo.set("language", "en")

            appleid = filename.replace('.xml','').replace('_Movie', '')

            artref = root.findall("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}LocalizedInfo/{http://www.movielabs.com/schema/md/v2.5/md}ArtReference")
            
            for _ in artref:
                localizedinfo.remove(_)

            io = ET.SubElement(localizedinfo[1], 'md:ArtReference')
            io.set("resolution", "2000X3000")
            io.set("purpose", "banner")
            io.text = f"{appleid}-banner-2000x3000.png"

            io = ET.SubElement(localizedinfo[1], 'md:ArtReference')
            io.set("resolution", "3840X2160")
            io.set("purpose", "banner")
            io.text = f"{appleid}-banner-3840x2160.png"

            io = ET.SubElement(localizedinfo[1], 'md:ArtReference')
            io.set("resolution", "3840X2160")
            io.set("purpose", "photo")
            io.text = f"{appleid}-photo-3840x2160.png"

            # # new youtube tv img -------
            io = ET.SubElement(localizedinfo[1], 'md:ArtReference')
            io.set("resolution", "4320X3240")
            io.set("purpose", "photo")
            io.text = f"{appleid}-photo-4320x3240.png"
        
            # delete <md:AltIdentifier>
            altidentifier = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AltIdentifier")
            basic.remove(altidentifier)

            # delete <md:AssociatedOrg organizationID='outtv' role='licensor'></md:AssociatedOrg>
            associatedorg = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}AssociatedOrg")
            basic.remove(associatedorg)

            # set all language in people to en
            displayname = root.findall("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}People/{http://www.movielabs.com/schema/md/v2.5/md}Name/{http://www.movielabs.com/schema/md/v2.5/md}DisplayName")

            for x in displayname:
                x.set("language", "en")

            # remove original language
            originallanguage = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}Basic/{http://www.movielabs.com/schema/md/v2.5/md}OriginalLanguage")
            basic.remove(originallanguage)

            # remove company disaply
            companydisplaycredit = root.find("{http://www.movielabs.com/schema/mdmec/v2.5}CompanyDisplayCredit")
            root.remove(companydisplaycredit)

            #ET.indent(tree, space="\t", level=0)
            tree.write(f"{appleid}_mec_youtube.xml", encoding = "UTF-8", xml_declaration = True)

            # update movielabs numbers in coremetadata
            # Read in the file
            with open(f"{appleid}_mec_youtube.xml", 'r') as file:
                filedata = file.read()

            # Replace the target string
            filedata = filedata.replace('<mdmec:CoreMetadata xmlns:md="http://www.movielabs.com/schema/md/v2.5/md" xmlns:mdmec="http://www.movielabs.com/schema/mdmec/v2.5" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.movielabs.com/schema/mdmec/v2.5 ../mdmec-v2.5.xsd">', '<mdmec:CoreMetadata xmlns:md="http://www.movielabs.com/schema/md/v2.7/md" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mdmec="http://www.movielabs.com/schema/mdmec/v2.7" xsi:schemaLocation="http://www.movielabs.com/schema/mdmec/v2.7 mdmec-v2.7.1.xsd">')

            # add line after title sort
            filedata = filedata.replace('<md:TitleSort>', '<md:TitleSort />\n')\
            
            filedata = filedata.replace('</md:TitleSort>', '')

            # put line between art refs
            filedata = filedata.replace('</md:ArtReference><md:ArtReference', '</md:ArtReference>\n<md:ArtReference')

            #add new associated org line
            filedata = filedata.replace(f'</md:People>\n</mdmec:Basic>','</md:People>\n<md:AssociatedOrg organizationID="outtv.com" role="licensor"></md:AssociatedOrg>\n</mdmec:Basic>')
            
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

            # rating exapnsion to all regions movie edition >>
            # ca value G
            try:
                filedata = filedata.replace(
                    '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CHVRS</md:System>\n<md:Value>G</md:Value>\n</md:Rating>', '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CHVRS</md:System>\n<md:Value>G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>US</md:country>\n</md:Region>\n<md:System>MPAA</md:System>\n<md:Value>G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>AU</md:country>\n</md:Region>\n<md:System>NCS</md:System>\n<md:Value>G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>NZ</md:country>\n</md:Region>\n<md:System>OFLC</md:System>\n<md:Value>G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>GB</md:country>\n</md:Region>\n<md:System>BBFC</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>IE</md:country>\n</md:Region>\n<md:System>IFCOF</md:System>\n<md:Value>G</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>BR</md:country>\n</md:Region>\n<md:System>DJCTQ</md:System>\n<md:Value>10</md:Value>\n</md:Rating>'
                    )
            except:
                pass

            # ca value PG
            try:
                filedata = filedata.replace(
                    '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CHVRS</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>', '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CHVRS</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>US</md:country>\n</md:Region>\n<md:System>MPAA</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>AU</md:country>\n</md:Region>\n<md:System>NCS</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>NZ</md:country>\n</md:Region>\n<md:System>OFLC</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>GB</md:country>\n</md:Region>\n<md:System>BBFC</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>IE</md:country>\n</md:Region>\n<md:System>IFCOF</md:System>\n<md:Value>PG</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>BR</md:country>\n</md:Region>\n<md:System>DJCTQ</md:System>\n<md:Value>12</md:Value>\n</md:Rating>'
                    )
            except:
                pass

            # ca value 14 > m
            try:
                filedata = filedata.replace(
                    '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CHVRS</md:System>\n<md:Value>14A</md:Value>\n</md:Rating>', '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CHVRS</md:System>\n<md:Value>14A</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>US</md:country>\n</md:Region>\n<md:System>MPAA</md:System>\n<md:Value>M</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>AU</md:country>\n</md:Region>\n<md:System>NCS</md:System>\n<md:Value>M</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>NZ</md:country>\n</md:Region>\n<md:System>OFLC</md:System>\n<md:Value>M</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>GB</md:country>\n</md:Region>\n<md:System>BBFC</md:System>\n<md:Value>15</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>IE</md:country>\n</md:Region>\n<md:System>IFCOF</md:System>\n<md:Value>16</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>BR</md:country>\n</md:Region>\n<md:System>DJCTQ</md:System>\n<md:Value>14</md:Value>\n</md:Rating>'
                    )
            except:
                pass

            # ca value 18 > 
            try:
                filedata = filedata.replace(
                    '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CHVRS</md:System>\n<md:Value>18A</md:Value>\n</md:Rating>', '<md:Rating>\n<md:Region>\n<md:country>CA</md:country>\n</md:Region>\n<md:System>CHVRS</md:System>\n<md:Value>18A</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>US</md:country>\n</md:Region>\n<md:System>MPAA</md:System>\n<md:Value>R</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>AU</md:country>\n</md:Region>\n<md:System>NCS</md:System>\n<md:Value>R18+</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>NZ</md:country>\n</md:Region>\n<md:System>OFLC</md:System>\n<md:Value>R</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>GB</md:country>\n</md:Region>\n<md:System>BBFC</md:System>\n<md:Value>18</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>IE</md:country>\n</md:Region>\n<md:System>IFCOF</md:System>\n<md:Value>18</md:Value>\n</md:Rating>\n<md:Rating>\n<md:Region>\n<md:country>BR</md:country>\n</md:Region>\n<md:System>DJCTQ</md:System>\n<md:Value>18</md:Value>\n</md:Rating>'
                    )
            except:
                pass

            #checks for movie ---------- new
            #check genres
            try:
                if 'av_genre' in filedata:
                    print(appleid, ' has a bad Genre')
                    match = re.search(r' id=.av_genre_.*/>', filedata).group(0)
                    genre_input = input('Enter a genre (eg. Comedy, Drama, Reality, Documentary): ')
                    filedata = filedata.replace(match, f'>{genre_input}</md:Genre>\n<md:Genre>Gay Lesbian</md:Genre>')
                    except:
                        pass

            #check empty year
            try:
                if '<md:ReleaseYear />' in filedata:
                    print(appleid, ' has bad Year')
                    year_input = input('Enter a Year (eg 2024): ')
                    filedata = filedata.replace('<md:ReleaseYear />', f'<md:ReleaseYear>{year_input}</md:ReleaseYear>')
            except:
                pass

            #check empty release date
            try:
                if '<md:ReleaseDate />' in filedata:
                    print(appleid, ' has bad Release Date')
                    release_date_input('Enter a release date (eg 2024-02-26): ')
                    filedata = filedata.replace('<md:ReleaseDate />', f'<md:ReleaseDate>{release_date_input}</md:ReleaseDate>')
            except:
                pass

            #check empty company display credit
            try:
                if '<mdmec:CompanyDisplayCredit>\n<md:DisplayString language="en" />\n</mdmec:CompanyDisplayCredit>' in filedata:
                    print(appleid, ' has bad Company Display Credit')
                    company_input = input('Enter a production company: ')
                    filedata = filedata.replace('<mdmec:CompanyDisplayCredit>\n<md:DisplayString language="en" />\n</mdmec:CompanyDisplayCredit>', f'<mdmec:CompanyDisplayCredit>\n<md:DisplayString language="en">{company_input}</md:DisplayString>\n</mdmec:CompanyDisplayCredit>')
            except:
                pass

            #check ratings populated
            try:
                if '<md:System>MPAA</md:System>' not in filedata:
                    print(appleid, ' has bad Ratings')
            except:
                pass


            # Write the file out again
            with open(f"{appleid}_mec_youtube.xml", 'w') as file:
                file.write(filedata)
                
            # make a unique timestamped dir
            d = datetime.datetime.now()
            time_stamp = d.strftime("%Y%m%d_%H%M%S")

            os.makedirs(f'{appleid}_{time_stamp}')

            #move xml and imgs into newly created dir

            try:
                shutil.move(f'./{appleid}_mmc_youtube.xml', f'./{appleid}_{time_stamp}')
            except:
                pass

            shutil.move(f'./{appleid}_mec_youtube.xml', f'./{appleid}_{time_stamp}')

            try:
                shutil.move(f'./{appleid}-banner-3840x2160.png', f'./{appleid}_{time_stamp}')
                shutil.move(f'./{appleid}-photo-3840x2160.png', f'./{appleid}_{time_stamp}')
            except:
                pass
            
            #cleanup old xml
            
            os.remove(fullname_for_later)

if __name__ == '__main__':
    movie_mec()