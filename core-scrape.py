from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import json

#character = "AAA"
#entity_name.send_keys("'")
def search(character, link):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://core.cro.ie/search")
    time.sleep(0.6)

    driver.find_element(By.XPATH, '//*[@id="content"]/cro-search/div/div/div/div/aside/cro-company-search-form/form/section[1]/div/div[1]/div/div[2]/label').click()
    entity_name = driver.find_element(By.ID, 'registeredName')
    entity_name.send_keys(character)
    time.sleep(0.6)

    driver.find_element(By.XPATH, '//*[@id="content"]/cro-search/div/div/div/div/aside/cro-company-search-form/form/section[2]/regsys-reactive-button[2]/button/span[1]').click()
    time.sleep(0.6)
    
    driver.find_element(By.XPATH, '//*[@id="content"]/cro-search/div/div/div/div[2]/cro-company-search-result/section/div[2]/mat-paginator/div/div/div[1]/mat-form-field').click()
    #time.sleep(1)
    
    driver.find_element(By.ID, 'mat-option-2').click()
    soup = BeautifulSoup(driver.page_source)

    df_number = pd.DataFrame([tag.text.split(" ")[2] \
                            for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-registeredNumber mat-column-registeredNumber ng-star-inserted"})], columns=['Number'])

    df_name = pd.DataFrame([tag.text.replace("Name", '') for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-registeredName mat-column-registeredName ng-star-inserted"})], columns=['Name'])

    df_type = pd.DataFrame([tag.text.replace("Type", '') for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-entityTypeDesc mat-column-entityTypeDesc ng-star-inserted"})], columns=['Type'])

    df_status = pd.DataFrame([tag.text.replace("Status", '') for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-entityStatusDesc mat-column-entityStatusDesc ng-star-inserted"})], columns=['Status'])

    df_register = pd.DataFrame([tag.text.replace("Registered On ", '') for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-entityRegisteredDate mat-column-entityRegisteredDate ng-star-inserted"})], columns=['Registered On'])

    while True:
        try :
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,  '//*[@id="content"]/cro-search/div/div/div/div[2]/cro-company-search-result/section/div[2]/mat-paginator/div/div/div[2]/button[2]' ))).click()
            #time.sleep(0.5)
            soup = BeautifulSoup(driver.page_source)
            soup.find_all("div", {"class": "mat-table-container ng-star-inserted"})
            soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-registeredNumber mat-column-registeredNumber ng-star-inserted"})
            
            # extract number
            df_numbernext = pd.DataFrame([tag.text.split(" ")[2] \
                                                for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-registeredNumber mat-column-registeredNumber ng-star-inserted"})], columns=['Number'])
            df_number = pd.concat([df_number, df_numbernext], ignore_index=True)
            
            # extract name
            df_namenext = pd.DataFrame([tag.text.replace("Name", '') for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-registeredName mat-column-registeredName ng-star-inserted"})], columns=['Name'])
            df_name = pd.concat([df_name, df_namenext], ignore_index=True)
            
            # extract type
            df_typenext = pd.DataFrame([tag.text.replace("Type", '') for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-entityTypeDesc mat-column-entityTypeDesc ng-star-inserted"})], columns=['Type'])
            df_type = pd.concat([df_type, df_typenext], ignore_index=True)
            
            # extract status
            df_statusnext = pd.DataFrame([tag.text.replace("Status", '') for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-entityStatusDesc mat-column-entityStatusDesc ng-star-inserted"})], columns=['Status'])
            df_status = pd.concat([df_status, df_statusnext], ignore_index=True)
            
            # extract register
            df_registernext = pd.DataFrame([tag.text.replace("Registered On ", '') for tag in soup.find_all("mat-cell", {"class": "mat-cell cdk-cell d-block d-lg-inline-block flex-lg-row mx-2 mb-2 m-lg-0 cdk-column-entityRegisteredDate mat-column-entityRegisteredDate ng-star-inserted"})], columns=['Registered On'])
            df_register = pd.concat([df_register, df_registernext], ignore_index=True)
        except:
            print("No more pages left")
            driver.quit()
            break

    df_tot = pd.concat([df_number, df_name, df_type, df_status, df_register], axis=1)

    # extract entity ID
    #f = open(r'C:\Users\hient\OneDrive - National University of Ireland, Galway\Documents\Sonra\web_scrape\New_Request-1661970261980.json')
    f = open(link, encoding="utf8")
    data = json.load(f)
    f.close()
    df_ID = pd.DataFrame.from_dict(pd.json_normalize(data['data']), orient='columns')
    df_ID2 = df_ID[['entityId', 'registeredNumber']]

    # rename column "registeredNumber" to "number"
    df_ID2.rename(columns = {'registeredNumber':'Number'}, inplace = True)
    df_result = pd.merge(df_tot, df_ID2, on="Number")
    return df_result.to_csv('./out_result_%s.csv' % character)

# extract with '
if __name__ == '__main__':
    start_time = time.time()
    search("AA", r"C:\Users\hient\OneDrive - National University of Ireland, Galway\Documents\Sonra\web_scrape\New_Request-AA-1662489983662.json")
    #search("AAA", r"C:\Users\hient\OneDrive - National University of Ireland, Galway\Documents\Sonra\web_scrape\New_Request-1661970261980.json")
    #search("'", r"C:\Users\hient\OneDrive - National University of Ireland, Galway\Documents\Sonra\web_scrape\New_Request-symbol_entity_number.json")
    #search("0", r"C:\Users\hient\OneDrive - National University of Ireland, Galway\Documents\Sonra\web_scrape\New_Request-0_entity_number.json")
    print("--- %s seconds ---" % (time.time() - start_time))
    print ("Done")