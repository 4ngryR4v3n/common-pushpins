from recon.core.module import BaseModule
import codecs
import os
import re
import time
import webbrowser
import math
#import pdb


class Module(BaseModule):

    meta = {
        'name': 'Common Pushpin Usernames',
        'author': '4ngryR4v3n - forked from the PushPin Report Generator module created by Tim Tomes (@lanmaster53)',
        'version': '1.0',
        'description': 'Finds the usernames that are common between locations.',
        'required_keys': ['google_api'],

        'options': (
            ('latitude', None, True, 'latitude of the epicenter'),
            ('longitude', None, True, 'longitude of the epicenter'),
            ('radius', None, True, 'radius from the epicenter in kilometers'),
            ('map_filename', os.path.join(BaseModule.workspace, 'pushpin_map.html'), True, 'path and filename for PushPin map report'),
            ('media_filename', os.path.join(BaseModule.workspace, 'pushpin_media.html'), True, 'path and filename for PushPin media report'),
            ('search_radius', 1, True, 'search radius from each location in locations table'),
            ('verbosity', 1, True, '(1)common users (2)+unique users per location (3)+pushpins per location')
        ),        
        'files': ['template_media.html', 'template_map.html'],
    }


    def getLocations(self):
        uLocs = []
        uniqueLocation = []
        points = self.query('SELECT DISTINCT latitude || \',\' || longitude FROM locations WHERE latitude IS NOT NULL AND longitude IS NOT NULL'),
        for point in points[0]:
            latitude, longitude = point[0].split(',')
            uLocs.append([latitude, longitude])
        for uLoc in uLocs:
            uniqueLocation.append(self.query('SELECT * FROM locations WHERE latitude=? AND longitude=?', (uLoc[0], uLoc[1],)))
        return uniqueLocation


    def aliasDots(self,x,y):
        dots = "........................................................"
        user = str(x)
        alias = str(y)
        dotstrimmed = dots[0:-len(user+alias)]
        aka = " \'" + user + "\'" + dotstrimmed + "\'" + alias + "\'"
        return aka 


    def printCommonUsers(self,user,x):
        self.output(f"{user}  in location {x + 1}")


    def appendUniqueUser(self,user,alias,x):
        appendMe = []
        appendMe.append(user)
        appendMe.append(alias)
        appendMe.append(x)
        return appendMe 


    def compareUniqueUsers(self,completeUniqueUsers): 
        commonUniqueUsers = []
        listLength = len(completeUniqueUsers)
        locCount = 0        
        print("")
        print("")
        print("================================================================================")
        print(f"Finding common users") 
        print("================================================================================")
        print("")
        print(f"Unique common users between locations found:")
        print("")
        print("     Screen Name                                     Profile Name")
        for x in range(listLength):#check each location
            for y in completeUniqueUsers[x]:
                for xx in range((x+1),listLength):
                    for yy in completeUniqueUsers[xx]:                    
                        if y[0] == yy[0]:
                            appendMeReturned = self.appendUniqueUser(y[0],y[1],x)
                            if appendMeReturned not in commonUniqueUsers:
                                commonUniqueUsers.append(appendMeReturned)
                            appendMeReturned = self.appendUniqueUser(yy[0],yy[1],xx)
                            if appendMeReturned not in commonUniqueUsers:
                                commonUniqueUsers.append(appendMeReturned)
                        elif y[0] == yy[1]:
                            appendMeReturned = self.appendUniqueUser(y[0],y[1],x)
                            if appendMeReturned not in commonUniqueUsers:
                                commonUniqueUsers.append(appendMeReturned)
                            appendMeReturned = self.appendUniqueUser(yy[0],yy[1],xx)
                            if appendMeReturned not in commonUniqueUsers:
                                commonUniqueUsers.append(appendMeReturned)
                        elif y[1] == yy[0]:
                            appendMeReturned = self.appendUniqueUser(y[0],y[1],x)
                            if appendMeReturned not in commonUniqueUsers:
                                commonUniqueUsers.append(appendMeReturned)
                            appendMeReturned = self.appendUniqueUser(yy[0],yy[1],xx)
                            if appendMeReturned not in commonUniqueUsers:
                                commonUniqueUsers.append(appendMeReturned)
                        elif y[1] == yy[1]:
                            appendMeReturned = self.appendUniqueUser(y[0],y[1],x)
                            if appendMeReturned not in commonUniqueUsers:
                                commonUniqueUsers.append(appendMeReturned)
                            appendMeReturned = self.appendUniqueUser(yy[0],yy[1],xx)
                            if appendMeReturned not in commonUniqueUsers:
                                commonUniqueUsers.append(appendMeReturned)
            locCount += 1
        nextUser = []
        for x in commonUniqueUsers:
            if nextUser != [x[0],x[1]]:
                print("")
            self.printCommonUsers(self.aliasDots(x[0],x[1]),x[2])
            nextUser = [x[0],x[1]]
        print("")
        print("")
        print("")
        return commonUniqueUsers


    def findCommonUsers(self, sources):
        culledPossibleItems = []
        possibleitems = self.query('SELECT * FROM pushpins')
        completeUniqueUsers = []
        verbosityOption = self.options['verbosity']

        # Get unique locations from database
        uniqueLocations = self.getLocations()

        # Iterate each unique location
        print("")
        print("")
        locationCount = 0
        for uniqueLocation in uniqueLocations:
            cPI = []
            possibleUsers = []
            culledUniqueUsers = []
            cUU = []
            if verbosityOption > 1:
                print("================================================================================")
                print(f"Location {locationCount + 1}")
                print(f"    Latitude: {uniqueLocation[0][0]}")
                print(f"    Longitude: {uniqueLocation[0][1]}")
                print(f"    Address: {uniqueLocation[0][2]}")
                print(f"    Notes: {uniqueLocation[0][4]}")
                print("================================================================================")
                print("")

            searchRad = self.options['search_radius'] 

            for possibleitem in possibleitems:
                ulLat = float(uniqueLocation[0][0])
                ulLong = float(uniqueLocation[0][1])
                rDistance = (math.sqrt(((abs((ulLat) - (float(possibleitem[7]))))**2) + ((abs((ulLong) - (float(possibleitem[8]))))**2)))
                if rDistance < (searchRad * .00898311):
                    cPI.append(possibleitem)
            culledPossibleItems.append(cPI)

            for x in culledPossibleItems[locationCount]:
                possUsrs = []
                if verbosityOption > 2:
                    print(f"Source: {x[0]}")
                    print(f"Profile Name: {x[1]}    Screen Name: {x[2]}")
                    print(f"Message: {x[6]}")
                    print(f"Profile Page: {x[3]}")
                    print("")
                possUsrs.append(x[1])
                possUsrs.append(x[2])
                possibleUsers.append(possUsrs)

            #Cull all duplicate users during each unque location pass
            for x in possibleUsers:
                if x not in culledUniqueUsers:
                    culledUniqueUsers.append(x)

            if verbosityOption > 1:
                cUULength = len(culledUniqueUsers)
    
                if cUULength > 1:
                    print("--------------------------------------------------------------------------------")
                    print(f"Unique Users Found in location {locationCount +1}")
                    print("--------------------------------------------------------------------------------")
                elif cUULength == 1:
                    print("--------------------------------------------------------------------------------")
                    print(f"One Unique User Found in location {locationCount +1}")
                    print("--------------------------------------------------------------------------------")
                else:
                    print("")

                print("")
                print("     Screen Name                                     Profile Name")
                print("")

                for culledUniqueUser in culledUniqueUsers:
                    self.output(self.aliasDots(culledUniqueUser[0],culledUniqueUser[1]))
                    cUU.append(culledUniqueUser)
            else:
                for culledUniqueUser in culledUniqueUsers:
                    cUU.append(culledUniqueUser)
    
            completeUniqueUsers.append(cUU)

            if verbosityOption > 1:
                print("")
                print("")

            locationCount +=1

        #Find all unique common users between locations
        commonUniqueUsers = self.compareUniqueUsers(completeUniqueUsers)
        return commonUniqueUsers


    def getSources(self,commonUniqueUsers):
        culledSources = []
        possibleitems = self.query('SELECT * FROM pushpins')
        for possibleitem in possibleitems:
            for commonUniqueUser in commonUniqueUsers:
                if possibleitem[1] in commonUniqueUser or possibleitem[2] in commonUniqueUser:
                    culledSources.append(possibleitem)
        return culledSources
        

    def remove_nl(self, x, repl=''):
        return re.sub('[\r\n]+', repl, self.html_escape(x))

    def build_content(self, sources, culledSources):
        icons = {
            'flickr': 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
            'instagram': 'http://maps.google.com/mapfiles/ms/icons/pink-dot.png',
            'picasa': 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
            'shodan': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
            'twitter': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
            'youtube': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
        }

        media_content = ''
        map_content = ''
        map_arrays = ''
        map_checkboxes = ''

        for source in sources:
            items = []
            count = 0 
            source = source[1]

            #add items to output list by source
            for culledSource in culledSources:
                if source in culledSource and culledSource not in items:
                    items.append(culledSource)
                    count +=1

            map_arrays += f"var {source.lower()} = [];\n"
            map_checkboxes += f'<input type="checkbox" id="{source.lower()}" onchange="toggleMarkers(\'{source.lower()}\');" checked="checked"/>{source}<br />\n'
            media_content += f'<div class="media_column {source.lower()}">\n<div class="media_header"><div class="media_summary">{count}</div>{source.capitalize()}</div>\n'

            items.sort(key=lambda x: x[9], reverse=True)
            for item in items:
                item = [self.to_unicode_str(x) if x != None else '' for x in item]
                media_content += f'<div class="media_row"><div class="prof_cell"><a href="{item[4]}" target="_blank"><img class="prof_img rounded" src="{item[5]}" /></a></div><div class="data_cell"><div class="trigger" id="trigger" lat="{item[7]}" lon="{item[8]}">[<a href="{item[3]}" target="_blank">{item[2]}</a>] {self.remove_nl(item[6], "<br />")}<br /><span class="time">{item[9]}</span></div></div></div>\n'
                map_details = (f"<table><tr><td class='prof_cell'><a href='{item[4]}' target='_blank'><img class='prof_img rounded' src='{item[5]}' /></a></td><td class='data_cell'>[<a href='{item[3]}' target='_blank'>{self.remove_nl(item[2])}</a>] {self.remove_nl(item[6], '<br />')}<br /><span class='time'>{item[9]}</span></td></tr></table>")
                map_content += f'add_marker({{position: new google.maps.LatLng({item[7]},{item[8]}),title:"{self.remove_nl(item[2])}",icon:"{icons[source.lower()]}",map:map}},{{details:"{map_details}"}}, "{source.lower()}");\n'
            media_content += '</div>\n'
        return (media_content,), (map_content, map_arrays, map_checkboxes)

    def write_markup(self, template, filename, content):
        temp_content = open(template).read()
        page = temp_content % content
        with codecs.open(filename, 'wb', 'utf-8') as fp:
            fp.write(page)

    def module_run(self):
        key = self.keys.get('google_api')
        sources = self.query('SELECT COUNT(source), source FROM pushpins GROUP BY source')
        commonUniqueUsers = self.findCommonUsers(sources)
        culledSources = self.getSources(commonUniqueUsers)
        media_content, map_content = self.build_content(sources, culledSources)
        meta_content = (self.options['latitude'], self.options['longitude'], self.options['radius'])
        # create the media report
        print("================================================================================")
        print(f"Creating HTML reports") 
        print("================================================================================")
        print("")
        media_content = meta_content + media_content
        media_filename = self.options['media_filename']
        self.write_markup(os.path.join(self.data_path, 'template_media.html'), media_filename, media_content)
        self.output(f"Media data written to '{media_filename}'")
        # order the map_content tuple
        map_content = meta_content + map_content + (key,)
        order = [6, 4, 0, 1, 2, 3, 5]
        map_content = tuple([map_content[i] for i in order])
        # create the map report
        map_filename = self.options['map_filename']
        self.write_markup(os.path.join(self.data_path, 'template_map.html'), map_filename, map_content)
        self.output(f"Mapping data written to '{map_filename}'")
        # open the reports in a browser
        w = webbrowser.get()
        w.open(media_filename)
        time.sleep(2)
        w.open(map_filename)
        print("")
        print("")
