import re
import uuid
import time
import json
import httpx
from sys import exit
from time import sleep
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

start_time = datetime.now()

s = Service('')  # Path to chromedriver

init(autoreset=True)

print(f"{Fore.BLUE}{Style.BRIGHT}Login with clever or the dreambox site? (clever or dreambox) ===> ", end='')
method = input()

print(f"{Fore.BLUE}{Style.BRIGHT}Do you want a invisible (y) or visible browser (n)? (default = invis) ===> ", end='')
browser = input()

invis = True
if browser == "y":
    invis = True
elif browser == "n":
    invis = False

amount = 1
print(f"{Fore.BLUE}{Style.BRIGHT}How many lessons do you want to do? (default = 1) ===> ", end='')
try:
    amount = int(input())
except:
    pass

logging = "needed"
print(f"{Fore.BLUE}{Style.BRIGHT}What logging method? (all or needed, default = needed)? ===> ", end='')
try:
    logging = input()
except:
    pass


config = json.loads(Path("config.json").read_text())
passwd = config["password"]
email = config["email"]

if method == "dreambox":
    url = "https://play.dreambox.com/play/login"
else:
    url = config["clever"]


done_L = 0
failed_L = 0
average_before = 0

options = Options()

options.add_argument("start-maximized")
options.add_argument("--log-level=3")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

if invis:
    options.add_argument('--headless')
else:
    options.add_argument('--browser')

driver = webdriver.Chrome(service=s, options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

driver.get(url)
actions = ActionChains(driver)
if method == "clever":
    driver.find_elements(By.CLASS_NAME, "AuthMethod--icon")[0].click()
    driver.find_elements(By.ID, "identifierId")[0].click()
    print(f"{Style.BRIGHT}{Fore.YELLOW}Opened clever login page. Logging in")
    sleep(0.75)

    actions.send_keys(email)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    sleep(5)

    actions.send_keys(passwd)
    actions.send_keys(Keys.ENTER)
    actions.perform()
else:
    driver.find_elements(By.ID, "txtEmailAddress")[0].click()
    actions.send_keys(email)
    actions.send_keys(Keys.TAB)
    actions.perform()
    sleep(0.75)

    actions.send_keys(passwd)
    sleep(0.5)
    driver.find_elements(By.ID, "buttonLogin")[0].click()


print(f"{Style.BRIGHT}{Fore.YELLOW}Logged in, waiting for redirect")
sleep(8)
print(f"{Style.BRIGHT}{Fore.YELLOW}Now in Dreambox")

cookies = driver.get_cookies()

utmb_f = cookies[0]
utmb = re.search("'value': '(.+?)'", str(utmb_f)).group(1)

utmt_f = cookies[1]
utmt = re.search("'value': '(.+?)'", str(utmt_f)).group(1)

utmc_f = cookies[2]
utmc = re.search("'value': '(.+?)'", str(utmc_f)).group(1)

utma_f = cookies[3]
utma = re.search("'value': '(.+?)'", str(utma_f)).group(1)

utmz_f = cookies[4]
utmz = re.search("'value': '(.+?)'", str(utmz_f)).group(1)

session_f = cookies[5]
session = re.search("'value': '(.+?)'", str(session_f)).group(1)

cookie = f"_session_id={session}; __utma={utma}; __utmc={utmc}; __utmz={utmz}; __utmt={utmt}; __utmb={utmb}"
print(f"{Style.BRIGHT}{Fore.YELLOW}Grabbed cookie")

html = driver.find_element(By.XPATH, "//body").get_attribute('outerHTML')

try:
    auth = re.search('&authsession=(.+?)"', html).group(1)
except AttributeError:
    auth = ''
    exit(f"{Style.BRIGHT}{Fore.RED}couldnt find auth string")

try:
    studentID = re.search('&studentid=(.+?)"', html).group(1)
except AttributeError:
    studentID = ''
    exit(f"{Style.BRIGHT}{Fore.RED}couldnt find studentID")

try:
    clientinstance = re.search('&clientinstance=(.+?)"', html).group(1)
except AttributeError:
    clientinstance = ''
    exit(f"{Style.BRIGHT}{Fore.RED}couldnt find clientinstance")

print(f"{Style.BRIGHT}{Fore.YELLOW}Grabbed auth string")
print(f"{Style.BRIGHT}{Fore.YELLOW}Grabbed student id")
print(f"{Style.BRIGHT}{Fore.YELLOW}Grabbed clientInstance")
print(f"{Style.BRIGHT}{Fore.YELLOW}Closing Dreambox")
driver.quit()

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
start_info = f"https://play.dreambox.com/public/v1/users/{studentID}/recommendations"
start = f"https://play.dreambox.com/public/v1/users/{studentID}/lessonStart"
end = f"https://play.dreambox.com/public/v1/users/{studentID}/lessonEnd"

headers_start_info = {

    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "dbl-authsessionuuid": auth,
    "origin": "https://play.dreambox.com",
    "referer": "https://play.dreambox.com/student/dbl?back=https%3A%2F%2Fplay.dreambox.com%2Fdashboard%2Flogin",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": useragent,

}

payload_start_info = {

    "recommendCount": "8"

}


def reload_rec():
    global recommendationID
    global lessonID
    global fqln

    i = httpx.post(start_info, headers=headers_start_info, data=json.dumps(payload_start_info))

    try:
        recommendationID = re.search('"recommendationUuid":"(.+?)",', i.text).group(1)
    except AttributeError:
        recommendationID = ''
        print(i.text)
        exit(f"{Style.BRIGHT}{Fore.RED}couldnt find recommendationUuid string")

    try:
        lessonID = int(re.search('"lessonId":(.+?),', i.text).group(1))
    except ValueError:
        exit(f"{Style.BRIGHT}{Fore.RED}lessonID was not an integer")
    except AttributeError:
        lessonID = ''
        exit(f"{Style.BRIGHT}{Fore.RED}couldnt find lessonID")

    try:
        fqln = re.search('"fqln":"(.+?)",', i.text).group(1)
    except AttributeError:
        fqln = ''
        exit(f"{Style.BRIGHT}{Fore.RED}couldnt find fqln")

    if logging == "all":
        print(f"{Style.BRIGHT}{Fore.YELLOW}Grabbed recommendationUuid, lessonID, and fqln")

headers_start = {

    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "cookie": cookie,
    "dbl-authsessionuuid": auth,
    "dbl-clientinstanceuuid": clientinstance,
    "dbl-clientrequestuuid": str(uuid.uuid4()),
    "origin": "https://play.dreambox.com",
    "referer": "https://play.dreambox.com/student/dbl?back=https%3A%2F%2Fplay.dreambox.com%2Fdashboard%2Flogin",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": useragent,

}

sequence = 2


def start_l():
    global lessonPlayUuid
    global lessonInstanceUuid
    global asData

    reload_rec()

    payload_start = {

        "assignmentId": None,
        "lessonId": lessonID,
        "recommendationUuid": recommendationID,
        "sequence": sequence,

    }

    with httpx.Client(headers=headers_start) as client:

        s = client.post(start, data=json.dumps(payload_start))

        if logging == "all":
            print(f"{Style.BRIGHT}{Fore.YELLOW}Sent start request")

        try:
            lessonPlayUuid = re.search('"lessonPlayUuid":"(.+?)",', s.text).group(1)
        except AttributeError:
            lessonPlayUuid = ""
            exit(f"{Style.BRIGHT}{Fore.RED}couldnt find lessonPlayUuid string")

        try:
            lessonInstanceUuid = re.search('"lessonInstanceUuid":"(.+?)",', s.text).group(1)
        except AttributeError:
            lessonInstanceUuid = ""
            exit(f"{Style.BRIGHT}{Fore.RED}couldnt find lessonInstanceUuid")

        if logging == "all":
            print(f"{Style.BRIGHT}{Fore.YELLOW}Grabbed lessonPlayUuid, and lessonInstanceUuid")

        asData = {"li": 934, "uuid": "b7a616db-bcfc-4974-88ed-3c6abf10c4f2", "lv": 4, "v": 3.02, "rv": 4, "aid": None, "ld": {"c": False, "p": False, "ltn": 1, "lta": 1, "s": 6, "prg": 100, "sn": 7}, "mo": [], "ls": [{"auid": "d2c50af7-8d24-4e03-ad22-30f69be7f864", "lsn": 1, "lss": 5,"pid": "9504b0a3-fbef-4eda-b84c-6c6b8a9de5cb", "prg": 100, "rid": "4f932263-16fc-41d7-814c-1f8cf8763d1b","s1": 91216, "s2": 91316, "scv": "16.14.3", "sp": 1646448098780, "st": 1646448091217, "ts": [{"cp": 0.5, "cs": 0, "ies": [{"o": 1, "qs": [1], "t": 1}, {"o": 3450, "qs": [1], "t": 7}],"kc": "problembasetwentysuper.harda.hardx.parentheses.horizontal", "lsn": 1, "ms": [{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [1], "qt": "basicfact", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "drag", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "challenge", "sc": 0,"st": 0, "sv": False}], "pr": [{"dr": True, "pid": 1, "qs": [1], "st": 0, "sp": None}], "qu": [{"as": [], "at": False, "dr": True, "pid": 1, "qid": 1, "qt": "basicfact", "sc": 0, "ss": 1,"st": 1, "sp": None}], "sp": 1646448098780, "st": 1646448095330, "ta": 1, "tn": 1, "tsn": 1}]},{"auid": "0de41972-05e0-4ab8-a833-3e6d9aeda899", "lsn": 2, "lss": 5,"pid": "b6c775a2-6048-4789-a81d-f4bd37aa0613", "prg": 100, "rid": "660fff90-f0ab-45b7-a8c4-8e0a9e7f2ecd","s1": 91316, "s2": 91316, "scv": "16.14.3", "sp": 1646448387162, "st": 1646448256115, "ts": [{"cp": 0.5, "cs": 0, "ies": [{"o": 7, "qs": [2], "t": 1}, {"o": 5620, "qs": [2], "t": 14},{"o": 5986, "qs": [2], "t": 13}, {"o": 7041, "qs": [2], "t": 14},{"o": 7913, "qs": [2], "t": 13}, {"o": 12161, "qs": [2], "t": 2},{"o": 116680, "qs": [2], "t": 14}, {"o": 119064, "qs": [2], "t": 13},{"o": 127046, "qs": [2], "t": 14}],"kc": "problembasetwentysuper.harda.hardx.parentheses.horizontal", "lsn": 2, "ms": [{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [2], "qt": "basicfact", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "drag", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "challenge", "sc": 0,"st": 0, "sv": False}], "pr": [{"dr": True, "pid": 2, "qs": [2], "st": 6, "sp": None}], "qu": [{"as": [], "at": False, "dr": True, "pid": 2, "qid": 2, "qt": "basicfact", "sc": 0, "ss": 1,"st": 7, "sp": None}], "sp": 1646448387161, "st": 1646448260056, "ta": 1, "tn": 1, "tsn": 2}]},{"auid": "d151006b-f8ec-43cf-ad43-16cc17deac1d", "lsn": 3, "lss": 4,"pid": "f09dd679-ff3c-4d5c-a8c8-56c3f8305635", "prg": 100, "rid": "0e3aa065-084d-4220-a952-ed856eb301fd","s1": 91416, "s2": 91316, "scv": "16.14.3", "sp": 1646523471610, "st": 1646522757341, "ts": [{"cp": 0.5, "cs": 0, "ies": [{"o": 6, "qs": [3], "t": 1}, {"o": 2427, "qs": [3], "t": 13},{"o": 7448, "qs": [3], "t": 2}, {"o": 309835, "qs": [3], "t": 11},{"o": 711259, "qs": [3], "t": 12}],"kc": "problembasetwentysuper.harda.hardx.parentheses.horizontal", "lsn": 3, "ms": [{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [3], "qt": "basicfact", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "drag", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "challenge", "sc": 0,"st": 0, "sv": False}], "pr": [{"dr": True, "pid": 3, "qs": [3], "st": 5, "sp": None}], "qu": [{"as": [], "at": False, "dr": True, "pid": 3, "qid": 3, "qt": "basicfact", "sc": 0, "ss": 1,"st": 6, "sp": None}], "sp": 1646523471609, "st": 1646522760338, "ta": 1, "tn": 1, "tsn": 3}]},{"auid": "ed4769e6-aac0-4803-910a-1c39f679f3ff", "lsn": 4, "lss": 5,"pid": "d6a60a49-60d9-4008-b5bd-2090b3b14a55", "prg": 0, "rid": "7e5eea77-ffd7-4c28-a784-5f879d3642c2","s1": 91516, "s2": 91316, "scv": "16.14.3", "sp": 1646589802877, "st": 1646589743007, "ts": [{"cp": 0.5, "cs": 0, "ies": [{"o": 6, "qs": [4], "t": 1}, {"o": 7177, "qs": [4], "t": 2},{"o": 56793, "qs": [4], "t": 14}],"kc": "problembasetwentysuper.harda.hardx.parentheses.horizontal", "lsn": 4, "ms": [{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [4], "qt": "basicfact", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "drag", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "challenge", "sc": 0,"st": 0, "sv": False}], "pr": [{"dr": True, "pid": 4, "qs": [4], "st": 5, "sp": None}], "qu": [{"as": [], "at": False, "dr": True, "pid": 4, "qid": 4, "qt": "basicfact", "sc": 0, "ss": 1,"st": 6, "sp": None}], "sp": 1646589802877, "st": 1646589746006, "ta": 1, "tn": 1, "tsn": 4}]},{"auid": "e190769f-2e4f-4aa3-9b85-de896544c425", "lsn": 5, "lss": 5,"pid": "b32b2782-7c1b-4831-895c-c488eafdc250", "prg": 0, "rid": "836185b5-5525-4297-b5e9-9a903b2da71d","s1": 91616, "s2": 91316, "scv": "16.14.3", "sp": 1646591451473, "st": 1646591402252, "ts": [{"cp": 0.5, "cs": 0, "ies": [{"o": 10, "qs": [5], "t": 1}, {"o": 5941, "qs": [5], "t": 13},{"o": 7574, "qs": [5], "t": 2}, {"o": 46187, "qs": [5], "t": 14}],"kc": "problembasetwentysuper.harda.hardx.parentheses.horizontal", "lsn": 5, "ms": [{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [5], "qt": "basicfact", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "drag", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "challenge", "sc": 0,"st": 0, "sv": False}], "pr": [{"dr": True, "pid": 5, "qs": [5], "st": 8, "sp": None}], "qu": [{"as": [], "at": False, "dr": True, "pid": 5, "qid": 5, "qt": "basicfact", "sc": 0, "ss": 1,"st": 10, "sp": None}], "sp": 1646591451473, "st": 1646591405170, "ta": 1, "tn": 1,"tsn": 5}]}, {"auid": "eb478379-0d40-448c-bb13-8a89812c8915", "lsn": 6, "lss": 5,"pid": "e4971144-ad49-47e5-b8e4-47c5bb57180a", "prg": 0,"rid": "eaf0c54c-4515-4e2d-9e66-efeed4dd5fe5", "s1": 91716, "s2": 91316,"scv": "16.14.3", "sp": 1646595774967, "st": 1646595755901, "ts": [{"cp": 0.5, "cs": 0, "ies": [{"o": 7, "qs": [6], "t": 1}, {"o": 7252, "qs": [6], "t": 2}],"kc": "problembasetwentysuper.harda.hardx.parentheses.horizontal", "lsn": 6, "ms": [{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [6], "qt": "basicfact","sc": 0, "st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "drag", "sc": 0,"st": 0, "sv": False},{"at": 1, "cp": 0.5, "mpt": "buildingarrays_leveltwelve", "qs": [], "qt": "challenge","sc": 0, "st": 0, "sv": False}],"pr": [{"dr": True, "pid": 6, "qs": [6], "st": 5, "sp": None}], "qu": [{"as": [], "at": False, "dr": True, "pid": 6, "qid": 6, "qt": "basicfact", "sc": 0, "ss": 1,"st": 7, "sp": None}], "sp": 1646595774967, "st": 1646595758607, "ta": 1, "tn": 1,"tsn": 6}]}, {"lsn": 7, "lss": 6, "pid": "6c2e9711-8c8a-41a4-bd43-ce09f26d5685","rid": "1e86740a-0f1f-4bb0-b624-c26ca0371b2a", "st": 1646599867545,"sp": 1646600941109, "scv": "16.14.3", "s1": 91816, "s2": 91316, "prg": 0,"auid": "c56a89bb-41b8-4bb9-ad54-0fe87912b0f7", "ts": [{"tt": None, "rc": None, "tn": 1, "lsn": 7, "tsn": 7, "ta": 1,"kc": "problembasetwentysuper.harda.hardx.parentheses.horizontal", "st": 1646599870232,"sp": 1646600941109, "cp": 0.5, "cs": 0, "ms": [{"qt": "basicfact", "mpt": "buildingarrays_leveltwelve", "mqt": None, "qs": [7], "at": 1,"st": 0, "cp": 0.5, "sc": 0, "sv": False},{"qt": "drag", "mpt": "buildingarrays_leveltwelve", "mqt": None, "qs": [], "at": 1, "st": 0,"cp": 0.5, "sc": 0, "sv": False},{"qt": "challenge", "mpt": "buildingarrays_leveltwelve", "mqt": None, "qs": [], "at": 1,"st": 0, "cp": 0.5, "sc": 0, "sv": False}],"pr": [{"dr": True, "pid": 7, "st": 6, "sp": None, "qs": [7]}], "qu": [{"dr": True, "qid": 7, "pid": 7, "qt": "basicfact", "sc": 0, "at": False, "ss": 1, "st": 7,"sp": None, "as": []}],"ies": [{"t": 1, "o": 7, "qs": [7]}, {"t": 13, "o": 2234, "qs": [7]},{"t": 14, "o": 5402, "qs": [7]}, {"t": 13, "o": 6240, "qs": [7]},{"t": 2, "o": 10805, "qs": [7]}, {"t": 14, "o": 242356, "qs": [7]},{"t": 13, "o": 243771, "qs": [7]}, {"t": 11, "o": 313880, "qs": [7]},{"t": 14, "o": 945065, "qs": [7]}, {"t": 12, "o": 946098, "qs": [7]},{"t": 13, "o": 946589, "qs": [7]}]}]}]}
        # if you are looking at the code, dreambox doesnt care about asData as long as it has values.

headers_end = {

    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "cookie": cookie,
    "dbl-authsessionuuid": auth,
    "dbl-clientinstanceuuid": clientinstance,
    "dbl-clientrequestuuid": str(uuid.uuid4()),  # gens random uuid
    "origin": "https://play.dreambox.com",
    "referer": "https://play.dreambox.com/student/dbl?back=https%3A%2F%2Fplay.dreambox.com%2Fdashboard%2Flogin",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": useragent,

}


def end_lesson(start_time):
    payload_end = {

        "lessonId": lessonID,
        "lessonInstanceUuid": lessonInstanceUuid,
        "sequence": sequence,
        "assignmentId": None,
        "exitCode": "PASS",
        "scores": [
            {"problemType": "auto_levelfortysix", "questionType": "standard", "score": 100, "maxPossibleScore": 100}],   # auto_levelfortsix might not matter, same as asData, as long as it exists its probalby good
        "progress": 100,
        "recommendationUuid": recommendationID,
        "lessonPlayUuid": lessonPlayUuid,
        "asData": asData,

    }

    e = httpx.post(end, headers=headers_end, data=json.dumps(payload_end))
    if "200" in str(e):
        global done_L, elapsed_time, average_before

        done_L += 1
        elapsed_time = time.time() - start_time
        average_before += elapsed_time
        print(f"{Style.BRIGHT}{Fore.GREEN}Completed lesson x{done_L} in {round(elapsed_time, 3)} seconds")

    else:
        global failed_L

        failed_L += 1
        print(f"{Style.BRIGHT}{Fore.RED}Problem with lesson completion; x{failed_L} {e.text}")


def dreambox():
    global average
    for lesson in range(amount):
        t0 = time.time()
        start_l()
        end_lesson(t0)
    average = average_before / amount

dreambox()

stop_time = datetime.now()
print(
    f"It took {stop_time - start_time} (hours:minutes:seconds) to do {done_L} successful lessons and {failed_L} failed lessons. The average time was {round(average, 3)} seconds")
