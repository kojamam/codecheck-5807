#!/usr/bin/env python3

import sys
import datetime
import pandas
import json
import urllib.request
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from collections import OrderedDict

def printResult(corrMatrix):
    res = '{"coefficients": ['
    i = 0
    for vec in corrMatrix:
        j = 0
        res += "["
        for corr in vec:
            if j < len(vec) - 1:
                res += str(corr) + ","
            else:
                res += str(corr) + "]"

            j += 1

        if i < len(corrMatrix) - 1:
            res += ","
        else:
            res += "], "
        i +=1
    res += '"posChecker": true}'

    print(res)



def calcCoeff(data):
    dataFrame = pandas.DataFrame(data)
    corrMatrix = dataFrame.corr().round(3).as_matrix().tolist()

    return corrMatrix

def urlEncode(url):
    p = urlparse(url)
    query = urllib.parse.quote_plus(p.query, safe='=&')
    url = '{}://{}{}{}{}{}{}{}{}'.format(
        p.scheme, p.netloc, p.path,
        ';' if p.params else '', p.params,
        '?' if p.query else '', query,
        '#' if p.fragment else '', p.fragment)

    return url


def reqAPI(keywords, startDatetime, endDatetime):

    numFounds = OrderedDict()

    baseurl = 'http://54.92.123.84/search?ackey=869388c0968ae503614699f99e09d960f9ad3e12&sort=ReleaseDate asc&rows=1'

    for keyword in keywords:
        numFounds[keyword] = []
        query = ''

        tmpStartDatetime = startDatetime
        tmpEndDatetime = startDatetime + datetime.timedelta(days=6)

        while tmpEndDatetime < endDatetime:
            query = 'q=Body:' + keyword + ' AND ' + 'ReleaseDate:[' + tmpStartDatetime.strftime("%Y-%m-%d") + ' TO ' + tmpEndDatetime.strftime("%Y-%m-%d") + ']'

            url = baseurl + '&' + query

            req = urllib.request.Request(urlEncode(url))

            with urllib.request.urlopen(req) as response:
                XmlData = response.read()

            root = ET.fromstring(XmlData)

            numFounds[keyword].append(int(root[2].attrib['numFound']))

            tmpStartDatetime = tmpEndDatetime + datetime.timedelta(days=1)
            tmpEndDatetime = tmpStartDatetime + datetime.timedelta(days=6)

    return numFounds

def main(argv):

    (startDateStr, endDateStr) = (argv[1], argv[2])
    keywords = [str.strip().strip('"') for str in argv[0].split("]")[0][1:].split(",")]

    startDatetime = datetime.datetime.strptime(startDateStr, '%Y-%m-%d')
    endDatetime = datetime.datetime.strptime(endDateStr, '%Y-%m-%d')
    corrMatrix = calcCoeff(reqAPI(keywords, startDatetime, endDatetime))
    printResult(corrMatrix)


    return 0

# main(sys.argv[1:])
