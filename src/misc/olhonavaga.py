import argparse
from pandas import DataFrame
from bs4 import BeautifulSoup


def getData(bs):
    table = bs.find('tbody',id="form:tabView:dataTable_data")
    return { i+1:[ d.text for d in r.findAll('td')[:-1]] for i,r in enumerate(table.findAll('tr')) }

def getHeader(bs):
    header = bs.find('div', attrs={'class': 'ui-datatable-tablewrapper'}).findAll('th', role="columnheader")
    return [ r.text if r is not None else None for r in [ c.find('div', attrs={'class': 'ui-tooltip-text'}) for c in header ]]




if __name__=='__main__':
    parser = argparse.ArgumentParser()    
    parser.add_argument("file", help="An HTML file contaning the ranking table from olhonoavaga")
    args = parser.parse_args()

    html_file = args.file
    print(html_file)
    

    with open(html_file) as html:
        bs = BeautifulSoup(html,'lxml')

    df = DataFrame.from_dict(getData(bs), orient='index', columns=getHeader(bs), dtype=int)   


    print(df.mean())

    
