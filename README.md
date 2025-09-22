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

Questa installazione include tutte le dipendenze necessarie, incluso il sistema di gestione automatica di ChromeDriver.

### Installazione ChromeDriver Manuale (Opzionale ma Raccomandata)

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

### Da sorgenti (per sviluppatori)

```bash
git clone https://github.com/Alfystar/ofxstatement-upday.git
cd ofxstatement-upday
pip install -e .
```

## Utilizzo

### Comando Base

```bash
ofxUpDay - output.ofx
```

Il plugin ti guiderà attraverso:
1. **Inserimento date** di inizio e fine
2. **Avvio automatico** del browser Chrome
3. **Login manuale** sul sito UpDay (quando necessario)
4. **Estrazione automatica** di tutte le transazioni
5. **Salvataggio** in formato CSV e conversione OFX

### Esempio Completo

```bash
$ ofxUpDay - upday_settembre_2024.ofx
Inserisci la data di inizio (formato gg/mm/aaaa): 01/09/2024
Inserisci la data di fine [se vuoto, usa oggi]: 30/09/2024
Date selezionate: da '01/09/2024' a '30/09/2024'

=== INIZIO SCRAPING UPDAY ===
🔍 Tentativo 1: Ricerca ChromeDriver già installato nel sistema...
✅ Trovato ChromeDriver in: /opt/homebrew/bin/chromedriver
🎉 Browser avviato con successo usando ChromeDriver locale

[... processo di scraping ...]

✅ File CSV salvato con successo: settembre_upday.csv
📊 Transazioni salvate: 42
🎉 Estrazione completata con successo!
```

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

## Configurazione Avanzata

### Personalizzazione Account

Crea un file di configurazione per evitare di inserire l'account ogni volta:

```ini
# ~/.config/ofxstatement/upday.conf
[upday]
default_account = 1234567890
charset = UTF-8
```

### Utilizzo in Script

```bash
# Per automazione, usa file CSV esistenti
ofxstatement convert -t upday movimento_upday.csv output.ofx
```

## Limitazioni Conosciute

- **Limite temporale**: Il sito UpDay permette l'accesso solo agli ultimi 12 mesi di dati
- **Dipendenza browser**: Richiede Google Chrome per il web scraping
- **Rate limiting**: Uso eccessivo potrebbe causare blocchi temporanei dal sito
- **Cambio sito**: Aggiornamenti del sito UpDay potrebbero richiedere aggiornamenti del plugin

## Privacy e Sicurezza

- **Nessuna memorizzazione credenziali**: Il plugin non salva username o password
- **Solo lettura**: Accede solo in lettura ai dati delle transazioni
- **Locale**: Tutti i dati vengono elaborati localmente sul tuo computer
- **Open source**: Il codice è ispezionabile su GitHub

## Contributi

I contributi sono benvenuti! Per segnalare bug o proporre miglioramenti:

1. Apri una [issue](https://github.com/Alfystar/ofxstatement-upday/issues) su GitHub
2. Fork del repository e pull request per le modifiche
3. Segnala problemi con il sito UpDay per aggiornamenti necessari

## Licenza

Questo progetto è distribuito sotto licenza GPLv3. Vedi il file `LICENSE` per i dettagli.
