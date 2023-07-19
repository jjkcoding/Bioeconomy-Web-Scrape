# Import Necessary Libraries From Selenium, Pandas, and Time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
import requests
import pandas as pd
import time

# Creating the paths for all input and export files
fold_path = "C:/Users/joshu/Desktop/web scraping/bioeconomy ventures/"
ex_path = fold_path + "start_up.csv"
ex_path2 = fold_path + "investors.csv"
logo_path = fold_path + "logos/"
attach_path = fold_path + "attachments/"
startup_site = "https://platform.bioeconomyventures.eu/start-ups/"
invest_site = "https://platform.bioeconomyventures.eu/investors/"

# Initialize Driver Options
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("start-maximized")
# options.add_argument('--single-process')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--incognito')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument("--headless=new")

options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("detach", True)
options.add_experimental_option('excludeSwitches', ['enable-logging'])

options.add_experimental_option(
    "prefs", {"profile.default_content_setting_values.notifications": 2}
)


# Fix strings that contain <br>
def fix_string(text):
    if text == None:
        return None
    clean_text = text.replace("<br>", "").strip()
    return clean_text

# Check if an element was returned
def check_element(cur_element, attr):
    if len(cur_element) == 0:
        return None
    return cur_element[0].get_attribute(attr)

# Gather all the data for the startup company
def get_startup(temp_df, url):
    driver = webdriver.Chrome(service = Service(ChromeDriverManager().install()),
                          options = options)
    stealth(driver,
            languages = ["en-US", "en"],
            vendor = "Google Inc.",
            platform = "Win32",
            webgl_vendor = "Intel Inc.",
            renderer = "Intel Iris OpenGL Engine")

    driver.get(url)
    time.sleep(2)

    no_thanks = driver.find_elements("xpath", "//a[text()[contains(., 'No thanks')]]")
    if len(no_thanks) > 0:
        no_thanks[0].click()
        time.sleep(1)

    cwa = driver.find_elements("xpath", "//button[text()[contains(., 'Continue without accepting')]]")
    if len(cwa) > 0:
        cwa[0].click()
        time.sleep(1)
    
    
    fb_link = None
    twitter_link = None
    linkedin_link = None

    cur_fb = driver.find_elements("xpath", "//div[contains(@class, 'candidate-social')]//a[contains(@class, 'facebook')]")
    if len(cur_fb) > 0:
        fb_link = cur_fb[0].get_attribute("href")
    cur_twitter = driver.find_elements("xpath", "//div[contains(@class, 'candidate-social')]//a[contains(@class, 'twitter')]")
    if len(cur_twitter) > 0:
        twitter_link = cur_twitter[0].get_attribute("href")
    cur_linkedin = driver.find_elements("xpath", "//div[contains(@class, 'candidate-social')]//a[contains(@class, 'linkedin')]")
    if len(cur_linkedin) > 0:
        linkedin_link = cur_linkedin[0].get_attribute("href")

    abt_q = driver.find_element("xpath", "//div[contains(@class, 'candidate-description')]//p").get_attribute("innerHTML")
    winner_q = driver.find_elements("xpath", "//div[contains(@class, 'candidate-description')]//div[contains(@id, 'custom-why')]//p")
    winner_q = check_element(winner_q, "innerHTML")
    bus_q = driver.find_elements("xpath", "//div[contains(@class, 'candidate-description')]//div[contains(@id, 'yourrevenue')]//p")
    bus_q = check_element(bus_q, "innerHTML")
    patent_q = driver.find_elements("xpath", "//div[contains(@class, 'candidate-description')]//div[contains(@id, 'youhavepatent')]//p")
    patent_q = check_element(patent_q, "innerHTML")
    tech_q = driver.find_elements("xpath", "//div[contains(@class, 'candidate-description')]//div[contains(@id, 'hasyourtecnhology')]//p")
    tech_q = check_element(tech_q, "innerHTML")
    market_q = driver.find_elements("xpath", "//div[contains(@class, 'candidate-description')]//div[contains(@id, 'whatmarket')]//p")
    market_q = check_element(market_q, "innerHTML")


    date_estab = driver.find_elements("xpath", "//div[.//h5[text()[contains(., 'Candidate Overview')]]]//aside[contains(@class, 'candidate-overview')]//span[contains(@id, 'datadicostituzione')]")
    date_estab = check_element(date_estab, "innerHTML")
    mrl_info = driver.find_elements("xpath", "//div[.//h5[text()[contains(., 'Candidate Overview')]]]//aside[contains(@class, 'candidate-overview')]//span[contains(@id, 'mrl')]")
    mrl_info = check_element(mrl_info, "innerHTML")
    req_inv = driver.find_elements("xpath", "//div[.//h5[text()[contains(., 'Candidate Overview')]]]//aside[contains(@class, 'candidate-overview')]//span[contains(@id, 'requested_investment')]")
    req_inv = check_element(req_inv, "innerHTML")
    avail_lang = driver.find_elements("xpath", "//div[.//h5[text()[contains(., 'Candidate Overview')]]]//aside[contains(@class, 'candidate-overview')]//div[.//h6[contains(., 'Languages')]]/span")
    avail_lang = check_element(avail_lang, "innerHTML")

        
        
    cur_attach = driver.find_elements("xpath", "//span[contains(@id, 'custom-attachments')]//a")
    attach_jpg = None
    if len(cur_attach) > 0:
        attach_jpg = str(temp_df['#'][0]) + "_P"
        response = requests.get(cur_attach[0].get_attribute("href"))
        with open(attach_path + attach_jpg + ".jpg", "wb") as file:
            file.write(response.content)
    

    trl_info = driver.find_element("xpath", "//aside[./h5[text()[contains(., 'TRL')]]]").get_attribute("innerText").replace("TRL:", "").strip()
    location_info = driver.find_element("xpath", "//aside[./h5[text()[contains(., 'LOCATION')]]]").get_attribute("innerText")
    category_info = driver.find_elements("xpath", "//div[contains(@id, 'resume_category')][count(.//*)=1]//a")

    cat_str = ""
    for i in range(len(category_info)):
        cat_str += category_info[i].get_attribute("innerText")
        if i + 1 != len(category_info):
            cat_str += ", "

    link_name = driver.find_elements("xpath", "//div[contains(@id, 'candidate-qualification')]//strong[contains(@class, 'location')]")
    link_pos = driver.find_elements("xpath", "//div[contains(@id, 'candidate-qualification')]//span[contains(@class, 'qualification')]")
    link_site = driver.find_elements("xpath", "//div[contains(@id, 'candidate-qualification')]//span[contains(@class, 'candidate-social')]//a[contains(@class, 'candidate-linkedin')]")

    cur_yt = driver.find_elements("xpath", "//div[contains(@class, 'candidate-video')]//iframe")
    yt_site = None
    if len(cur_yt) > 0:
        yt_site = cur_yt[0].get_attribute("src")


    temp_df['Facebook'] = [fb_link]
    temp_df['Twitter'] = [twitter_link]
    temp_df['Linkedin'] = [linkedin_link]
    temp_df['About my Start-up'] = [fix_string(abt_q)]
    temp_df['Why your idea is a “winner"?:'] = [fix_string(winner_q)]
    temp_df['What is your current or intended business/revenue model?:'] = [fix_string(bus_q)]
    temp_df['Do you have any Patent or IP registered (related to the solution that you are looking for an investment)?:'] = [fix_string(patent_q)]
    temp_df['Has your technology already been implemented in any field/sector?:'] = [fix_string(tech_q)]
    temp_df['Which market and customer need(s)/problem(s) is (are) your products(s)/service(s) going to solve?:'] = [fix_string(market_q)]
    temp_df['Company'] = temp_df['Name']
    temp_df['Date of establishment/to be established'] = [date_estab]
    temp_df['MRL'] = [fix_string(mrl_info)]
    temp_df['Requested Investment range (€)'] = [req_inv]
    if avail_lang != None:
        temp_df['Languages'] = [fix_string(avail_lang).strip()]
    else:
        temp_df['Languages'] = None
    temp_df['Attachments (Please save them as pdf file with "#dataset_P")'] = attach_jpg
    temp_df['TRL'] = [fix_string(trl_info)]
    temp_df['Location:'] = [fix_string(location_info).replace("Location:", "").strip()]
    temp_df['Category'] = [fix_string(cat_str)]


    for team_i in range(0, 3):
        if team_i + 1 <= len(link_pos):
            cur_name = link_name[team_i].get_attribute("innerHTML").replace("Dr", "").replace(".", "").strip().split(" ")
            temp_df['TM{} - First name'.format(team_i+1)] = [cur_name[0]]
            temp_df['TM{} - Last name'.format(team_i+1)] = [cur_name[-1]]
            temp_df['TM{} - Position'.format(team_i+1)] = [link_pos[team_i].get_attribute("innerHTML")]
            temp_df['TM{} - Linkedin'.format(team_i+1)] = [link_site[team_i].get_attribute("href")]
        else:
            temp_df['TM{} - First name'.format(team_i+1)] = [None]
            temp_df['TM{} - Last name'.format(team_i+1)] = [None]
            temp_df['TM{} - Position'.format(team_i+1)] = [None]
            temp_df['TM{} - Linkedin'.format(team_i+1)] = [None]

    temp_df['Youtube video URL'] = [yt_site]

    temp_df = temp_df.reset_index(drop = True)
    driver.close()
    return temp_df
    


# Gather all the data for the investors 
def get_investor(team_df, url):
    driver3 = webdriver.Chrome(service = Service(ChromeDriverManager().install()),
                            options = options)

    stealth(driver3,
            languages = ["en-US", "en"],
            vendor = "Google Inc.",
            platform = "Win32",
            webgl_vendor = "Intel Inc.",
            renderer = "Intel Iris OpenGL Engine")
    driver3.get(url)
    time.sleep(2)

    fb_link = None
    twitter_link = None
    linkedin_link = None

    cur_fb = driver3.find_elements("xpath", "//div[contains(@class, 'company-social')]//a[contains(@class, 'facebook')]")
    if len(cur_fb) > 0:
        fb_link = cur_fb[0].get_attribute("href")
    cur_twitter = driver3.find_elements("xpath", "//div[contains(@class, 'company-social')]//a[contains(@class, 'twitter')]")
    if len(cur_twitter) > 0:
        twitter_link = cur_twitter[0].get_attribute("href")
    cur_linkedin = driver3.find_elements("xpath", "//div[contains(@class, 'company-social')]//a[contains(@class, 'linkedin')]")
    if len(cur_linkedin) > 0:
        linkedin_link = cur_linkedin[0].get_attribute("href")

    my_fund_q = driver3.find_element("xpath", "//div[contains(@class, 'company-content-wrapper')][./h6[text()[contains(., 'What is my fund looking for?:')]]]//p[string-length(.) > 0]").get_attribute("innerText")
    short_desc_q = driver3.find_element("xpath", "//div[contains(@id, 'company-description')]//p").get_attribute("innerText")
    cur_loc = driver3.find_elements("xpath", "//div[./h6[text()[contains(., 'Location')]]]//a")
    comp_loc = None
    if len(cur_loc) > 0:
        comp_loc = cur_loc[0].get_attribute("innerText")

    cur_yt = driver3.find_elements("xpath", "//div[contains(@class, 'company-video')]//iframe")
    yt_link = None
    if len(cur_yt) > 0:
        yt_link = cur_yt[0].get_attribute("src")

    team_df['Facebook'] = fb_link
    team_df['Twitter'] = twitter_link
    team_df['Linkedin'] = linkedin_link
    team_df['WHAT IS MY FUND LOOKING FOR?:'] = my_fund_q
    team_df['SHORT DESCRIPTION ABOUT MY FUND:'] = short_desc_q
    team_df['LOCATION'] = comp_loc
    team_df['Youtube'] = yt_link
    
    driver3.close()
    return team_df



# RUNS A LOOP TO GATHER ALL THE STARTUP DATA
driver1 = webdriver.Chrome(service = Service(ChromeDriverManager().install()),
                          options = options)

stealth(driver1,
        languages = ["en-US", "en"],
        vendor = "Google Inc.",
        platform = "Win32",
        webgl_vendor = "Intel Inc.",
        renderer = "Intel Iris OpenGL Engine")

driver1.get(startup_site)
time.sleep(2)

no_thanks = driver1.find_element("xpath", "//a[text()[contains(., 'No thanks')]]")
no_thanks.click()
time.sleep(1)

cwa = driver1.find_element("xpath", "//button[text()[contains(., 'Continue without accepting')]]")
cwa.click()
time.sleep(1)


load_clicks = 14
for i in range(load_clicks):
    find_next = driver1.find_elements("xpath", "//a[contains(@class, 'load_more_resumes')]//strong[text()[contains(., 'See all Start-ups')]]")
    if len(find_next) > 0:
        find_next[0].click()
        time.sleep(6)
    else:
        keep_cont = False


site_url = driver1.find_elements("xpath", "//ul[contains(@class, 'resume_list')]//a[contains(@class, 'resume-link')]")
comp_name = driver1.find_elements("xpath", "//div[contains(@class, 'candidate-content-main')]//div[contains(@class, 'candidate-title')]//h5")
imgs = driver1.find_elements("xpath", "//div[contains(@class, 'candidate-photo-wrapper')]//img[contains(@class, 'candidate_photo')]")
print(len(site_url))
for cur_num in range(146, len(site_url)):
    print("Current Web: " + site_url[cur_num].get_attribute("href"))
    temp_df = pd.DataFrame()
    temp_df['#'] = [cur_num+1]
    temp_df['Bioeconomy Ventures URL'] = [site_url[cur_num].get_attribute("href")]

    temp_df['Name'] = [comp_name[cur_num].get_attribute("innerText")]
    temp_df['Website URL'] = [None]

    with open(logo_path + "{}_L.png".format(cur_num + 1), "wb") as file:
        file.write(imgs[cur_num].screenshot_as_png)

    temp_df['Logo (Please save them as png file with "#dataset_L")'] = ['{}_L'.format(cur_num+1)]

    temp_df = get_startup(temp_df, site_url[cur_num].get_attribute("href"))
    # startup_df = pd.concat([startup_df, temp_df]).reset_index(drop = True)
    if cur_num == 0:
        temp_df.to_csv(ex_path, index = False, encoding='utf-8-sig')
    else:
        temp_df.to_csv(ex_path, index = False, mode = 'a', header = False, encoding='utf-8-sig')
print("COMPLETED")
driver1.close()




# RUNS A LOOP TO GATHER ALL THE INVESTOR DATA
driver2 = webdriver.Chrome(service = Service(ChromeDriverManager().install()),
                          options = options)

stealth(driver2,
        languages = ["en-US", "en"],
        vendor = "Google Inc.",
        platform = "Win32",
        webgl_vendor = "Intel Inc.",
        renderer = "Intel Iris OpenGL Engine")

driver2.get(invest_site)
time.sleep(2)

no_thanks = driver2.find_element("xpath", "//a[text()[contains(., 'No thanks')]]")
no_thanks.click()
time.sleep(1)

cwa = driver2.find_element("xpath", "//button[text()[contains(., 'Continue without accepting')]]")
cwa.click()
time.sleep(1)

site_url = driver2.find_elements("xpath", "//ul[contains(@class, 'company_listings')]//a")
comp_name = driver2.find_elements("xpath", "//ul[contains(@class, 'company_listings')]//div[contains(@class, 'company-title')]//h5")
print("URLS: " + str(len(site_url)))
for cur_num in range(len(site_url)):
    print("Current Web: " + site_url[cur_num].get_attribute("href"))
    temp_df = pd.DataFrame()
    temp_df['#'] = [cur_num+1]
    temp_df['Bioeconomy Ventures URL'] = [site_url[cur_num].get_attribute("href")]
    temp_df['Name'] = [comp_name[cur_num].get_attribute("innerText")]
    temp_df['Website URL'] = [None]
    temp_df = get_investor(temp_df, site_url[cur_num].get_attribute("href"))
    if cur_num == 0:
        temp_df.to_csv(ex_path2, index = False, encoding='utf-8-sig')
    else:
        temp_df.to_csv(ex_path2, index = False, mode = 'a', header = False, encoding='utf-8-sig')


print("COMPLETED")
driver2.close()





