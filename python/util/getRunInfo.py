import das_client, rrClient
import json, datetime

def today() :
    return datetime.datetime.now().date()

def daysAgo(n) :
    date = today()
    return date - datetime.timedelta(days=n)

def day(string) :
    return datetime.datetime.strptime(string, "%Y%m%d").date()

def getRunsForDate(date, minlumis=10) :
    '''
        date: expected to be datetime.datetime object
    '''
    datestring = date.strftime('%Y%m%d')
    querystring = "run date={date} | grep run.nlumis>{minlumis}".format(date=datestring, minlumis=minlumis)
    return dasRunQueryToDict(querystring)

def getRunsNewer(run, minlumis=10, source='RunRegistry') :
    '''
        run: run number int
        source: Either RunRegistry or DAS
    '''
    if source == 'RunRegistry' :
        return rrClient.getRunsNewer(run, minlumis)
    elif source == 'DAS' :
        querystring = "run | grep run.nlumis>{minlumis}, run.runnumber>{run}".format(run=run, minlumis=minlumis)
        return dasRunQueryToDict(querystring)

def getFilesForRun(run, dataset) :
    '''
        run : int
        dataset : string dataset to find files in, e.g.
            /ExpressCosmics/Run2015A-Express-v1/FEVT
            /ExpressPhysics/Run2015A-Express-v1/FEVT
    '''
    querystring = "file dataset={dataset} run={run}".format(dataset=dataset, run=run)

    files = []
    for fileDict in dasQuery(querystring, 'file') :
        # cmsRun will not like unicode
        files.append(fileDict['name'].encode('ascii','replace'))

    return files


# -------------------- DAS convert tools

def dasRunQueryToDict(querystring) :
    runs = {}
    for runDict in dasQuery(querystring, 'run') :
        runNo = int(runDict['run_number'])
        runDict['date'] = datestring
        runs[runNo] = runDict
    return runs

def dasQuery(queryString, entryTitle) :
    dasinfo = das_client.get_data('https://cmsweb.cern.ch', queryString, 0, 0, False)
    if dasinfo['status'] != 'ok' :
        raise Exception('DAS query failed.\nQuery: %s\nDAS Status returned: %s' % (queryString, dasinfo['status']))

    for entry in dasinfo['data'] :
        if len(entry[entryTitle]) > 0 :
            yield entry[entryTitle][0]
