from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from localCredentials import *


GLOBAL_loadingSleep = 0.2
GLOBAL_loadingSleepCalculation = 1
GLOBAL_URL = "https://lichess.org/analysis"
GLOBAL_maxLoadingTime = 5


class LichessComparator:

    def __init__(self, AI_color, isHeadless=False):

        options = webdriver.ChromeOptions()
        chrome_options = Options()
        chrome_options.add_argument('log-level=2')
        options.add_argument('--no-sandbox')
        if isHeadless:
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(chrome_options=options,executable_path=GLOBAL_webdriberPath)
        self.AI_color = AI_color

    def connectToLichess(self):
        self.driver.get(GLOBAL_URL)
        try:
            testElm = WebDriverWait(self.driver, GLOBAL_maxLoadingTime).until(EC.presence_of_element_located((By.ID, 'blind-mode')))
            return True
        except TimeoutException:
            return False

    def getScore(self,fen):

        # Correct FEN
        if self.AI_color == 'black':
            correctedFen = fen.replace('w','b')
        else:
            correctedFen = fen.replace('b','w')

        # clear input then enter FEN & press ENTER
        self.driver.find_element_by_class_name('analyse__underboard__fen').clear()
        for i in range(120):
            self.driver.find_element_by_class_name('analyse__underboard__fen').send_keys(Keys.BACKSPACE )

        self.driver.find_element_by_class_name('analyse__underboard__fen').send_keys(correctedFen,Keys.ENTER)

        # loading FEN time
        sleep(GLOBAL_loadingSleep)

        # activate Analyzer
        self.driver.find_element_by_xpath('/html/body/div/main/div[2]/div[1]/div/label').click()

        # calculating time
        sleep(GLOBAL_loadingSleepCalculation)

        # get score
        score = self.driver.find_element_by_xpath("/html/body/div/main/div[3]/div[1]/pearl").text

        # Format score
        while '#' in score:
            score = score.replace('#','')

        if '--' in score:
            try:
                score = -eval(score)
            except:
                score = 0
        
        if '++' in score:
            try:
                score = eval(score)
            except:
                score = 0

        try:
            score = eval(score)
        except:
            score = 0

        score = float(score) 

        return score

if __name__ == "__main__":

    instance = LichessComparator(False)
    isConnected = instance.connectToLichess()

    sleep(4)

    FENS = [
    '3k4/4p3/8/8/8/8/4P3/3K4 w - - 0 1',
    '3k4/4p3/8/8/8/4P3/8/3K4 b - - 0 1',
    '8/2k1p3/8/8/8/4P3/8/3K4 w - - 1 2',
    '8/2k1p3/8/8/8/4P3/8/4K3 b - - 2 2',
    '8/4p3/3k4/8/8/4P3/8/4K3 w - - 3 3',
    '8/4p3/3k4/8/8/4P3/8/3K4 b - - 4 3',
    '8/4p3/8/2k5/8/4P3/8/3K4 w - - 5 4',
    '8/4p3/8/2k5/8/4P3/2K5/8 b - - 6 4',
    '8/8/8/2k1p3/8/4P3/2K5/8 w - - 0 5',
    '8/8/8/2k1p3/8/2K1P3/8/8 b - - 1 5'
    ]

    for FEN in FENS:
        print(FEN)
        print(instance.getScore(FEN))