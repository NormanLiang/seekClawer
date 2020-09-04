class Job_infor():
    
    def __init__(self):
        self.job_titles = []
        self.job_companies = []
        self.job_locations = []
        self.job_areas = []
        self.maps = []
        self.id = 0
        self.lists = []

    def updateTitles(self, titles):
        self.job_titles.append(titles)

    def updateCompanies(self, companies):
        self.job_companies.append(companies)
    
    def updateLocations(self, locations):
        self.job_locations.append(locations) 

    def updateArea(self, areas):
        self.job_areas.append(areas)

    def resetData(self):
        self.job_titles = []
        self.job_companies = []
        self.job_locations = []
        self.job_areas = []     

    def updateOnce(self):
        if len(self.job_titles) > 0:
            for i in range(0, len(self.job_titles)):
                map_tmp = {}
                map_tmp['id'] = self.id
                map_tmp['title'] = self.job_titles[i]
                map_tmp['company'] = self.job_companies[i]
                map_tmp['location'] = self.job_locations[i]
                map_tmp['area'] = self.job_areas[i]
                self.id += 1
                self.maps.append(map_tmp)
        
        self.resetData()

    def renderToLists(self):
        
        for i in range(0, len(self.job_titles)):
            for j in range(0, len(self.job_titles[i])):     
                map_tmp = (self.id, self.job_titles[i][j], self.job_companies[i][j], self.job_locations[i][j], self.job_areas[i][j])
                self.id += 1
                self.lists.append(map_tmp)                

    def renderToMap(self):
        for i in range(0, len(self.job_titles)):

            for j in range(0, len(self.job_titles[i])):
                map_tmp = {}

                map_tmp['id'] = self.id
                map_tmp['title'] = self.job_titles[i][j]
                map_tmp['company'] = self.job_companies[i][j]
                map_tmp['location'] = self.job_locations[i][j]
                map_tmp['area'] = self.job_areas[i][j]

                self.id += 1
                self.maps.append(map_tmp)

    def getLists(self):
        return self.lists 

    def updateData(self, datamap):
        self.lists.append(datamap)

    def getID(self):
        ret = self.id
        self.id += 1
        return ret

    def getDefaultJobCompany(self):
        return 'Private Advisor'

    def getDefaultJobArea(self):
        return " "

    def getDefaultJobLink(self):
        return ' '



class XIECHENG_Helper():

    STATE_IDLE = 0
    STATE_BUSY = 1
    STATE_PENDING = 2

    def __init__(self, id):
        self.id = id
        self.state = self.STATE_BUSY
        self.url = ''

    def isWorking(self):
        return True if self.state == self.STATE_BUSY else False
    
    def setState(self, st):
        self.state = st
    
    def getState(self):
        return self.state

    def setURL(self, url):
        self.url = url

    def getID(self):
        return self.id

SKILL_POLL = [
    'C', 'C/C++', 'Vue', 'Angular', 'React', 'Linux', 'HTML', 'GIT', 'CSS', 'PHP', 'Java', 'JavaScript', 'SQL', 'Ruby',
    'AWS', 'AZure', 'SQL', 'CSS', 'SSH', '.Net', 'C#', 'REST', 'Python', 'Go', 'Golong', 'ASX', 'Docker', 'Typescript', 'Redus',
    'NodeJS', 'MicroServices', 'spring', 'firmware', 'Embedded', 'C++', 'Django', 'R', 'ReactJS', 'CI/CD', 'Swift', 'Kotlin', 'RESTful',
    'LOT',
]



