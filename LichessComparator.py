from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from localCredentials import *


GLOBAL_loadingSleep = 0.4
GLOBAL_loadingSleepCalculation = 1.5
GLOBAL_URL = "https://lichess.org/analysis"
GLOBAL_maxLoadingTime = 5


class LichessComparator:

    def __init__(self, isHeadless=False):

        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        if isHeadless:
            options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(chrome_options=options,executable_path=GLOBAL_webdriberPath)

    def connectToLichess(self):
        self.driver.get(GLOBAL_URL)
        try:
            testElm = WebDriverWait(self.driver, GLOBAL_maxLoadingTime).until(EC.presence_of_element_located((By.ID, 'blind-mode')))
            return True
        except TimeoutException:
            return False

    def getScore(self,fen):


        # clear input then enter FEN & press ENTER
        self.driver.find_element_by_class_name('analyse__underboard__fen').clear()
        for i in range(120):
            self.driver.find_element_by_class_name('analyse__underboard__fen').send_keys(Keys.BACKSPACE )

        self.driver.find_element_by_class_name('analyse__underboard__fen').send_keys(fen,Keys.ENTER)

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
            score = -eval(score)
        
        if '++' in score:
            score = eval(score)

        score = eval(score)

        score = float(score) 

        return score

if __name__ == "__main__":

    instance = LichessComparator(False)
    isConnected = instance.connectToLichess()

    sleep(4)

    FENS = [
        '1B6/pp6/8/8/4k3/1PK1P2p/P1P3r1/8 b - - 9 41',
        '8/1p6/1P6/8/p2r4/K7/P1Pk4/8 b - - 4 49',
        '3r3r/pp2qk1p/3p1n2/4p3/1B2PP1R/3Q4/PPP2P2/2KR4 b - - 0 22',
    ]

    for FEN in FENS:
        print(instance.getScore(FEN))