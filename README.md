# Plugin UpDay per ofxstatement

Questo plugin per ofxstatement permette di importare automaticamente le transazioni dei buoni pasto UpDay dal sito day.it e convertirle nel formato OFX compatibile con software di contabilità come GnuCash.

[ofxstatement](https://github.com/kedder/ofxstatement) è uno strumento per convertire estratti conto proprietari nel formato OFX standard.

## Descrizione

UpDay è un'azienda italiana che si occupa della gestione di buoni pasto aziendali. Questo plugin automatizza il processo di estrazione e conversione dei movimenti dal portale web utilizzatori.day.it.

### **Funzionalità principali:**

- **Download automatico** tramite web scraping del sito utilizzatori.day.it
- **Salvataggio CSV** per modifiche offline e riesportazioni successive
- **Conversione OFX** compatibile con software di contabilità
- **Gestione automatica** della paginazione e navigazione del sito
- **Validazione date** con controllo del limite di 1 anno del sito

### **Perché il web scraping?**

Al momento UpDay non fornisce un sistema di esportazione diretta dei dati tramite file o API. Il web scraping è stato implementato come soluzione temporanea in attesa che l'azienda introduca metodi di esportazione più convenienti per gli utenti.

## Requisiti di Sistema

### **Requisiti Obbligatori:**

- **Python 3.9 o superiore**
- **Google Chrome** installato e aggiornato all'ultima versione
- **Account UpDay attivo** su day.it
- **Connessione internet** per il web scraping

### **Gestione ChromeDriver (Automatica):**

Il plugin gestisce automaticamente ChromeDriver con una strategia intelligente:

1. **🔍 Prima priorità**: Cerca ChromeDriver già installato localmente
   - Homebrew (macOS): `/opt/homebrew/bin/chromedriver` o `/usr/local/bin/chromedriver`
   - Sistema Linux: `/usr/bin/chromedriver`
   - PATH di sistema: comando `chromedriver`

2. **🌐 Fallback automatico**: Se ChromeDriver non è trovato localmente, tenta il download automatico
   - ⚠️ **Richiede connessione internet**
   - ⚠️ **Può fallire** per restrizioni di sistema, firewall aziendali, o politiche di sicurezza
   - ✅ **Una volta scaricato**, viene memorizzato in cache per utilizzi futuri

3. **🚨 Se il download automatico fallisce**: Il plugin fornisce istruzioni dettagliate per l'installazione manuale

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

Questa installazione include tutte le dipendenze necessarie, incluso il sistema di gestione automatica di Chrome (per scraping automatico).

## Configurazione

Per modificare il file di configurazione, esegui:

```bash
ofxstatement edit-config
```

Si aprirà un editor vim con la configurazione attuale. Aggiungi la configurazione del plugin:

```ini
[upday-config]
plugin = upday
default_account = UPDAY_BUONI_PASTO
browser = chrome
```

### **Parametri di configurazione:**

- `upday-config`: Nome della configurazione, selezionata dall'opzione `-t upday-config`, puoi cambiarlo come preferisci e averne più di una, ma ogni una di esse deve essere univoca
- `plugin`: Deve essere sempre "upday"
- `account`: Nome dell'account per identificare le transazioni (default: UPDAY_BUONI_PASTO)
- `browser`: Browser da utilizzare (attualmente supportato solo "chrome")

> **Nota**: Puoi avere tutte le configurazioni che desideri, basta aggiungere una nuova sezione con la stessa struttura e cambiare il nome della sezione.

### Utilizzo in Script

```bash
# Per download automatico e conversione
ofxstatement convert -t upday-config - upday.ofx
# Per automazione, usa file CSV già esistenti
ofxstatement convert -t upday-config movimento_upday.csv output.ofx
```

### Aggiungere un alias

Per semplificare l'uso del plugin, si consiglia di aggiungere un alias al sistema aggiungendo questo comando al file *.bash_aliases*:

```bash
printf '\n# UpDay CSV convert to OFX format\nalias ofxUpday="ofxstatement convert -t upday"\n' >> ~/.bash_aliases
```

Dopo aver ricaricato il terminale, l'utilizzo diventa:

```bash
# Per download automatico e conversione
ofxUpday - upday.ofx
# Per automazione, usa file CSV già esistenti
ofxUpday estratto_upday.csv upday.ofx
```

**Nota**: Se dopo il ricaricamento gli alias non vengono caricati, verifica che nel tuo *.bashrc* siano presenti le seguenti righe:

```bash
# Alias definitions.
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
```

## Privacy e Sicurezza

- **Nessuna memorizzazione credenziali**: Il plugin non salva username o password
- **Solo lettura**: Accede solo in lettura ai dati delle transazioni
- **Locale**: Tutti i dati vengono elaborati localmente sul tuo computer
- **Open source**: Il codice è ispezionabile su GitHub

<details>
<summary>Installazione manuale di ChromeDriver (se il download automatico fallisce)</summary>

Per evitare dipendenze dalla connessione internet e garantire massima affidabilità:

#### macOS:
```bash
# Con Homebrew (raccomandato)
brew install chromedriver

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

<details>
<summary>Da sorgenti (per sviluppatori)</summary>

```bash
git clone https://github.com/Alfystar/ofxstatement-upday.git
cd ofxstatement-upday
pip install -e .
```

</details>

## Utilizzo

Il plugin supporta **due modalità di utilizzo**:

### 🌐 **Modalità 1: Download Automatico** (raccomandato)

Usa il carattere speciale `-` come nome del file di input per attivare il **web scraping automatico**:

```bash
ofxUpDay - output.ofx
```

**Cosa succede:**
1. Il plugin avvia automaticamente Chrome
2. Ti chiede di inserire le date di inizio e fine
3. Esegue il login automatico (o ti chiede di farlo manualmente)
4. Scarica automaticamente tutte le transazioni dal sito UpDay
5. Salva i dati in un file CSV intermedio
6. Converte il CSV in formato OFX

**Requisiti:**
- Connessione internet attiva
- Chrome e ChromeDriver funzionanti
- Account UpDay valido

### 📁 **Modalità 2: Solo Conversione** (per file esistenti)

Usa un file CSV esistente (scaricato precedentemente) per **solo convertire** in OFX:

```bash
ofxUpDay movimento_upday.csv output.ofx
```

**Cosa succede:**
1. Il plugin legge direttamente il file CSV fornito
2. Converte i dati dal CSV al formato OFX
3. Non richiede connessione internet o browser

**Requisiti:**
- Solo il file CSV con il formato corretto
- Nessuna connessione internet necessaria

### Esempio Completo: Download Automatico

<details>
<summary>Log di esempio</summary>

```bash
$ ofxUpDay - upday_ottobre_2024.ofx
Inserisci la data di inizio (formato gg/mm/aaaa): 01/10/2024
Inserisci la data di fine [se vuoto, usa oggi]: 31/10/2024
Date selezionate: da '01/10/2024' a '31/10/2024'

🚀 Avvio del browser...
  • 🔍 Tentativo 1: Uso ChromeDriver predefinito di sistema
    ◦ 🎉 Browser avviato con successo usando ChromeDriver predefinito

🔐 Navigazione alla pagina di login
  • Reindirizzamento automatico alla home page
    ◦ ✅ Navigazione completata: https://utilizzatori.day.it/day/it/home

📄 Inizio scraping delle pagine
  • Scraping pagina 1
    ◦ ✅ Estratte 15 transazioni dalla pagina 1
  • Scraping pagina 2
    ◦ ✅ Estratte 12 transazioni dalla pagina 2

✅ Scraping completato. Totale transazioni estratte: 27 da 2 pagine

Inserisci il nome del file csv: ottobre_2024_upday
📊 Transazioni salvate: 27
🎉 Estrazione completata con successo!
```

</details>

### Esempio Completo: Solo Conversione

```bash
$ ofxUpDay ottobre_2024_upday.csv output.ofx
INFO: Conversion completed: (27 lines, 0 invest-lines) -
```

### Formati Date Supportati

Il plugin riconosce automaticamente diversi formati di data:
- `01/10/2024`, `1/10/24` (formato standard)
- `01-10-2024`, `1-10-24` (con trattini)
- `01.10.2024`, `1.10.24` (con punti)

## Risoluzione Problemi

### Errore "ChromeDriver non trovato"

Se vedi questo errore, il plugin non è riuscito a trovare o scaricare ChromeDriver:

```
🚨 Impossibile avviare Chrome - ChromeDriver non trovato
```

**Soluzioni in ordine di priorità:**

1. **Installa ChromeDriver manualmente** (vedi sezione installazione sopra)
2. **Verifica che Chrome sia aggiornato**: Menu → Aiuto → Informazioni su Google Chrome
3. **Controlla la connessione internet** per il download automatico
4. **Se sei in ambiente aziendale**: Chiedi all'IT di installare ChromeDriver o sbloccare i download

### Errore di connessione al sito

Se il plugin non riesce a connettersi al sito UpDay:

- Verifica che il sito utilizzatori.day.it sia accessibile dal tuo browser
- Controlla eventuali VPN o proxy che potrebbero interferire
- Riprova più tardi se il sito è temporaneamente non disponibile

### Browser che si chiude improvvisamente

- Assicurati di avere l'ultima versione di Chrome installata
- Su macOS, potresti dover autorizzare ChromeDriver: `xattr -d com.apple.quarantine /path/to/chromedriver`
- Controlla che non ci siano altri processi Chrome in esecuzione

### Problemi con file CSV esistenti

Se hai problemi nella conversione di file CSV già scaricati:

- Verifica che il file CSV sia nel formato corretto (vedi sezione formato)
- Assicurati che il file non sia corrotto o modificato manualmente
- Prova a riscaricare i dati usando la modalità download automatico

## Formato File CSV

Il plugin genera e legge file CSV con questo formato:

```csv
data,ora,descrizione_operazione,tipo_operazione,numero_buoni,valore,luogo_utilizzo,indirizzo,codice_riferimento,pagina_origine
01/10/2024,12:30,Utilizzo Buoni Pasto,usage,2,-11.00,CONAD SUPERSTORE,Via Roma 123,,-1
03/10/2024,00:00,Accredito Buoni Pasto,credit,20,110.00,,,REF123456,1
```

**Colonne:**
- `data`: Data della transazione (gg/mm/aaaa)
- `ora`: Ora della transazione (hh:mm)
- `descrizione_operazione`: Descrizione dal sito UpDay
- `tipo_operazione`: `credit` (accredito) o `usage` (utilizzo)
- `numero_buoni`: Numero di buoni coinvolti
- `valore`: Importo in euro (positivo per accrediti, negativo per utilizzi)
- `luogo_utilizzo`: Nome dell'esercente (solo per utilizzi)
- `indirizzo`: Indirizzo dell'esercente (solo per utilizzi)
- `codice_riferimento`: Codice di riferimento (solo per accrediti)
- `pagina_origine`: Numero di pagina da cui è stata estratta


## Limitazioni Conosciute

- **Limite temporale**: Il sito UpDay permette l'accesso solo agli ultimi 12 mesi di dati
- **Dipendenza browser**: La modalità download automatico richiede Google Chrome
- **Rate limiting**: Uso eccessivo potrebbe causare blocchi temporanei dal sito
- **Cambio sito**: Aggiornamenti del sito UpDay potrebbero richiedere aggiornamenti del plugin

## Contributi

I contributi sono benvenuti! Per segnalare bug o proporre miglioramenti:

1. Apri una [issue](https://github.com/Alfystar/ofxstatement-upday/issues) su GitHub
2. Fork del repository e pull request per le modifiche
3. Segnala problemi con il sito UpDay per aggiornamenti necessari

## Licenza

Questo progetto è distribuito sotto licenza GPLv3. Vedi il file `LICENSE` per i dettagli.
