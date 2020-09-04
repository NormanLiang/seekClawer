import requests
import asyncio
from enum import Enum
import aiohttp
from lxml import etree
import csv
from modules.seekmodule import XIECHENG_Helper, Job_infor

DOMIN_STR = 'https://www.seek.com.au'

HEADER = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
    'cookie':'JobseekerSessionId=7cb467b82e27c501af541007653181b9; JobseekerVisitorId=7cb467b82e27c501af541007653181b9; RecommendedJobsUiNew=true; s_ecid=MCMID%7C56369498586087465671507818261925689828; _ga=GA1.3.2051820522.1596522722; _scid=570345f3-5b47-419c-854b-00a34eb9683c; _gcl_au=1.1.896364186.1596522722; responsive-trial=chrome:7; _fbp=fb.2.1596522724415.496790069; .ASPXAUTH=F4D0BB3707C489C6C7D3C9EF9263922EE27294216889FB481CA2052655D43A8039F654518901C217C69DBEECEF68713C31B2FD89816A8052F01BB9899F541171AAB50ACF6CC336C1118A7F8146CE3580B72594B60E802E18D985CFE2C0B3EA137AA6553950027D02EC92BE443763610BB6EBA64D7DAEDAA09848BE3EB5E8DED9EF3342000F9E7D8C0FA4AB1FA540A872300E94FE; Login=Jt1kEjo+WHwspVFKVNvT47B5wQT2lUxuLjg9xXuMKDw=; _sj=; sol_id_old_value=blank; sol_id=4c129b0b-4749-4ea6-83cb-bb8d3be569b7; sol_id_generated=4c129b0b-4749-4ea6-83cb-bb8d3be569b7; sol_id_pre_stored=4c129b0b-4749-4ea6-83cb-bb8d3be569b7; __gads=ID=3e5f681586bed127:T=1596522769:S=ALNI_MZzsUlARHevZ7h6hiwXjz28t87VbQ; sol_id_initialized=4c129b0b-4749-4ea6-83cb-bb8d3be569b7; _pin_unauth=dWlkPU1qTXlPR0kyTVRFdE1UVTBZeTAwWXpZMExXSm1NRFl0TUdJd1pHVTVOemN6TVRGayZycD1abUZzYzJV; _sctr=1|1597586400000; _hjid=ee0b8100-5ba7-408d-bc24-2be3de27be4c; ASP.NET_SessionId=cjaxqirqf3gnovbrn1rj4jx5; UpdatedLastLogin=true; _hjAbsoluteSessionInProgress=0; AMCVS_199E4673527852240A490D45%40AdobeOrg=1; s_cc=true; _gid=GA1.3.360223791.1598064426; wfhDismissedNudge=true; AMCV_199E4673527852240A490D45%40AdobeOrg=-1712354808%7CMCIDTS%7C18497%7CMCMID%7C56369498586087465671507818261925689828%7CMCAAMLH-1598679653%7C8%7CMCAAMB-1598679653%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1598082053s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.3.0; s_sq=%5B%5BB%5D%5D; utag_main=v_id:0173b82b6be90017de8f01ee22a503073001806b00978$_sn:6$_se:2$_ss:0$_st:1598082411887$vapi_domain:seek.com.au$ses_id:1598080434777%3Bexp-session$_pn:2%3Bexp-session; main=V%7C2~P%7Cjobsearch~K%7Csoftware%20developer~WID%7C3000~L%7C3000~OSF%7Cquick&set=1598080612115; skl-lcid=fa64aae4-f9dc-44ce-b1e3-54e7ae4a0e98; _gat_tealium_0=1',
    'referer': DOMIN_STR,
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
}


MAX_XIECHENG_NUM = 5

XC_helpers = []

URL_lists = {}

URLS = [
    'https://www.seek.com.au/software-developer-jobs',
    'https://www.seek.com.au/software-engineer-jobs',
]

TARGET_STR = '{n}'
PAGES = '?page='+TARGET_STR

g_job_info = None
g_url_manager = None

class URL_Manager():
    
    def __init__(self):
        self.idx = 0
        self.url_valid = True
        self.url_idx = 0

    def getURLIdx(self):
        return self.url_idx

    def getCurrentIdx(self):
        return self.idx
    
    def resetIdx(self):
        self.idx = 0
        return self.idx

    def updateCurrentIdx(self):
        self.idx += 1
        return self.idx

    def getURLFromIdx(self, idx):
        if idx >= 1:
            url = URLS[self.url_idx] + PAGES.replace(TARGET_STR, str(idx+1))
        else:
            url = URLS[self.url_idx]
        return url    

    def setURLInvalid(self):
        self.url_valid = False
#        self.invalid_count += 1

    def getURLValid(self):
        return self.url_valid    
#        return self.invalid_count

    def nextURLidx(self):
        tmp = self.url_idx + 1
        if tmp >= len(URLS):
            return None
        else:
            self.url_idx = tmp
            return self.url_idx

    def getDefaultDomin(self):
        return DOMIN_STR

def checkStop(id):
    check = 0
    for xc in XC_helpers:
        if xc.getState() == XIECHENG_Helper.STATE_PENDING:
            check += 1
    
    if check == MAX_XIECHENG_NUM:
        if g_url_manager.nextURLidx() == None:
            return True
        else:
            filename = URLS[g_url_manager.getURLIdx()-1].split('/')[-1] + '.csv'
            writeToFile(filename)
            g_url_manager.resetIdx()
            for xc in XC_helpers:
                xc.setState(XIECHENG_Helper.STATE_BUSY)
            return False
    else:
        return False

def getURLFromPool():
    idx = g_url_manager.getCurrentIdx()
    url = g_url_manager.getURLFromIdx(idx)
    g_url_manager.updateCurrentIdx()
    return url


def parse_data(raw, url, id):

    global g_job_info
    try:

        html = etree.HTML(raw)
        node_all = html.xpath('//article')
        if len(node_all) > 0:

            for child in node_all:
                job_id = child.xpath('./@data-job-id')[0]
                job_title = child.xpath('.//a[@data-automation="jobTitle"]/text()')[0]
                job_company = child.xpath('.//a[@data-automation="jobCompany"]/text()')
                if len(job_company) == 0:
                    job_company = g_job_info.getDefaultJobCompany()
                else:
                    job_company = job_company[0]

                job_detail_link = child.xpath('.//a/@href')

                if len(job_detail_link) == 0:
                    job_detail_link = g_job_info.getDefaultJobLink()
                else:
                    job_detail_link = g_url_manager.getDefaultDomin() + job_detail_link[0]


                job_location = child.xpath('.//a[@data-automation="jobLocation"]/text()')[0]
                job_area = child.xpath('.//a[@data-automation="jobArea"]/text()')

                if len(job_area) == 0:
                    job_area = g_job_info.getDefaultJobArea()
                else:
                    job_area = job_area[0]

                g_job_info.updateData((job_id, job_title, job_company, job_location, job_area, job_detail_link))
        else:
#            g_url_manager.setURLInvalid()
            XC_helpers[id].setState(XIECHENG_Helper.STATE_PENDING)


    except Exception as e:
        print('url_invalid at ' + url)

async def request_and_parse(url, id):
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADER) as resp:    
            if resp.status == 200:
                data = await resp.read()
                print('parsing url: ' + url)
                parse_data(data, url, id)


async def crawl_url(id):
    
    while True:

        if XC_helpers[id].getState() != XIECHENG_Helper.STATE_BUSY:
            if checkStop(id) == True:
                break            
            else:
                await asyncio.sleep(1)
        
        url = getURLFromPool()

        if url is not None:
            await request_and_parse(url, id)




def processData():
    
#    g_job_info.renderToLists()
    pass


def writeToFile(filename):

    headers = ['id', 'title', 'company', 'location', 'area', 'link']

    try:

        with open(filename, 'w', newline='') as f:
            csv_f = csv.writer(f)
            csv_f.writerow(headers)
            csv_f.writerows(g_job_info.getLists())

    except Exception as e:
        print(e)

def main():

    global g_job_info, g_url_manager

    tasks = []
    g_job_info = Job_infor()
    g_url_manager = URL_Manager()

    asyncio.set_event_loop(asyncio.new_event_loop())

    for i in range(0, MAX_XIECHENG_NUM):
        xc = XIECHENG_Helper(i)
        gen = crawl_url(xc.getID())
        tasks.append(gen)
        XC_helpers.append(xc)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

#    processData()
    filename = URLS[g_url_manager.getURLIdx()].split('/')[-1] + '.csv'
    writeToFile(filename)



if __name__ == "__main__":
    main()

