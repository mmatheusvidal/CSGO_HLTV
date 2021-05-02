from selenium.webdriver import Chrome
from time import sleep
import json
import pandas as pd

def macro_info(browser, paginas):
    details = []
    for i in range(len(paginas)):
        browser.get(paginas[i])
        sleep(2)
        pre_match = browser.find_elements_by_class_name('padding')
        date = browser.find_element_by_class_name('date')

        played = browser.find_elements_by_class_name('played')
        played_info = []
        for i in range(len(played)):
            played_info.append(played[i].text)

            #Not Working
        links = browser.find_elements_by_class_name('results-stats')
        list_links = []
        for i in range(len(links)):
            list_links.append(links[i].get_attribute('href'))
            dict_details = {'data' : date.text,
                    'what' : pre_match[0].text,
                    'PicsBans': pre_match[1].text,
                    'Teams_History': pre_match[-1].text,
                    'played_info' : played_info,
                    'list_links' : list_links}
        details.append(dict_details)
    return details

# Transform Result
# dict_details['PicsBans'] = dict_details['PicsBans'].split('\n')
# dict_details['Teams_History'] = dict_details['Teams_History'].split('\n')
# dict_details['Teams_History'] = {dict_details['Teams_History'][0] : dict_details['Teams_History'][1],
#                                  'Overtimes' : dict_details['Teams_History'][3],
#                                  dict_details['Teams_History'][7] : dict_details['Teams_History'][5]}
