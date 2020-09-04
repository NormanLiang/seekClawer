import sys
import csv
import re

from enum import Enum
from modules.seekmodule import SKILL_POLL

import matplotlib.pyplot as plt
import seaborn as sns



g_Job_Info = None

class JOBIndex(Enum):
    JOB_ID = 0
    JOB_TITLE = 1
    JOB_COMPANY = 2
    JOB_LOCATION = 3
    JOB_AREA = 4
    JOB_SKILLSET = 5
    JOB_DETAILLINK = 6


class JobInfor():
    
    def __init__(self):
        self.__lists = []
        self.__locations = {}
        self.__skills = {}

        self.locationmap = {}

    def updateToList(self, theset):
        self.__lists.append(theset)

    @property
    def locations(self):
        return self.__locations
    
    @locations.setter
    def locations(self, location):
        if location in self.__locations.keys():
            self.__locations[location] += 1
        else:
            self.__locations[location] = 1

    @property
    def skills(self):
        return self.__skills

    @skills.setter
    def skills(self, skill):

        if skill == '':
            return
        
        skill = skill.upper()

        if skill in self.__skills.keys():
            self.__skills[skill] += 1
        else:
            self.__skills[skill] = 1

    @property
    def lists(self):
        return self.__lists

    @lists.setter
    def lists(self, lst):
        self.__lists.append(lst)

    @lists.deleter
    def lists(self):
        self.__lists = [] 

    def updateMap(self, location, skills):
        
        if location in self.locationmap.keys():
            dicttmp = self.locationmap[location]
            for skill in skills:
                if skill != '':
                    skill = skill.upper()
                    if skill in dicttmp.keys():
                        dicttmp[skill] += 1
                    else:
                        dicttmp[skill] = 1
            self.locationmap[location] = dicttmp
        else:
            dicttmp = {}
            for skill in skills:
                if skill != '':
                    skill = skill.upper()
                    dicttmp[skill] = 1
            if len(dicttmp) > 0:
                self.locationmap[location] = dicttmp


def readFromFile(filename):
    
    global g_Job_Info

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            g_Job_Info.lists = (row['id'], row['title'], row['company'], row['location'], row['area'], row['skillset'], row['link'])


def processData():

    for info in g_Job_Info.lists:

        skill = info[5]
        location = info[3]

        g_Job_Info.locations = location

        skills = skill.split(' ')

        for skill in skills:
            g_Job_Info.skills = skill

        g_Job_Info.updateMap(location, skills)

def showlocation(*args):

    labels = []
    nums = []

    for loc in g_Job_Info.locations.keys():
        n = g_Job_Info.locations[loc]
        if n >= 10:
            labels.append(loc)
            nums.append(n)

    plt.xlabel('location',fontsize=14)

    plt.bar(labels, nums, width=0.35)
    plt.xticks(labels, labels, rotation=20, fontsize=8)

    for a, b in zip(labels, nums):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=8)   

    plt.xlim(-0.5, len(nums))
    plt.show()
    

def showSkills(*args):

    labels = []
    nums = []

    for skill in g_Job_Info.skills.keys():
        n = g_Job_Info.skills[skill]
        labels.append(skill)
        nums.append(n)

    plt.xlabel('skills',fontsize=14)

    plt.bar(labels, nums, width=0.35)
    plt.xticks(labels, labels, rotation=40, fontsize=8)

    for a, b in zip(labels, nums):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=8)   

    plt.xlim(-0.5, len(nums))
    plt.show()


def showDetailedLocation(location):

    labels = []
    nums = []

    for key in g_Job_Info.locationmap.keys():
        locations = re.split(',| ', key)
        if location in locations:
            skillsets = g_Job_Info.locationmap[location]

            for skill in skillsets.keys():
                n = skillsets[skill]
                labels.append(skill)
                nums.append(n)

            plt.xlabel('skills in '+location, fontsize=14)

            plt.bar(labels, nums, width=0.35)
            plt.xticks(labels, labels, rotation=40, fontsize=8)

            for a, b in zip(labels, nums):
                plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=8)   

            plt.xlim(-0.5, len(nums))
            plt.show()
            break


def showdata(args):

    methods = {
        'location': showlocation,
        'skills' : showSkills,
    }

    if args != None:
        if args in methods.keys():
            method = methods[args]
        else:
            method = showDetailedLocation
    else:
        method = showDetailedLocation

    method(args)

def main(*args):

    global g_Job_Info

    g_Job_Info = JobInfor()
    readFromFile(args[0])

    processData()

    if len(args) > 1:
        showdata(args[1])
    else:
        showdata(None)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])

