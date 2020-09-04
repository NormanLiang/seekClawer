import sys
import csv
import asyncio
import aiohttp
from enum import Enum
from lxml import etree
import re

from modules.seekmodule import XIECHENG_Helper, SKILL_POLL

FILENAME_STR = 'software-engineer-jobs.csv'

XC_Helper = []

XC_Defualt_Num = 5

DOMIN_STR = 'https://www.seek.com.au'

HEADER = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
    'cookie':'JobseekerSessionId=7cb467b82e27c501af541007653181b9; JobseekerVisitorId=7cb467b82e27c501af541007653181b9; RecommendedJobsUiNew=true; s_ecid=MCMID%7C56369498586087465671507818261925689828; _ga=GA1.3.2051820522.1596522722; _scid=570345f3-5b47-419c-854b-00a34eb9683c; _gcl_au=1.1.896364186.1596522722; responsive-trial=chrome:7; _fbp=fb.2.1596522724415.496790069; .ASPXAUTH=F4D0BB3707C489C6C7D3C9EF9263922EE27294216889FB481CA2052655D43A8039F654518901C217C69DBEECEF68713C31B2FD89816A8052F01BB9899F541171AAB50ACF6CC336C1118A7F8146CE3580B72594B60E802E18D985CFE2C0B3EA137AA6553950027D02EC92BE443763610BB6EBA64D7DAEDAA09848BE3EB5E8DED9EF3342000F9E7D8C0FA4AB1FA540A872300E94FE; Login=Jt1kEjo+WHwspVFKVNvT47B5wQT2lUxuLjg9xXuMKDw=; _sj=; sol_id_old_value=blank; sol_id=4c129b0b-4749-4ea6-83cb-bb8d3be569b7; sol_id_generated=4c129b0b-4749-4ea6-83cb-bb8d3be569b7; sol_id_pre_stored=4c129b0b-4749-4ea6-83cb-bb8d3be569b7; __gads=ID=3e5f681586bed127:T=1596522769:S=ALNI_MZzsUlARHevZ7h6hiwXjz28t87VbQ; sol_id_initialized=4c129b0b-4749-4ea6-83cb-bb8d3be569b7; _pin_unauth=dWlkPU1qTXlPR0kyTVRFdE1UVTBZeTAwWXpZMExXSm1NRFl0TUdJd1pHVTVOemN6TVRGayZycD1abUZzYzJV; _sctr=1|1597586400000; _hjid=ee0b8100-5ba7-408d-bc24-2be3de27be4c; ASP.NET_SessionId=cjaxqirqf3gnovbrn1rj4jx5; UpdatedLastLogin=true; _hjAbsoluteSessionInProgress=0; AMCVS_199E4673527852240A490D45%40AdobeOrg=1; s_cc=true; _gid=GA1.3.360223791.1598064426; wfhDismissedNudge=true; AMCV_199E4673527852240A490D45%40AdobeOrg=-1712354808%7CMCIDTS%7C18497%7CMCMID%7C56369498586087465671507818261925689828%7CMCAAMLH-1598679653%7C8%7CMCAAMB-1598679653%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1598082053s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.3.0; s_sq=%5B%5BB%5D%5D; utag_main=v_id:0173b82b6be90017de8f01ee22a503073001806b00978$_sn:6$_se:2$_ss:0$_st:1598082411887$vapi_domain:seek.com.au$ses_id:1598080434777%3Bexp-session$_pn:2%3Bexp-session; main=V%7C2~P%7Cjobsearch~K%7Csoftware%20developer~WID%7C3000~L%7C3000~OSF%7Cquick&set=1598080612115; skl-lcid=fa64aae4-f9dc-44ce-b1e3-54e7ae4a0e98; _gat_tealium_0=1',
    'referer': DOMIN_STR,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
}

g_URL_Manager = None
g_skillpool = []
g_currentIdx = 0

g_dictres = []

class Job_Info(Enum):

    JOB_ID = 0
    JOB_TITLE = 1
    JOB_COMPANY = 2
    JOB_LOCATION = 3
    JOB_ARE = 4
    JOB_LINK = 5

class URL_Manager():
    
    def __init__(self):
        self.url_list = []
        self.skillsets = {}
        self.urlListPool = None

    def updateToList(self, item):
        self.url_list.append(item)

    def constructPool(self):
        self.urlListPool = self.url_list.copy()

    def getURLCount(self):
        return len(self.url_list)

    def getURLList(self, idx):
        return self.url_list

    def getURLFromPool(self):
        if len(self.urlListPool) > 0:
            url = self.urlListPool[0]
            self.urlListPool.pop(0)
            
            return url
        else:
            return None


    def updateSkillsets(self, jobid, skillset):
        self.skillsets[jobid] = skillset

    def getSkillsetMap(self):
        return self.skillsets
  
    def getURLFromIdx(self, idx):
        return self.url_list[idx]

def readFromFile(filename):
    
    global g_URL_Manager

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            g_URL_Manager.updateToList((row['id'], row['title'], row['company'], row['location'], row['area'], row['link']))

def getSkillSet(discription):
    
    ret = set()
    tars = re.split(',| |-|\(|\)', discription)
    
    for tar in tars:
        if tar.upper() in g_skillpool:
            ret.add(tar)

    return ret
    
def parse_data(raw, url, id):
    
    try:
        html = etree.HTML(raw)
        nodes = html.xpath('//li/text()')
        nodes_back = html.xpath('//li/p/text()')
        skillset = set()

        if url[0] == '50466885':
            skillset = set() 

        if len(nodes_back) > 0:
            for node in nodes_back:
                ret = getSkillSet(node)
                if len(ret) > 0:
                    skillset = skillset | ret
        
        for node in nodes:
            ret = getSkillSet(node)
            if len(ret) > 0:
                skillset = skillset | ret

            

    except Exception as e:
        print(e)

#    XC_Helper[id].setState(XIECHENG_Helper.STATE_PENDING)
    print(skillset)
    return skillset 
    

def getURLFromPool():

    global g_URL_Manager

    url = g_URL_Manager.getURLFromPool()

    return url

async def request_and_parse(url, id):

    global g_currentIdx

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url[-1], headers=HEADER, timeout=200) as resp:    
                if resp.status == 200:
                    data = await resp.read()
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    print('parsing url: ' + url[0] + ' ' + str(id) + ' ' + ' ' + url[-1])
                    skillset = parse_data(data, url, id)
                    if len(skillset) > 0:
                        g_URL_Manager.updateSkillsets(url[0], skillset)
                    else:
                        g_URL_Manager.updateSkillsets(url[0], "")
                    print('----------------------------------------------')
                    g_currentIdx += 1 
                else:
                    print('job no longer at ' + url[0])   
                    g_URL_Manager.updateSkillsets(url[0], "")    
    except Exception as e:
        print(e)
    
def checkStop(id):
    check = 0
    for xc in XC_Helper:
        if xc.getState() == XIECHENG_Helper.STATE_PENDING:
            check += 1
    
    if check == XC_Defualt_Num:
        return True
    else:
        return False

async def crawl_url(id):

    while True:
        if XC_Helper[id].getState() != XIECHENG_Helper.STATE_BUSY:
            if checkStop(id) == True:
                break            
            else:
                await asyncio.sleep(1)            
        
        url = getURLFromPool()

        if url is not None:
#            print('url is out of pool ' + url[0] + ' ' + str(id))
            await request_and_parse(url, id) 
        else:
            XC_Helper[id].setState(XIECHENG_Helper.STATE_PENDING)


def writeToFiles():

    headers = ['id', 'title', 'company', 'location', 'area', 'skillset', 'link']

    with open('result.csv', 'w', newline='') as f:
        csv_f = csv.writer(f)
        csv_f.writerow(headers)
        csv_f.writerows(g_dictres)        


def processData():
    
    skillsets = g_URL_Manager.getSkillsetMap()

    for i in range(0, g_URL_Manager.getURLCount()):
        url_list = g_URL_Manager.getURLFromIdx(i)
        skill = skillsets[url_list[0]] 
        dictres = [x for x in url_list]
        dictres.append(' '.join(skill))
        dictres[-1], dictres[-2] = dictres[-2], dictres[-1]
        g_dictres.append(dictres)

def main(arg1):

    global g_URL_Manager, g_skillpool

    tasks = []
    g_URL_Manager = URL_Manager()

    for skill in SKILL_POLL:
        g_skillpool.append(skill.upper())

    readFromFile(arg1)

    g_URL_Manager.constructPool()
    
    for i in range(0, XC_Defualt_Num):
        xc = XIECHENG_Helper(i)
        gen = crawl_url(xc.getID())
        tasks.append(gen)
        XC_Helper.append(xc)        

    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))   

    processData()
    writeToFiles() 


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(sys.argv[1])

