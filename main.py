import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

app = FastAPI()

class MarginSimulatorService:
    URL = "https://simulador.b3.com.br/"
    
    # XPaths fornecidos por você
    OPTION_BUTTON_XPATH = "/html/body/app-root/mat-drawer-container/mat-drawer-content/mat-sidenav-container/mat-sidenav-content/form/div[1]/div/div[5]/div[1]/div/div[4]/label"
    TICKER_INPUT_XPATH = "/html/body/app-root/mat-drawer-container/mat-drawer-content/mat-sidenav-container/mat-sidenav-content/form/div[1]/div/div[5]/div[2]/div[1]/div[1]/div/ng-select/div/div/div[2]/input"
    ADD_BUTTON_XPATH = "/html/body/app-root/mat-drawer-container/mat-drawer-content/mat-sidenav-container/mat-sidenav-content/form/div[1]/div/div[5]/div[2]/div[3]/div/button"
    CALCULATE_BUTTON_XPATH = "/html/body/app-root/mat-drawer-container/mat-drawer-content/mat-sidenav-container/mat-sidenav-content/form/div[2]/div[3]/button[2]"
    MARGIN_VALUE_XPATH = "/html/body/app-root/mat-drawer-container/mat-drawer-content/mat-sidenav-container/mat-sidenav-content/form/div[2]/div[4]/app-result/div[3]/table/tbody/tr[5]/td"

    def __init__(self, driver):
        self.driver = driver

    def fill_portfolio(self, portfolio):
        self.driver.get(self.URL)
        time.sleep(3)
        for ticker, pos in portfolio.items():
            # Seleciona Opção
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, self.OPTION_BUTTON_XPATH))).click()
            time.sleep(1)
            
            # Ticker
            input_field = self.driver.find_element(By.XPATH, self.TICKER_INPUT_XPATH)
            input_field.send_keys(ticker)
            time.sleep(1)
            ActionChains(self.driver).send_keys(Keys.RETURN).perform()
            time.sleep(1)
            
            # Quantidades via TAB
            ActionChains(self.driver).send_keys(Keys.TAB).perform()
            active = self.driver.switch_to.active_element
            if pos.get("long", 0) != 0: active.send_keys(str(pos["long"]))
            
            ActionChains(self.driver).send_keys(Keys.TAB).perform()
            active = self.driver.switch_to.active_element
            if pos.get("short", 0) != 0: active.send_keys(str(pos["short"]))
            
            # Adicionar
            self.driver.find_element(By.XPATH, self.ADD_BUTTON_XPATH).click()
            time.sleep(2)

    def select_all_and_calculate(self):
        # Calcular primeiro
        self.driver.find_element(By.XPATH, self.CALCULATE_BUTTON_XPATH).click()
        time.sleep(3)
        
        # Checkboxes
        cb_xpath = "//datatable-row-wrapper//datatable-body-row//datatable-body-cell[1]//input[@type='checkbox']"
        checkboxes = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, cb_xpath)))
        for cb in checkboxes:
            if not cb.is_selected(): 
                cb.click()
                time.sleep(0.5)
        
        # Calcular Final
        self.driver.find_element(By.XPATH, self.CALCULATE_BUTTON_XPATH).click()
        time.sleep(3)
        return self.driver.find_element(By.XPATH, self.MARGIN_VALUE_XPATH).text

    @staticmethod
    def get_driver():
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # No Render, o binário do Chrome fica em um local específico se usar o script de build
        if os.path.exists("/usr/bin/google-chrome"):
            options.binary_location = "/usr/bin/google-chrome"
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

@app.post("/calculate-margin")
async def calculate_margin(portfolio: dict):
    driver = MarginSimulatorService.get_driver()
    try:
        service = MarginSimulatorService(driver)
        service.fill_portfolio(portfolio)
        margin = service.select_all_and_calculate()
        return {"status": "success", "margin_required": margin}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.quit()

if __name__ == "__main__":
    # Configuração para teste VISUAL (Local)
    options = Options()
    options.add_argument("--start-maximized")
    # Removido o --headless para você ver o teste rodando
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Seu dicionário de teste
    test_portfolio = {
        "BPACM502": {"long": 0, "short": 100},
        "PETRB330": {"long": 0, "short": 200},
        "SMALB125": {"long": 100, "short": 0}
    }
    
    try:
        service_instance = MarginSimulatorService(driver)
        service_instance.fill_portfolio(test_portfolio)
        resultado = service_instance.select_all_and_calculate()
        
        print("\n" + "="*30)
        print(f"RESULTADO: {resultado}")
        print("="*30)
        
    except Exception as e:
        print(f"ERRO NO TESTE: {e}")
    finally:
        input("\nTeste finalizado. Pressione ENTER para fechar o navegador...")
        driver.quit()