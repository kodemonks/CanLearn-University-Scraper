from scrapy import Spider
from scrapy import Request
import logging
from scrapy.utils.log import configure_logging
from canLearnScraper.items import CollegeInfoItem

import time
start_time = time.time()


#Configuring logs for Main crawler Module.
#Log file name can be changed below
#Log Level can be modified to INFO , ERROR , WARNING , DEBUG etc
#Format specifies file format
configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='log.txt',
    format='%(levelname)s: %(message)s',
    level=logging.ERROR
)


class CanLearnSpider(Spider):
    #Defining Name of Spider | It will be used for running spider
    #Use - scrapy crawl <spider-name>  [scrapeData in our case]
    name='scrapeData'

    # Domains allowed during scrape session | Outer domains will be filtered
    # This section need not to be altered in our case
    # So it can be left unaltered
    allowed_domain=[ 'http://tools.canlearn.ca' ]

    #Start URLS for scraping
    #Change here for different URL
    #We can add multiple url here, seaprated by a comma(,)
    # example ['url1' , 'url2' , 'url3' ]
    start_urls=[
                 "http://tools.canlearn.ca/cslgs-scpse/cln-cln/rep-fit/p/af.p.clres.do?institution_id=default&searchType=ALL&searchString=&progLang=A&instType=B&prov_4=prov_4&progNameOnly=N&start=1&finish=14&section=1"
               ]




    #Default Parse Method will be used for fetching all college URL's
    #Scrapy makes call to start_urls SET and then response is parsed
    #by this block in ASYNC manner
    def parse(self, response):
        #Fetching each info as a block and iterating over it -
        for collegeBlock in response.xpath("//div[contains(@class,'wb-frm')]/form/div/section/ol/li"):
            #Fetching 1st section details and passing it to next async call
            university = collegeBlock.xpath(".//ul/li[1]/text()").extract_first()
            university =" ".join(university.split()).replace(",","\n")
            city = collegeBlock.xpath(".//ul/li[2]/text()").extract_first()
            city = " ".join(city.split()).replace(",","\n")
            type = collegeBlock.xpath(".//strong/a/text()").extract_first()
            #Fetching Next URL for parse Async call
            url = collegeBlock.xpath(".//strong/a/@href").extract_first()

            #Change relative URL to absolute for making call
            absolute_urls=response.urljoin(url)

            #make a new Scrapy Request | handle it using different parser parse_college_data (below).
            yield Request(absolute_urls,callback=self.parse_college_data,meta={'city': city,'university':university,'type':type})
        print('\n\n\n\n\nTIME CONSUMED BY APP - \n\n\n\n\n\n')
        print((time.time() - start_time))



    #Parse method, will be used for parsing University data :
    def parse_college_data(self,response):
            email=''
            #Fetching info from prev. async call
            city = response.meta['city']
            type = response.meta['type']
            university = response.meta['university']

            #Cleaing Response body
            response = response.replace(body=response.body.replace('<br/>','\n'))
            response = response.replace(body=response.body.replace('<br>', '\n'))

            #Fetching website link
            college_website=response.xpath("(//div[contains(@class,'panel-body')])[2]/dl/dd/a/@href").extract_first()


            # Creating Item details (Dict. key and value) to fill complete Set
            general_info_key=response.xpath("(//div[contains(@class,'panel-body')])[4]/dl/dt/text()").extract()
            general_info_value=response.xpath("(//div[contains(@class,'panel-body')])[4]/dl/dd/text()").extract()
            email = response.xpath("(//div[contains(@class,'panel-body')])[4]/dl/dd/a/text()").extract_first()
            if "@" not in str(email):
                email='n/a'

            #Handling exceptional case | Ambigious college link in detected
            if len(general_info_key) != len(general_info_value):
                indices = [i for i, s in enumerate(general_info_key) if 'Website' in s]
                general_info_value.insert(indices[0]-1,'na')

            #Creating Dictionary of general Info items
            general_info_dict = dict(zip(general_info_key, general_info_value))
            print(general_info_dict)


            #Filling all information into items Object Here -
            item=CollegeInfoItem()
            item['University']=university.encode('utf-8')
            item['Type']=type.encode('utf-8')
            item['City'] = city.encode('utf-8')
            item['Website'] = college_website.encode('utf-8')
            item['Address'] = general_info_dict.get('Address:').encode('utf-8')
            item['Credential_Type'] = general_info_dict.get('Credential Type:').encode('utf-8')
            item['Email'] = email
            item['Fax'] = general_info_dict.get('Fax:')
            item['Joint_Credential_Type'] = general_info_dict.get('Joint Credential Type:')
            item['Joint_Program_Level'] = general_info_dict.get('Joint Program Level:')
            item['Program_Level'] = general_info_dict.get('Program Level:').encode('utf-8')
            item['Telephone'] = general_info_dict.get('Telephone:')
            item['Toll_Free'] = general_info_dict.get('Toll Free:')


            print('Successfully Parsed - '+str(university))
            #Saving data to CSV file
            yield item



    #Method to filter text data
    def filterString(stringHere):
       return  " ".join(stringHere.split()).replace(",", "")
