from selenium.webdriver.firefox.webdriver import WebDriver

class SeleniumTests():
    
    live_server_url = ''  #type: str
    selenium = None #type: WebDriver

    def __init__(self, live_server_url, selenium):
        #type: (str, WebDriver)->None
        self.live_server_url = live_server_url
        self.selenium = selenium

    def loginUsuari(self, nomUsuari, password):
        #type: (str, str)->None
        self.selenium.get( self.live_server_url + '/usuaris/login/')
        #localitza usuari i paraulaDePas
        inputUser = self.selenium.find_element_by_name("usuari")
        inputUser.clear()
        inputUser.send_keys(nomUsuari)
        inputParaulaDePas = self.selenium.find_element_by_name("paraulaDePas")
        inputParaulaDePas.clear()
        inputParaulaDePas.send_keys(password)
        botons = self.selenium.find_elements_by_xpath("//button[@type='submit']")
        boto = botons[0]
        boto.click()

        