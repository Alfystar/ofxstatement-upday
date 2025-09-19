import csv
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from decimal import Decimal
from io import TextIOWrapper
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement, StatementLine
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Iterable, List, Dict, Any
from webdriver_manager.chrome import ChromeDriverManager


# ============================================================================
# DATE VALIDATION FUNCTIONS
# ============================================================================

def _validate_start_date(start_date: str) -> bool:
    """
    Valida che la data di inizio non sia antecedente a 1 anno fa

    Args:
        start_date: Data di inizio nel formato gg/mm/aaaa

    Returns:
        True se la data è valida, False altrimenti
    """
    try:
        # Parse della data di inizio
        start_dt = datetime.strptime(start_date, "%d/%m/%Y").date()

        # Calcola la data limite (1 anno fa da oggi + 1 giorno per evitare problemi dovuti all'orario di esecuzione)
        one_year_ago = (datetime.now() - timedelta(days=364)).date()

        # Verifica se la data di inizio è troppo vecchia
        if start_dt < one_year_ago:
            print("\n" + "=" * 70)
            print("❌ ERRORE: DATA DI INIZIO NON VALIDA")
            print("=" * 70)
            print(f"🚫 Data inserita: {start_date}")
            print(f"📅 Data limite del sito: {one_year_ago.strftime('%d/%m/%Y')}")
            print(f"⚠️  Il sito UpDay non permette di accedere a dati antecedenti a 1 anno fa.")
            print(f"✅ La prima data ammissibile è: {one_year_ago.strftime('%d/%m/%Y')}")
            print("\n💡 Suggerimento: Inserisci una data di inizio più recente.")
            print("=" * 70)
            return False

        return True

    except ValueError:
        print(f"❌ Errore nel parsing della data: {start_date}")
        return False
    except Exception as e:
        print(f"❌ Errore nella validazione della data: {e}")
        return False


# ============================================================================
# WEB SCRAPING FUNCTIONS
# ============================================================================

def _get_date_from_user(info: str = "inizio", optional: bool = False) -> str:
    """Chiede all'utente di inserire la data di inizio"""
    while True:
        date_input = input(f"Inserisci la data di {info} (formato gg/mm/aaaa, g/m/aa, ecc.): ").strip()
        if optional and date_input == "":
            return ""
        # Prova diversi formati di data
        date_formats = [
            "%d/%m/%Y",
            "%d/%m/%y",
            "%d-%m-%Y",
            "%d-%m-%y",
            "%d.%m.%Y",
            "%d.%m.%y"
        ]

        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_input, fmt)
                # Converte nel formato richiesto dal sito (gg/mm/aaaa)
                formatted_date = parsed_date.strftime("%d/%m/%Y")

                # Valida la data solo per la data di inizio (non opzionale)
                if not optional and not _validate_start_date(formatted_date):
                    break  # Esci dal loop dei formati e richiedi una nuova data

                return formatted_date
            except ValueError:
                continue

        # Se arriviamo qui, o il formato non è valido o la data non è ammissibile
        if not optional:
            # Per la data di inizio, mostra un messaggio più specifico
            one_year_ago = datetime.now() - timedelta(days=365)
            print(f"⚠️  Inserisci una data valida non antecedente al {one_year_ago.strftime('%d/%m/%Y')}")
        else:
            print("Formato data non valido. Riprova con formato gg/mm/aaaa")


def _setup_browser():
    # TODO: scegliere quale browser usare in base alla configurazione
    """Configura e avvia il browser Chrome"""
    print("Avvio del browser...")

    chrome_options = Options()

    # FORZA la modalità con UI visibile - importante per il debugger
    chrome_options.add_argument("--disable-headless")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-default-apps")

    # Configurazioni di sicurezza e prestazioni
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")

    # Imposta una finestra di dimensioni moderate invece di schermo intero
    chrome_options.add_argument("--window-size=1200,800")
    chrome_options.add_argument("--window-position=100,100")

    # Rimuovo start-maximized per evitare schermo intero
    chrome_options.add_experimental_option("detach", True)

    # Configurazioni per supportare CAPTCHA e login
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        # RIMUOVO la disabilitazione delle immagini per permettere il CAPTCHA
        # "profile.managed_default_content_settings.images": 2  # COMMENTATO!
        "profile.default_content_setting_values.media_stream": 2,
        "profile.default_content_setting_values.geolocation": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Aggiungi User-Agent realistico per evitare detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Disabilita automation flags per sembrare più umano
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Per il debugging: aggiungi log verboso ma meno invasivo
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=1")  # Riduco il livello di log

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Nascondi il fatto che stiamo usando webdriver
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.implicitly_wait(10)

        # Rimuovo maximize_window() per mantenere dimensioni moderate
        # driver.maximize_window()

        print(f"Browser avviato correttamente. Finestra visibile: {not driver.get_window_size() is None}")
        return driver

    except Exception as e:
        print(f"Errore nell'avvio del browser: {e}")
        print("Tentativo con configurazione alternativa...")

        try:
            # Configurazione di fallback più semplice con finestra normale
            simple_options = Options()
            simple_options.add_argument("--disable-headless")
            simple_options.add_argument("--no-sandbox")
            simple_options.add_argument("--window-size=1200,800")
            simple_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=simple_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.implicitly_wait(10)
            # Rimuovo maximize_window() anche dal fallback
            # driver.maximize_window()

            return driver
        except Exception as fallback_e:
            _handle_fatal_error(None, f"Impossibile avviare Chrome. Assicurati che Chrome sia installato sul sistema", fallback_e)


def _wait_page_load(driver, href_click_url, destination_url, timeout: int = 120):
    """Attende che l'utente completi le azioni necessarie partendo dall' href_click_url per arrivare al destination_url, entro un timeout"""
    driver.execute_script(f"window.location.href = '{href_click_url}';")
    print(f"Link cliccato, in attesa di giungere a '{destination_url}' entro il timeout di {timeout}s ...")
    # Attendi che la pagina navighi all'URL target
    try:
        WebDriverWait(driver, timeout).until(lambda driver: driver.current_url == destination_url)
    except Exception as e:
        raise TimeoutError(f"Timeout: non sono riuscito a navigare a '{destination_url}' automaticamente.") from e


def _navigate_to_login(driver):
    """Naviga alla pagina di login e clicca sul pulsante evidenziato"""
    print("Navigazione alla pagina di login...")

    login_url = "https://www.day.it/login-utilizzatori#:~:text=Accesso%20piattaforma%20unica%20per%20Buoni%20Pasto%2C%20Piattaforma%20Welfare%20e%20Buoni%20Acquisto%20Cadhoc%C2%A0"
    driver.get(login_url)

    # Attendi e clicca sul link specifico per l'accesso alla piattaforma
    try:
        # Cerca il link specifico per l'accesso alla piattaforma utilizzatori
        login_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='https://utilizzatori.day.it/day/it/login']")))

        # Forza la navigazione nello stesso tab usando JavaScript
        target_url = login_link.get_attribute('href')
        try:
            _wait_page_load(driver, target_url, "https://utilizzatori.day.it/day/it/home", timeout=120)
        except Exception as e:
            _handle_fatal_error(driver, "Timeout nel login automatico - il sito potrebbe essere lento o non raggiungibile", e)
        print(f"Navigazione completata: {driver.current_url}")
        return

    except Exception as e:
        print("Pulsante di login non trovato automaticamente. Procedi manualmente.")
        raise ReferenceError("Pulsante di login non trovato") from e


def _wait_for_manual_login(driver):
    """Attende che l'utente effettui il login manualmente"""
    print("\n" + "=" * 60)
    print("EFFETTUA IL LOGIN MANUALMENTE NEL BROWSER")
    print("Una volta loggato, premi INVIO qui per continuare...")
    print("=" * 60)

    input("Premi INVIO quando hai completato il login: ")

    if driver.current_url != "https://utilizzatori.day.it/day/it/home":
        _handle_fatal_error(driver, f"Login non completato correttamente - URL attuale: {driver.current_url}. Assicurati di essere sulla home page prima di premere INVIO")


def _navigate_to_movements(driver):
    """Naviga alla pagina dei movimenti"""
    print("Navigazione alla pagina dei movimenti...")

    movements_url = "https://utilizzatori.day.it/day/it/pausa-pranzo/monitora/movimenti"
    driver.get(movements_url)

    # Attendi che la pagina si carichi completamente
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except Exception as e:
        _handle_fatal_error(driver, "La pagina dei movimenti non si è caricata correttamente", e)

    # Gestisci automaticamente il banner dei cookie
    _handle_cookie_banner(driver)


def _set_date_filter(driver, start_date: str, end_date: str = None):
    """Imposta il filtro data e avvia la ricerca"""
    print(f"Impostazione filtro data: da {start_date} a {end_date if end_date else 'oggi'}")

    try:
        # Campo data di inizio - selettore specifico per dataDa
        start_date_field = None
        try:
            start_date_field = driver.find_element(By.ID, "dataDa")
            print("Campo data di inizio trovato con ID 'dataDa'")
        except:
            try:
                start_date_field = driver.find_element(By.CSS_SELECTOR, "input[name='dataDa']")
                print("Campo data di inizio trovato con name 'dataDa'")
            except:
                print("Campo data di inizio non trovato")

        if start_date_field:
            start_date_field.clear()
            start_date_field.send_keys(start_date)
            print(f"Data di inizio impostata: {start_date}")
        else:
            print("ERRORE: Campo data di inizio non trovato!")
            return False

        # Campo data di fine - selettore specifico per dataA (opzionale)
        if end_date:
            end_date_field = None
            try:
                end_date_field = driver.find_element(By.ID, "dataA")
                print("Campo data di fine trovato con ID 'dataA'")
            except:
                try:
                    end_date_field = driver.find_element(By.CSS_SELECTOR, "input[name='dataA']")
                    print("Campo data di fine trovato con name 'dataA'")
                except:
                    print("Campo data di fine non trovato")

            if end_date_field:
                end_date_field.clear()
                end_date_field.send_keys(end_date)
                print(f"Data di fine impostata: {end_date}")
            else:
                print("ATTENZIONE: Campo data di fine non trovato, ma continuo...")
        else:
            print("Data di fine non specificata, verrà usata la data odierna automaticamente")

        # Pulsante di ricerca - selettore specifico per btnNext
        search_button = None
        try:
            search_button = driver.find_element(By.ID, "btnNext")
            print("Pulsante di ricerca trovato con ID 'btnNext'")
        except:
            try:
                search_button = driver.find_element(By.CSS_SELECTOR, "input[name='btnNext']")
                print("Pulsante di ricerca trovato con name 'btnNext'")
            except:
                try:
                    search_button = driver.find_element(By.CSS_SELECTOR, "input[value='CERCA']")
                    print("Pulsante di ricerca trovato con value 'CERCA'")
                except:
                    print("Pulsante di ricerca non trovato")

        if search_button:
            search_button.click()
            print("Pulsante CERCA cliccato")

            # Attendi che la pagina si ricarichi e i risultati appaiano
            print("Attendo il caricamento dei risultati...")
            # time.sleep(5)

            # Verifica che la tabella dei risultati sia presente
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".wrap-table table.table tbody")))
                return
            except:
                _handle_fatal_error(driver, "I risultati non sono stati caricati correttamente dopo la ricerca")
        else:
            _handle_fatal_error(driver, "Pulsante di ricerca non trovato - impossibile procedere")

    except Exception as e:
        _handle_fatal_error(driver, "Errore nell'impostazione dei filtri", e)


def _scrape_all_pages(driver) -> List[Dict[str, Any]]:
    """Esegue lo scraping di tutte le pagine dei risultati"""
    print("Inizio scraping delle pagine...")

    all_transactions = []
    page_number = 1

    while True:
        print(f"Scraping pagina {page_number}...")

        # Estrai i dati della tabella della pagina corrente
        table_html = _extract_table_html(driver)
        if table_html:
            # Analizza l'HTML e estrae le transazioni strutturate
            page_transactions = _parse_transactions_from_html(table_html)

            # Aggiungi informazioni sulla pagina di origine
            for transaction in page_transactions:
                transaction['pagina_origine'] = page_number

            all_transactions.extend(page_transactions)
            print(f"Estratte {len(page_transactions)} transazioni dalla pagina {page_number}")

        # Controlla se ci sono altre pagine
        if not _go_to_next_page(driver):
            break

        page_number += 1

    print(f"Scraping completato. Totale transazioni estratte: {len(all_transactions)} da {page_number} pagine")

    # Stampa un riepilogo delle transazioni per debug
    if all_transactions:
        print("\n=== RIEPILOGO TRANSAZIONI ===")
        credits = [t for t in all_transactions if t['tipo_operazione'] == 'credit']
        usages = [t for t in all_transactions if t['tipo_operazione'] == 'usage']

        print(f"Accrediti: {len(credits)}")
        print(f"Utilizzi: {len(usages)}")

        total_credits = sum(t['valore'] for t in credits)
        total_usage = sum(abs(t['valore']) for t in usages)

        print(f"Totale accreditato: +{total_credits:.2f}€")
        print(f"Totale utilizzato: -{total_usage:.2f}€")
        print("=" * 30)

    return all_transactions


def _extract_table_html(driver) -> str:
    """Estrae l'HTML della tabella dei movimenti"""
    try:
        # Selettore specifico per la tabella UpDay basato sull'HTML fornito
        table_selector = ".wrap-table .table-responsive table.table"

        try:
            table = driver.find_element(By.CSS_SELECTOR, table_selector)
            html_content = table.get_attribute('outerHTML')
            return html_content
        except:
            print("Tabella principale non trovata, provo con selettori alternativi...")

            # Selettori alternativi specifici per UpDay
            alternative_selectors = [
                ".wrap-table table",
                "table.table",
                ".table-responsive table",
                "div.wrap-table > div.table-responsive > table"
            ]

            for selector in alternative_selectors:
                try:
                    table = driver.find_element(By.CSS_SELECTOR, selector)
                    html_content = table.get_attribute('outerHTML')
                    print(f"Tabella trovata con selettore alternativo '{selector}': {len(html_content)} caratteri")
                    return html_content
                except:
                    continue

            print("ERRORE: Nessuna tabella trovata con i selettori UpDay")

            # Debug: mostra tutte le tabelle presenti nella pagina
            try:
                all_tables = driver.find_elements(By.TAG_NAME, "table")
                print(f"DEBUG: Trovate {len(all_tables)} tabelle nella pagina")
                for i, table in enumerate(all_tables):
                    class_attr = table.get_attribute('class') or 'no-class'
                    print(f"  Tabella {i + 1}: class='{class_attr}'")

                # Se c'è almeno una tabella, usa la prima
                if all_tables:
                    html_content = all_tables[0].get_attribute('outerHTML')
                    print(f"Usando la prima tabella trovata: {len(html_content)} caratteri")
                    return html_content
            except Exception as debug_e:
                print(f"Errore nel debug delle tabelle: {debug_e}")

            return ""

    except Exception as e:
        print(f"Errore nell'estrazione della tabella: {e}")
        return ""


def _go_to_next_page(driver) -> bool:
    """Controlla se esiste una pagina successiva e ci naviga"""
    try:
        # Salva il numero della pagina corrente prima di fare qualsiasi operazione
        current_page_number = None
        try:
            current_active = driver.find_element(By.CSS_SELECTOR, "#pg_page li.item.active a")
            current_page_number = current_active.text.strip()
            print(f"Pagina corrente: {current_page_number}")
        except:
            print("⚠️  Non riesco a determinare la pagina corrente")

        # Cerca la paginazione con id pg_page
        pagination = driver.find_element(By.ID, "pg_page")

        # Trova tutti gli elementi li con classe item
        items = pagination.find_elements(By.CSS_SELECTOR, "li.item")

        if not items:
            print("Nessun elemento di paginazione trovato")
            return False

        # Trova l'elemento attivo
        active_item = None
        active_index = -1

        for i, item in enumerate(items):
            if "active" in item.get_attribute("class"):
                active_item = item
                active_index = i
                break

        if active_item is None:
            print("⚠️  Elemento di paginazione attivo non trovato")
            return False

        # Controlla se esiste un elemento successivo
        if active_index + 1 < len(items):
            next_item = items[active_index + 1]

            # Cerca un link nell'elemento successivo
            try:
                next_link = next_item.find_element(By.TAG_NAME, "a")
                next_page_number_text = next_link.text.strip()
                next_page_url = next_link.get_attribute('href')

                print(f"Navigazione alla pagina successiva: {next_page_number_text}")

                # Strategia 1: Prova con il click normale
                try:
                    next_link.click()
                except Exception as click_e:
                    print(f"Click normale fallito: {click_e}")
                    # Strategia 2: Usa JavaScript per il click
                    try:
                        driver.execute_script("arguments[0].click();", next_link)
                        print("Click JavaScript riuscito")
                    except Exception as js_e:
                        print(f"Click JavaScript fallito: {js_e}")
                        # Strategia 3: Naviga direttamente con l'URL
                        if next_page_url:
                            print(f"Navigazione diretta all'URL: {next_page_url}")
                            driver.get(next_page_url)
                        else:
                            print("❌ Tutte le strategie di click fallite")
                            return False

                # Attendi che la pagina si carichi con una strategia più robusta
                print("⏳ Attendo il caricamento della pagina successiva...")

                # Strategia di attesa più robusta
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        # Aspetta che la tabella sia presente (indica che la pagina è caricata)
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".wrap-table table.table tbody"))
                        )

                        # Verifica che la paginazione sia nuovamente disponibile
                        WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "#pg_page li.item.active"))
                        )

                        # Verifica che la pagina sia effettivamente cambiata
                        try:
                            new_active = driver.find_element(By.CSS_SELECTOR, "#pg_page li.item.active a")
                            new_page_number = new_active.text.strip()

                            if new_page_number == next_page_number_text:
                                print(f"✅ Navigazione riuscita alla pagina {new_page_number}")
                                return True
                            elif new_page_number != current_page_number:
                                print(f"✅ Pagina cambiata da {current_page_number} a {new_page_number}")
                                return True
                            else:
                                print(f"⚠️  Tentativo {attempt + 1}: Pagina non cambiata, riprovo...")
                                if attempt < max_attempts - 1:
                                    import time
                                    time.sleep(1)
                                    continue

                        except Exception as verify_e:
                            print(f"⚠️  Tentativo {attempt + 1}: Errore nella verifica: {verify_e}")
                            if attempt < max_attempts - 1:
                                import time
                                time.sleep(1)
                                continue

                        break

                    except Exception as wait_e:
                        print(f"⚠️  Tentativo {attempt + 1}: Timeout nell'attesa: {wait_e}")
                        if attempt < max_attempts - 1:
                            import time
                            time.sleep(2)
                            continue
                        else:
                            print("❌ Timeout definitivo nel caricamento della pagina")
                            return False

                return True

            except Exception as e:
                print(f"⚠️  Errore nella ricerca del link successivo: {e}")
                return False
        else:
            print("✅ Nessuna pagina successiva disponibile (fine paginazione)")
            return False

    except Exception as e:
        print(f"❌ Errore generale nella navigazione alla pagina successiva: {e}")
        return False


def _handle_fatal_error(driver, error_message: str, exception: Exception = None):
    """
    Gestisce errori fatali chiudendo tutto pulitamente e fornendo feedback

    Args:
        driver: Il driver Selenium da chiudere
        error_message: Messaggio di errore da mostrare all'utente
        exception: L'eccezione originale (opzionale)
    """
    print("\n" + "=" * 60)
    print("❌ ERRORE FATALE - OPERAZIONE INTERROTTA")
    print("=" * 60)
    print(f"PROBLEMA: {error_message}")

    if exception:
        print(f"DETTAGLI TECNICI: {str(exception)}")

    print("\nIl plugin si arresterà per evitare ulteriori problemi.")
    print("=" * 60)

    # Chiudi il browser se presente
    if driver:
        try:
            print("Chiusura del browser...")
            driver.quit()
        except:
            print("Browser già chiuso o non disponibile")

    # Termina l'esecuzione
    exit(1)


def _parse_transactions_from_html(html_content: str) -> List[Dict[str, Any]]:
    """
    Analizza l'HTML della tabella e estrae le informazioni delle transazioni

    Args:
        html_content: Stringa HTML della tabella

    Returns:
        Lista di dizionari con i dati delle transazioni strutturate
    """
    transactions = []

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Trova tutte le righe delle transazioni (wrap-collapse-tr)
        transaction_rows = soup.find_all('tr', class_='wrap-collapse-tr')

        for row in transaction_rows:
            try:
                # Trova la tabella interna (table-collapse) che contiene i dati della transazione
                inner_table = row.find('table', class_='table-collapse')
                if not inner_table:
                    continue

                # Trova le righe della tabella interna
                inner_rows = inner_table.find('tbody').find_all('tr')
                if len(inner_rows) < 2:
                    continue

                # Prima riga contiene i dati principali
                main_row = inner_rows[0]
                main_cells = main_row.find_all('td')

                if len(main_cells) < 4:
                    continue

                # Estrazione dati principali
                datetime_text = main_cells[0].get_text(strip=True)
                description = main_cells[1].get_text(strip=True)
                vouchers_count = main_cells[2].get_text(strip=True)
                amount_text = main_cells[3].get_text(strip=True)

                # Parsing data e ora
                date_part = None
                time_part = None
                try:
                    if ' ' in datetime_text:
                        date_part, time_part = datetime_text.split(' ', 1)
                    else:
                        date_part = datetime_text
                        time_part = "00:00"
                except:
                    date_part = datetime_text
                    time_part = "00:00"

                # Parsing dell'importo (rimuove € e converte in float)
                amount_value = None
                try:
                    # Rimuovi €, spazi e converte virgola in punto
                    clean_amount = amount_text.replace('€', '').replace(' ', '').replace(',', '.')
                    # Gestisce segno + o -
                    if clean_amount.startswith('+'):
                        amount_value = float(clean_amount[1:])
                    elif clean_amount.startswith('-'):
                        amount_value = -float(clean_amount[1:])
                    else:
                        amount_value = float(clean_amount)
                except:
                    amount_value = 0.0

                # Parsing numero buoni
                vouchers_num = None
                try:
                    vouchers_num = int(vouchers_count)
                except:
                    vouchers_num = 0

                # Seconda riga contiene i dettagli (collapse)
                details_row = inner_rows[1] if len(inner_rows) > 1 else None
                merchant_name = ""
                merchant_location = ""
                reference_code = ""

                if details_row:
                    collapse_div = details_row.find('div', class_='collapse')
                    if collapse_div:
                        # Estrai nome esercente
                        name_span = collapse_div.find('span', class_='name')
                        if name_span:
                            merchant_name = name_span.get_text(strip=True)

                        # Estrai location
                        location_span = collapse_div.find('span', class_='location')
                        if location_span:
                            merchant_location = location_span.get_text(strip=True)

                        # Estrai codice ricarica (per accrediti)
                        strong_tags = collapse_div.find_all('strong')
                        for strong in strong_tags:
                            if 'Ricarica' in strong.get_text():
                                # Il codice dovrebbe essere nel testo dopo il strong
                                parent_text = strong.parent.get_text()
                                if ':' in parent_text:
                                    reference_code = parent_text.split(':', 1)[1].strip()

                # Determina il tipo di operazione
                operation_type = "unknown"
                if "Utilizzo" in description:
                    operation_type = "usage"
                elif "Accredito" in description:
                    operation_type = "credit"

                # Crea il record della transazione
                transaction = {
                    'data': date_part,
                    'ora': time_part,
                    'numero_buoni': vouchers_num,
                    'valore': amount_value,
                    'descrizione_operazione': description,
                    'tipo_operazione': operation_type,
                    'luogo_utilizzo': merchant_name,
                    'indirizzo': merchant_location,
                    'codice_riferimento': reference_code,
                    'datetime_originale': datetime_text,
                    'importo_originale': amount_text
                }

                transactions.append(transaction)

            except Exception as e:
                print(f"Errore nel parsing di una transazione: {e}")
                continue

        print(f"Estratte {len(transactions)} transazioni dall'HTML")
        return transactions

    except Exception as e:
        print(f"Errore nel parsing dell'HTML: {e}")
        return []


def _handle_cookie_banner(driver):
    """Gestisce il banner dei cookie cliccando su 'Usa solo i cookie necessari'"""
    try:
        print("Controllo presenza banner cookie...")

        # Cerca il pulsante "Usa solo i cookie necessari"
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
        )

        print("Banner cookie trovato, clicco su 'Usa solo i cookie necessari'")
        cookie_button.click()

        # Attendi che il banner scompaia
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "CybotCookiebotDialogBodyButtonDecline"))
        )

        print("Banner cookie chiuso con successo")
        return True

    except Exception as e:
        print(f"Banner cookie non trovato o già gestito: {e}")
        return False


def scrapeInfoFromWeb(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Esegue il web scraping del sito UpDay per estrarre le transazioni

    Args:
        start_date: Data di inizio nel formato gg/mm/aaaa

    Returns:
        Lista di dizionari contenenti i dati delle tabelle estratte
    """
    driver = None
    table_data = []

    try:
        print("=== INIZIO SCRAPING UPDAY ===")

        # Setup browser
        driver = _setup_browser()

        # Navigazione e login
        try:
            _navigate_to_login(driver)
        except ReferenceError:
            _wait_for_manual_login(driver)
        # Start automatic scraping after login
        _navigate_to_movements(driver)
        # Impostazione filtri e scraping
        _set_date_filter(driver, start_date, end_date)
        table_data = _scrape_all_pages(driver)

        print(f"=== SCRAPING COMPLETATO: {len(table_data)} pagine elaborate ===")
        return table_data

    except Exception as e:
        print(f"Errore durante il web scraping: {e}")
        return []
    finally:
        if driver:
            print("Chiusura del browser...")
            driver.quit()


def sanitize_filename(filename: str) -> str:
    """Sanitizza il nome del file rimuovendo caratteri non validi"""
    # Rimuovi l'estensione se presente
    if '.' in filename:
        filename = filename.rsplit('.', 1)[0]
    # Mantieni solo caratteri alfanumerici, spazi, trattini e slash
    filename = re.sub(r'[^\w\s\-/]', '', filename)
    # Sostituisci spazi con underscore
    filename = filename.replace(' ', '_')
    # Se il nome è vuoto dopo la sanitizzazione, usa la data odierna
    if not filename.strip():
        filename = date.today().strftime("%Y-%m-%d_upday")
    # Aggiungi sempre l'estensione .csv
    return f"{filename}.csv"


def save_transactions_to_csv(transactions: List[Dict[str, Any]], filename: str) -> bool:
    """
    Salva le transazioni in un file CSV

    Args:
        transactions: Lista delle transazioni estratte
        filename: Nome del file CSV dove salvare

    Returns:
        True se salvato con successo, False altrimenti
    """
    try:
        if not transactions:
            print("⚠️  Nessuna transazione da salvare")
            return False

        # Definisci le colonne del CSV nell'ordine desiderato
        fieldnames = [
            'data',
            'ora',
            'descrizione_operazione',
            'tipo_operazione',
            'numero_buoni',
            'valore',
            'luogo_utilizzo',
            'indirizzo',
            'codice_riferimento',
            'pagina_origine'
        ]

        # Crea la directory se non esiste
        directory = os.path.dirname(filename) if os.path.dirname(filename) else '.'
        os.makedirs(directory, exist_ok=True)

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Scrivi l'header
            writer.writeheader()

            # Scrivi i dati delle transazioni
            for transaction in transactions:
                # Filtra solo i campi che vogliamo nel CSV
                filtered_transaction = {key: transaction.get(key, '') for key in fieldnames}
                writer.writerow(filtered_transaction)

        print(f"✅ File CSV salvato con successo: {filename}")
        print(f"📊 Transazioni salvate: {len(transactions)}")

        # Mostra statistiche del file salvato
        file_size = os.path.getsize(filename)
        print(f"📁 Dimensione file: {file_size} bytes")

        return True

    except Exception as e:
        print(f"❌ Errore nel salvataggio del file CSV: {e}")
        return False


# ============================================================================
# OFXSTATEMENT PLUGIN CLASSES
# ============================================================================


class UpDayPlugin(Plugin):
    """UpDay Buoni Pasto plugin - scrapes data from day.it website"""

    def get_parser(self, filename: str) -> "UpDayParser":
        """Main entry point for parsers - performs web scraping and parsing"""
        if filename == "-":
            # Richiedi la data di inizio all'utente
            start_date = _get_date_from_user("inizio")
            end_date = _get_date_from_user("fine [se vuoto, usa oggi]", optional=True)
            print(f"Date selezionate: da '{start_date}' a '{end_date if end_date else 'oggi'}'")

            # Esegui il web scraping
            transactions_data = scrapeInfoFromWeb(start_date, end_date)

            # Chiedi il nome del file e sanitizzalo
            raw_filename = input("Inserisci il nome del file csv dove salvare questa estrazione automatica (se vuoto verrà usata la data odierna): ").strip()
            filename = sanitize_filename(raw_filename)
            print(f"Nome file sanitizzato: {filename}")

            # Salva i dati nel file CSV
            if save_transactions_to_csv(transactions_data, filename):
                print(f"\n🎉 Estrazione completata con successo!")
                print(f"📄 File salvato: {filename}")
                print(f"📍 Percorso completo: {os.path.abspath(filename)}")
            else:
                print("❌ Errore nel salvataggio del file")
                exit(1)
        f = open(filename, 'r', encoding=self.settings.get("charset", "UTF-8"))
        default_account = self.settings.get("default_account")
        return UpDayParser(f, default_account)


class UpDayParser(CsvStatementParser):
    """Parser per i file CSV di UpDay - converte in formato OFX"""

    date_format = "%d/%m/%Y"

    # Csv column names
    columns = ["data", "ora", "descrizione_operazione", "tipo_operazione", "numero_buoni", "valore", "luogo_utilizzo", "indirizzo", "codice_riferimento", "pagina_origine"]

    mappings = {
        'date': 'data',
        'memo': 'descrizione_operazione',
        'amount': 'valore'
    }

    def __init__(self, csv_file: TextIOWrapper, account_id: str) -> None:
        super().__init__(csv_file)
        self.statement.account_id = account_id

    def parse(self) -> Statement:
        """Parse del file CSV e creazione dello statement OFX"""
        stmt = super().parse()

        # Imposta informazioni account da configurazione
        stmt.currency = 'EUR'
        stmt.bank_id = 'UPDAY'

        return stmt

    def split_records(self) -> Iterable[str]:
        """Return iterable object consisting of a line per transaction"""

        reader = csv.reader(self.fin, delimiter=',')
        next(reader, None)
        return reader

    def parse_record(self, line: str) -> StatementLine:
        """Parse della singola riga CSV """

        row_dict = dict(zip(self.columns, line))

        # Crea oggetto StatementLine
        stmt_line = StatementLine()

        # Parse data
        try:
            parsed_date = datetime.strptime(row_dict['data'], self.date_format)
            stmt_line.date = parsed_date  # Passa datetime completo, non solo date
        except (ValueError, KeyError):
            return StatementLine()  # Ritorna StatementLine vuoto invece di None

        # Parse importo usando Decimal per compatibilità OFX
        try:
            stmt_line.amount = Decimal(str(row_dict['valore']))
        except (ValueError, KeyError):
            stmt_line.amount = Decimal('0.0')

        # Crea ID unico per la transazione
        date_str = row_dict.get('data', '')
        time_str = row_dict.get('ora', '')
        amount_str = row_dict.get('valore', '')
        ref_code = row_dict.get('codice_riferimento', '')

        # ID basato su data, ora, importo e codice riferimento
        unique_id = re.sub(r'[\/: ,\.]', '', f"{date_str}_{time_str}_{amount_str}_{ref_code}")
        stmt_line.id = unique_id

        # Determina il tipo di operazione per personalizzare il memo
        tipo_op = row_dict.get('tipo_operazione', '')

        if tipo_op == 'credit':
            # MEMO PER ACCREDITI - stile specifico con mese di assegnazione
            try:
                # Estrai il mese dalla data per determinare il mese di assegnazione
                parsed_date = datetime.strptime(row_dict['data'], self.date_format)
                mese_nomi = {
                    1: 'Gennaio', 2: 'Febbraio', 3: 'Marzo', 4: 'Aprile',
                    5: 'Maggio', 6: 'Giugno', 7: 'Luglio', 8: 'Agosto',
                    9: 'Settembre', 10: 'Ottobre', 11: 'Novembre', 12: 'Dicembre'
                }
                mese_nome = mese_nomi.get(parsed_date.month, 'Sconosciuto')

                # Numero buoni accreditati
                num_buoni = row_dict.get('numero_buoni', '0')
                if num_buoni and num_buoni != '0':
                    stmt_line.memo = f"Buoni pasto assegnati per il mese di {mese_nome} (+{num_buoni})"
                else:
                    stmt_line.memo = f"Buoni pasto assegnati per il mese di {mese_nome}"

                # Aggiungi codice riferimento se disponibile
                if row_dict.get('codice_riferimento'):
                    stmt_line.memo += f" - Cod.Rif: {row_dict['codice_riferimento']}"

            except:
                # Fallback se c'è un errore nel parsing della data
                stmt_line.memo = row_dict.get('descrizione_operazione', 'Accredito Buoni')
                if row_dict.get('numero_buoni') and row_dict.get('numero_buoni') != '0':
                    stmt_line.memo += f" (+{row_dict['numero_buoni']})"

            stmt_line.trntype = 'DEP'

        elif tipo_op == 'usage':
            # MEMO PER UTILIZZI - stile come negli acquisti con luogo e orario
            memo_parts = []

            # Nome esercente se disponibile
            luogo = row_dict.get('luogo_utilizzo', '').strip()
            if luogo:
                memo_parts.append(f"Spesa al {luogo}")
            else:
                memo_parts.append("Spesa")

            # Numero buoni utilizzati
            num_buoni = row_dict.get('numero_buoni', '0')
            if num_buoni and num_buoni != '0':
                try:
                    buoni_int = int(num_buoni)
                    if buoni_int == 1:
                        memo_parts.append(f"{buoni_int} buono pasto")
                    else:
                        memo_parts.append(f"{buoni_int} buoni pasto")
                except ValueError:
                    pass

            # Aggiungi indirizzo se disponibile
            if row_dict.get('indirizzo'):
                memo_parts.append(f"({row_dict['indirizzo']})")

            # Aggiungi ora se significativa (non 00:00)
            if row_dict.get('ora') and row_dict['ora'] != '00:00':
                memo_parts.append(f"ore {row_dict['ora']}")

            stmt_line.memo = ' - '.join(memo_parts)
            stmt_line.trntype = 'PAYMENT'

        else:
            # Fallback per tipi di operazione sconosciuti
            stmt_line.memo = row_dict.get('descrizione_operazione', 'Transazione')
            stmt_line.trntype = 'OTHER'

        return stmt_line
