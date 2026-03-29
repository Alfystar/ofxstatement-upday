# Plugin UpDay per ofxstatement

Questo plugin per ofxstatement permette di importare automaticamente le transazioni dei buoni pasto UpDay dal sito day.it e convertirle nel formato OFX compatibile con software di contabilità come GnuCash.

[ofxstatement](https://github.com/kedder/ofxstatement) è uno strumento per convertire estratti conto proprietari nel formato OFX standard.

## Descrizione

UpDay è un'azienda italiana che si occupa della gestione di buoni pasto aziendali. Questo plugin automatizza il processo di estrazione e conversione dei movimenti dal portale web utilizzatori.day.it.

### **Funzionalità principali:**

- **Download automatico** tramite web scraping del sito utilizzatori.day.it (comando `upday-download`)
- **Salvataggio CSV** per modifiche offline e riesportazioni successive
- **Conversione OFX** compatibile con software di contabilità (plugin ofxstatement)
- **Gestione automatica** della paginazione e navigazione del sito
- **Validazione date** con controllo del limite di 1 anno del sito
- **Workflow in 2 fasi** per separare download e conversione

### **Perché il web scraping?**

Al momento UpDay non fornisce un sistema di esportazione diretta dei dati tramite file o API. Il web scraping è stato implementato come soluzione temporanea in attesa che l'azienda introduca metodi di esportazione più convenienti per gli utenti.

## Requisiti di Sistema

### **Requisiti Obbligatori:**

- **Python 3.9 o superiore**
- **Google Chrome** installato e aggiornato all'ultima versione (solo per il download da web)
- **Account UpDay attivo** su day.it (solo per il download da web)
- **Connessione internet** per il web scraping (solo fase di download)

### **Gestione del driver browser (Automatica):**

Il comando `upday-download` usa **Selenium Manager** (integrato in Selenium) per trovare o scaricare automaticamente il driver compatibile con la versione di Chrome installata.

- ✅ **Nessun path manuale** da configurare nel codice
- ✅ **Cache automatica** del driver per gli avvii successivi
- ⚠️ **Al primo utilizzo** può servire connessione internet
- ⚠️ **Firewall aziendali, proxy o policy di sicurezza** possono bloccare il download automatico

Se il download automatico fallisce, il programma mostra indicazioni diagnostiche e puoi comunque ricorrere a un'installazione manuale come soluzione di emergenza.

### **Quando l'installazione automatica può fallire:**

- **Firewall aziendali** che bloccano il download
- **Politiche di sicurezza** che impediscono l'esecuzione di binari scaricati
- **Connessione internet assente** durante il primo utilizzo
- **Permessi insufficienti** per scrivere nella cache
- **Versioni di Chrome non supportate**

## Installazione

### Installazione Semplice (Raccomandata)

```bash
pip install ofxstatement-upday
```

Questa installazione include:
- Il comando `upday-download` per scaricare i dati dal web
- Il plugin `upday` per ofxstatement per convertire CSV in OFX
- Tutte le dipendenze necessarie

## Configurazione

Per modificare il file di configurazione, esegui:

```bash
ofxstatement edit-config
```

Si aprirà un editor vim con la configurazione attuale. Aggiungi la configurazione del plugin:

```ini
[upday]
plugin = upday
account = UPDAY_BUONI_PASTO
```

### **Parametri di configurazione:**

- `upday`: Nome della configurazione (puoi cambiarlo come preferisci)
- `plugin`: Deve essere sempre "upday"
- `account`: Nome dell'account per identificare le transazioni (default: UPDAY_BUONI_PASTO)

> **Nota**: Puoi avere multiple configurazioni, basta aggiungere nuove sezioni con nomi diversi.

## Utilizzo

Il plugin ora funziona in **2 fasi separate** per maggiore flessibilità:

### 🌐 **FASE 1: Download dei dati da web**

Usa il comando `upday-download` per scaricare i dati dal sito UpDay e salvarli in CSV:

```bash
upday-download
```

**Cosa succede:**
1. Il comando avvia automaticamente Chrome
2. Ti chiede di inserire le date di inizio e fine
3. Esegue il login automatico (o ti chiede di farlo manualmente se necessario)
4. Scarica automaticamente tutte le transazioni dal sito UpDay
5. Ti chiede il nome del file CSV dove salvare i dati
6. Salva i dati nel file CSV specificato

**Requisiti per questa fase:**
- ✅ Connessione internet attiva
- ✅ Google Chrome funzionante
- ✅ Selenium Manager in grado di risolvere il driver compatibile
- ✅ Account UpDay valido

**Output:** Un file CSV con tutte le transazioni estratte

### 📊 **FASE 2: Conversione CSV → OFX**

Usa ofxstatement per convertire il file CSV in formato OFX:

```bash
ofxstatement convert -t upday movimenti.csv upday.ofx
```

**Cosa succede:**
1. Il plugin legge il file CSV
2. Converte i dati nel formato OFX standard
3. Salva il file OFX pronto per l'importazione

**Requisiti per questa fase:**
- ✅ Solo il file CSV (ottenuto dalla Fase 1)
- ❌ Nessuna connessione internet necessaria
- ❌ Nessun browser necessario

**Output:** Un file OFX pronto per GnuCash o altri software di contabilità

### 🎯 **Esempio Completo: Workflow in 2 Fasi**

```bash
# FASE 1: Scarica i dati da web
$ upday-download
Inserisci la data di inizio (formato gg/mm/aaaa): 01/09/2024
Inserisci la data di fine [se vuoto, usa oggi]: 30/09/2024
...
[il browser si apre e scarica i dati]
...
Inserisci il nome del file csv: settembre_2024
📄 File salvato: settembre_2024.csv

# FASE 2: Converti il CSV in OFX
$ ofxstatement convert -t upday settembre_2024.csv settembre_2024.ofx
✅ Conversione completata: settembre_2024.ofx
```

### 💡 **Vantaggi del Workflow in 2 Fasi**

- **✅ Modifiche manuali**: Puoi modificare il CSV prima della conversione
- **✅ Riconversioni**: Puoi riconvertire lo stesso CSV più volte senza riscaricare
- **✅ Backup**: Hai sempre una copia dei dati grezzi in CSV
- **✅ Offline**: La conversione funziona anche senza internet
- **✅ Automazione**: Puoi automatizzare solo la fase di conversione negli script

### 🔄 **Workflow Automatizzato**

Per automatizzare entrambe le fasi in un unico script:

```bash
#!/bin/bash
# download_and_convert.sh

# Scarica i dati (interattivo)
upday-download

# Converti l'ultimo file CSV creato
ULTIMO_CSV=$(ls -t *.csv 2>/dev/null | head -1)
if [ -n "$ULTIMO_CSV" ]; then
    OUTPUT_OFX="${ULTIMO_CSV%.csv}.ofx"
    ofxstatement convert -t upday "$ULTIMO_CSV" "$OUTPUT_OFX"
    echo "✅ Conversione completata: $OUTPUT_OFX"
else
    echo "❌ Nessun file CSV trovato"
fi
```

### 📝 **Formato del File CSV**

Il file CSV generato da `upday-download` ha questa struttura:

```csv
data,ora,descrizione_operazione,tipo_operazione,numero_buoni,valore,luogo_utilizzo,indirizzo,codice_riferimento,pagina_origine
01/09/2024,12:30,Utilizzo buoni pasto,usage,1,-8.00,BAR CENTRALE,VIA ROMA 1 - MILANO,,1
05/09/2024,00:00,Accredito buoni pasto,credit,20,160.00,,,ABC123,1
```

Puoi modificare questo file manualmente prima della conversione in OFX.

## Privacy e Sicurezza

- **Nessuna memorizzazione credenziali**: Il plugin non salva username o password
- **Solo lettura**: Accede solo in lettura ai dati delle transazioni
- **Locale**: Tutti i dati vengono elaborati localmente sul tuo computer
- **Open source**: Il codice è ispezionabile su GitHub
- **Separazione dei compiti**: Download e conversione sono separati per maggiore controllo

## Installazione Manuale di ChromeDriver

<details>
<summary>Clicca per vedere le istruzioni per l'installazione manuale</summary>

Normalmente **non serve** installare ChromeDriver manualmente.

Questa sezione è utile solo come workaround se Selenium Manager non riesce a scaricare o riutilizzare automaticamente il driver corretto.

#### macOS:
```bash
# Con Homebrew (raccomandato)
brew install chromedriver

# Rimuovi quarantena macOS
xattr -d com.apple.quarantine $(which chromedriver)

# Verifica installazione
chromedriver --version
```

#### Linux Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver

# Verifica installazione
chromedriver --version
```

#### Linux altre distribuzioni:
```bash
# Scarica ChromeDriver compatibile con la tua versione di Chrome
wget https://chromedriver.chromium.org/downloads
# Estrai e sposta in /usr/bin/
sudo mv chromedriver /usr/bin/
sudo chmod +x /usr/bin/chromedriver
```

#### Windows:
1. Scarica ChromeDriver da https://chromedriver.chromium.org
2. Estrai il file `chromedriver.exe`
3. Aggiungi la cartella al PATH di sistema
4. Verifica: apri cmd e digita `chromedriver --version`

</details>

## Troubleshooting

### Il comando `upday-download` non viene trovato

Dopo l'installazione, potrebbe essere necessario riavviare il terminale o ricaricare la configurazione:

```bash
# Bash
source ~/.bashrc

# Zsh
source ~/.zshrc
```

Se il problema persiste, verifica che pip installi i binari in una directory nel PATH:

```bash
pip show ofxstatement-upday
```

### Errore "File non trovato" durante la conversione

Assicurati di:
1. Aver eseguito prima `upday-download`
2. Specificare il percorso corretto del file CSV
3. Essere nella directory corretta

```bash
# Verifica che il file esista
ls -la *.csv

# Usa il percorso assoluto se necessario
ofxstatement convert -t upday /path/completo/file.csv output.ofx
```

### Il download automatico del driver non funziona su macOS

macOS Gatekeeper può bloccare i binari scaricati automaticamente. Se necessario, prova con:

```bash
xattr -d com.apple.quarantine $(which chromedriver)
```

## Sviluppo

<details>
<summary>Installazione da sorgenti per sviluppatori</summary>

```bash
git clone https://github.com/Alfystar/ofxstatement-upday.git
cd ofxstatement-upday
pip install -e .
```

</details>

### Test automatici

Il progetto include **3 file di test** che coprono plugin, parser e download/browser setup.

#### `tests/test_sample.py`

Serve come **smoke test end-to-end minimale** del plugin OFX:

- crea un CSV temporaneo di esempio
- istanzia `UpDayPlugin`
- verifica che il parsing produca uno statement valido
- controlla che una transazione di utilizzo venga mappata come `PAYMENT`

È utile quando vuoi verificare rapidamente che il workflow **CSV → parser → statement OFX** sia ancora integro.

#### `tests/test_upday.py`

Copre la logica principale del plugin e del parser:

- creazione di `UpDayPlugin`
- restituzione corretta del parser da `get_parser`
- parsing della data utente in `get_date_from_user`
- gestione di input invalidi seguiti da input validi
- parsing di una riga CSV di utilizzo in `UpDayParser.parse_record`

È il test più utile quando modifichi la logica di conversione **CSV → OFX** o la validazione delle date.

#### `tests/test_download.py`

Copre la parte introdotta per il download/browser setup:

- sanitizzazione del nome file CSV con `sanitize_filename`
- avvio del browser tramite `Selenium Manager` usando mock di `webdriver.Chrome`
- gestione dell'errore fatale quando Selenium non riesce ad avviare Chrome

È il test più importante quando tocchi `src/ofxstatement_upday/download.py` o la logica di inizializzazione del browser.

### Come eseguire i test

Esegui tutta la suite:

```bash
pipenv run pytest -q
```

Oppure usa il `Makefile`:

```bash
make test
```

Esegui un singolo file di test:

```bash
pipenv run pytest tests/test_sample.py -q
pipenv run pytest tests/test_upday.py -q
pipenv run pytest tests/test_download.py -q
```

Esegui un singolo test specifico:

```bash
pipenv run pytest tests/test_download.py::test_setup_browser_uses_selenium_manager -q
```

### Build e pubblicazione

Per preparare e pubblicare una nuova release su PyPI:

```bash
rm -rf dist build *.egg-info src/*.egg-info
pipenv run pytest -q
pipenv run python -m build
pipenv run twine check dist/*
pipenv run twine upload dist/*
```

Se vuoi pubblicare prima su TestPyPI:

```bash
pipenv run twine upload --repository testpypi dist/*
```

## Licenza

GPLv3 - Vedi il file LICENSE per i dettagli

## Contributi

I contributi sono benvenuti! Per favore apri una issue o una pull request su GitHub.

## Changelog

### v1.2.0
- ✨ **BREAKING CHANGE**: Separazione in 2 comandi distinti
  - `upday-download`: per scaricare i dati da web
  - Plugin ofxstatement: per convertire CSV in OFX
- ✅ Gestione driver browser demandata a Selenium Manager
- ✅ Test automatici aggiornati e documentati
- ✅ Workflow più flessibile e manutenibile
- ✅ Possibilità di modificare il CSV prima della conversione
- ✅ Conversione offline senza bisogno di browser

### v1.0.1
- Gestione automatica ChromeDriver
- Login automatico migliorato
- Validazione date

## Sheet cheat per deployment

```bash
cd "./ofxstatement-upday"
rm -rf dist build *.egg-info src/*.egg-info
pipenv sync --dev
pipenv run pytest -q
pipenv run python -m build
pipenv run twine check dist/*
pipenv run twine upload dist/*
```

Per aggiornare sui sistemi target:

```bash
pip install --upgrade ofxstatement-upday
upday-download --version # per verificare che sia aggiornata
```


## Autore

Alfystar - alfystar1701@gmail.com

## Link Utili

- [Repository GitHub](https://github.com/Alfystar/ofxstatement-upday)
- [Segnala un problema](https://github.com/Alfystar/ofxstatement-upday/issues)
- [Documentazione ofxstatement](https://github.com/kedder/ofxstatement)
