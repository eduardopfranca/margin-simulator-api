import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

"""
Prompt Perfeito para Extrair Dados de Portfólio de Opções em Dicionário Python:

Você é um especialista em análise de dados financeiros e interpretação de imagens. Dada uma imagem contendo um portfólio de opções, sua tarefa é extrair o ticker das opções e a quantidade total de cada posição. O objetivo é retornar um dicionário Python no seguinte formato:

```python
{
    "TICKER1": {"long": QUANTIDADE_LONG_1, "short": QUANTIDADE_SHORT_1},
    "TICKER2": {"long": QUANTIDADE_LONG_2, "short": QUANTIDADE_SHORT_2},
    # ... e assim por diante
}
Instruções Específicas:

Analise a imagem anexada (ou fornecida de outra forma). Identifique a coluna que contém o ticker das opções e a coluna que indica a quantidade total da posição ("Qtd Total").
Para cada linha da tabela de opções:
Extraia o ticker da opção exatamente como aparece na imagem.
Extraia o valor da "Qtd Total".
Interprete o sinal da quantidade:
Se a quantidade for um número positivo (sem o sinal "-"), atribua esse valor à chave "long" para o respectivo ticker, com o valor de "short" sendo 0.
Se a quantidade for um número negativo (com o sinal "-"), remova o sinal negativo e atribua o valor absoluto à chave "short" para o respectivo ticker, com o valor de "long" sendo 0.
Construa o dicionário Python: Utilize o ticker da opção como a chave principal do dicionário. O valor associado a cada ticker deve ser outro dicionário com as chaves "long" e "short" contendo as quantidades correspondentes.
Retorne APENAS o dicionário Python formatado exatamente como no exemplo, sem qualquer texto adicional, explicações ou formatação fora do dicionário. Certifique-se de que as chaves (tickers) e os valores (quantidades) estejam corretos.
Formato de Entrada (Versatilidade):

Este prompt deve ser capaz de processar informações de portfólios de opções apresentadas em:

Imagens (JPEG, PNG, etc.): Analise visualmente a tabela na imagem.
Tabelas de texto (como em planilhas de Excel coladas): Se a imagem for uma representação textual de uma tabela, interprete as linhas e colunas.
Outras fontes: Adapte a análise para identificar as colunas relevantes de ticker e quantidade, independentemente do formato de apresentação.
Exemplo de Saída Esperada (com base na sua imagem anterior):

Python

{
    "AAAAQ110": {"long": 0, "short": 500},
    "AAAAR118": {"long": 0, "short": 500},
    "BBBBE110": {"long": 0, "short": 600},
    "BBBBQ110": {"long": 0, "short": 600},
    "DDDDE352": {"long": 0, "short": 300},
    "EEEEF583": {"long": 0, "short": 200},
    "GGGGQ324": {"long": 0, "short": 300},
    "HHHHS563": {"long": 0, "short": 200},
    "MMMMF126": {"long": 0, "short": 200},
    "SSSSQ339": {"long": 0, "short": 300}
}

IMPORTANTE: RETORNAR A LISTA EM ORDEM ALFABÉTICA

IMPORTANTE: OBSERVE A ESTRUTURA DE UM TICKER DE OPCAO NO BRASIL: TTTTVNNN
T = letra referente ao ticker
V = letra referente ao vencimento 
N = número referente ao valor de strike
Ou seja, todo ticker tem obrigatoriamente que começar com 5 letras
"""

class MarginSimulatorAutoFiller:
    # URL of the B3 margin simulator
    URL = "https://simulador.b3.com.br/"

    # XPaths for the required elements on the simulation page
    OPTION_BUTTON_XPATH = (
        "/html/body/app-root/mat-drawer-container/mat-drawer-content/"
        "mat-sidenav-container/mat-sidenav-content/form/div[1]/div/div[5]/div[1]/div/div[4]/label"
    )
    TICKER_INPUT_XPATH = (
        "/html/body/app-root/mat-drawer-container/mat-drawer-content/"
        "mat-sidenav-container/mat-sidenav-content/form/div[1]/div/div[5]/div[2]/div[1]/div[1]/div/ng-select/div/div/div[2]/input"
    )
    # XPath for the Add button (to add each entry)
    ADD_BUTTON_XPATH = (
        "/html/body/app-root/mat-drawer-container/mat-drawer-content/"
        "mat-sidenav-container/mat-sidenav-content/form/div[1]/div/div[5]/div[2]/div[3]/div/button"
    )
    # XPath for the Calculate button (that updates the margin call value)
    CALCULATE_BUTTON_XPATH = (
        "/html/body/app-root/mat-drawer-container/mat-drawer-content/"
        "mat-sidenav-container/mat-sidenav-content/form/div[2]/div[3]/button[2]"
    )
    # XPath for the margin value cell in the resulting table
    MARGIN_VALUE_XPATH = (
        "/html/body/app-root/mat-drawer-container/mat-drawer-content/"
        "mat-sidenav-container/mat-sidenav-content/form/div[2]/div[4]/app-result/div[3]/table/tbody/tr[5]/td"
    )

    def __init__(self, driver):
        """
        Initializes the margin simulator with a Selenium WebDriver instance.
        """
        self.driver = driver
        self.alerts = []

    def visit_site(self, url):
        """Navigates to the specified URL."""
        self.driver.get(url)

    def find_element_by_xpath(self, xpath, wait=True):
        """
        Finds and returns an element using the provided XPath.
        If wait is True, waits until the element is present.
        """
        if wait:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        element = self.driver.find_element(By.XPATH, xpath)
        time.sleep(1)
        return element

    def type_text_in_xpath(self, xpath, text, wait=True):
        """
        Types the given text into an element located by the specified XPath.
        """
        if wait:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        element = self.find_element_by_xpath(xpath, wait=False)
        element.clear()
        time.sleep(1)
        element.send_keys(text)

    def press_enter(self):
        """Sends the ENTER key using ActionChains."""
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.RETURN).perform()

    def send_tab(self, times=1):
        """Sends the TAB key a given number of times."""
        actions = ActionChains(self.driver)
        for _ in range(times):
            actions.send_keys(Keys.TAB)
        actions.perform()

    def add_ticker(self, ticker, long_qty, short_qty):
        """
        Adds a single ticker to the margin simulator form using TAB navigation.
        
        Steps:
          1. Click the option button.
          2. Enter the ticker code and press ENTER.
          3. Press TAB once to focus on the long quantity field.
             - If long_qty is nonzero, type it; if zero, simply click the field.
          4. Press TAB again to focus on the short quantity field.
             - If short_qty is nonzero, type it; if zero, simply click the field.
          5. Click the add button to register the entry.
          
        :param ticker: The ticker code as a string.
        :param long_qty: Long (buy) quantity as a number.
        :param short_qty: Short (sell) quantity as a number.
        """
        # Click the option button to activate a new entry
        option_button = self.find_element_by_xpath(self.OPTION_BUTTON_XPATH)
        option_button.click()
        time.sleep(2)

        # Type the ticker and press ENTER
        self.type_text_in_xpath(self.TICKER_INPUT_XPATH, ticker)
        time.sleep(2)
        self.press_enter()
        time.sleep(2)

        # Press TAB to focus on the long quantity field
        self.send_tab(times=1)
        time.sleep(1)
        # Type the long quantity if nonzero; otherwise, just click the field
        active_field = self.driver.switch_to.active_element
        if int(long_qty) != 0:
            active_field.send_keys(str(long_qty))
        else:
            active_field.click()
        time.sleep(1)

        # Press TAB to move to the short quantity field
        self.send_tab(times=1)
        time.sleep(1)
        active_field = self.driver.switch_to.active_element
        if int(short_qty) != 0:
            active_field.send_keys(str(short_qty))
        else:
            active_field.click()
        time.sleep(1)

        # Finally, click the add button to add the entry to the portfolio
        add_button = self.find_element_by_xpath(self.ADD_BUTTON_XPATH)
        add_button.click()
        time.sleep(2)

    def fill_portfolio(self, portfolio):
        """
        Fills the margin simulator form with your portfolio data.
        
        The portfolio must be provided as a dictionary where each key is a ticker code
        and each value is another dictionary with keys 'long' and 'short'.
        The code uses TAB navigation:
          - After entering the ticker, it presses TAB to move to the long field.
          - If a quantity is zero, the field is simply clicked.
        
        :param portfolio: Dictionary with your portfolio data.
                          Example:
                          {
                              "valeq523": {"long": 0, "short": 500},
                              "valee583": {"long": 0, "short": 500},
                              "petrq324": {"long": 0, "short": 700},
                              "petre352": {"long": 0, "short": 700}
                          }
        """
        # Navigate to the simulator page
        self.visit_site(self.URL)
        time.sleep(3)

        # Process each ticker in the portfolio
        for ticker, positions in portfolio.items():
            long_qty = positions.get("long", 0)
            short_qty = positions.get("short", 0)
            self.add_ticker(ticker, long_qty, short_qty)

        # Click the calculate button to update the margin call value on the page
        calculate_button = self.find_element_by_xpath(self.CALCULATE_BUTTON_XPATH)
        calculate_button.click()
        time.sleep(3)

        print("Portfolio has been filled on the website. Margin call value should be visible.")

    def select_all_positions(self):
        """
        Finds and selects all checkboxes in the portfolio table.
        This method uses a generalized XPath to locate all the checkboxes.
        """
        checkboxes_xpath = (
            "//datatable-row-wrapper//datatable-body-row//datatable-body-cell[1]//input[@type='checkbox']"
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, checkboxes_xpath))
        )
        checkboxes = self.driver.find_elements(By.XPATH, checkboxes_xpath)
        print(f"Found {len(checkboxes)} checkboxes in the portfolio table.")

        for checkbox in checkboxes:
            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(0.5)

        print("All available checkboxes have been selected.")

    def click_calculate_again(self):
        """
        Clicks the calculate button once again to update the margin call,
        then extracts the margin value from the page.
        """
        calculate_button = self.find_element_by_xpath(self.CALCULATE_BUTTON_XPATH)
        calculate_button.click()
        time.sleep(3)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, self.MARGIN_VALUE_XPATH))
        )
        margin_element = self.find_element_by_xpath(self.MARGIN_VALUE_XPATH)
        margin_value = margin_element.text
        return margin_value

if __name__ == "__main__":
    # Initialize the Selenium WebDriver (Chrome in this example)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # For headless mode, uncomment the next line:
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    simulator = MarginSimulatorAutoFiller(driver)
    
    # Define your portfolio.
    # For sold positions, long is 0 and short is a positive number.
    portfolio = {
        "SMALB120": {"long": 0, "short": 100},
        "SMALB125": {"long": 100, "short": 0},
        "SMALN105": {"long": 100, "short": 0},
        "SMALN108": {"long": 0, "short": 100},
    }
    
    # Fill the portfolio on the website
    simulator.fill_portfolio(portfolio)
    
    # Select all the added positions by checking their checkboxes
    simulator.select_all_positions()
    
    # Click calculate again and extract the margin required value
    margin_required = simulator.click_calculate_again()
    
    # Create a DataFrame to represent your portfolio
    portfolio_rows = []
    for ticker, pos in portfolio.items():
        # For each ticker, if long is nonzero, that indicates a bought position;
        # if not, then it's sold, represented as a negative value.
        if pos.get("long", 0) != 0:
            position = pos["long"]
        else:
            position = -pos["short"]
        portfolio_rows.append({"ticker": ticker, "posicao": position})
    
    df = pd.DataFrame(portfolio_rows)
    
    # Print the portfolio DataFrame
    print("\nPortfolio:")
    print(df.to_string(index=False))
    print()  # Blank line
    
    print("Margem requerida para manutenção do portfolio: " + margin_required)
    
    input("\nPress ENTER when you are finished and wish to exit...")
    driver.quit()

