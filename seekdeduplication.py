import csv


duplicatedList = [
    'software-engineer-jobs.csv',
    'software-developer-jobs.csv',
    
]

g_Job_Info = None
g_index = 0

RES_FILE_NAME = 'software_jobs.csv'

class Job_Info():
    
    def __init__(self):
        self.lists = {}
        self.res = []

    def updateToList(self, item):
        if item[0] not in self.lists.keys():
#            print(item[0])
            self.lists[item[0]] = item
        else:
#            print(item[0])
            pass

    def getList(self):
        return self.lists.values()

    def renderData(self):
        for job in self.lists.values():
            pass

        

def processData(filename):
    
    global g_Job_Info, g_index

    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
#            g_index += 1
            g_Job_Info.updateToList((row['id'], row['title'], row['company'], row['location'], row['area'], row['link']))


def writeToFile(filename):
    
    global g_Job_Info

    headers = ['id', 'title', 'company', 'location', 'area', 'link']

    try:

        with open(filename, 'w', newline='') as f:
            csv_f = csv.writer(f)
            csv_f.writerow(headers)
            csv_f.writerows(g_Job_Info.getList())

    except Exception as e:
        print(e)

def main():

    global g_Job_Info, g_index

    g_Job_Info = Job_Info()

    for fname in duplicatedList:
        processData(fname)

#    g_Job_Info.renderData()
    writeToFile(RES_FILE_NAME)


if __name__ == '__main__':
    main()
    

