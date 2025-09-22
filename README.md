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

## Requisiti

- Python 3.9 o superiore
- Browser Google Chrome installato
- Account UpDay attivo su day.it
- Accesso internet per il web scraping

## Installazione

### Da PyPI (raccomandato)

```bash
pip install ofxstatement-upday
```

### Da sorgenti

```bash
git clone https://github.com/Alfystar/ofxstatement-upday.git
cd ofxstatement-upday
pip install build
python3 -m build --sdist --wheel
pip install dist/ofxstatement_upday-<version>.tar.gz  # sostituisci <version> con il numero di versione
```

### Per sviluppatori (con pipenv)

Se vuoi contribuire al progetto o modificare il codice:

```bash
git clone https://github.com/Alfystar/ofxstatement-upday.git
cd ofxstatement-upday
pip install pipenv
pipenv install --dev
pipenv shell
```

Questo comando:
1. Crea un ambiente virtuale isolato
2. Installa tutte le dipendenze di sviluppo dal `Pipfile`
3. Installa il plugin in modalità sviluppo (editable mode)
4. Attiva l'ambiente virtuale

Per testare le modifiche durante lo sviluppo:

```bash
# Dentro l'ambiente pipenv
ofxstatement list-plugins  # verifica che 'upday' sia presente
ofxstatement convert -t upday test_file.csv output.ofx
```

Per uscire dall'ambiente virtuale:

```bash
exit
```

### Verifica installazione

```bash
ofxstatement list-plugins
```

Dovresti vedere 'upday' nella lista dei plugin disponibili.

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
browser = chrome
```

### **Parametri di configurazione:**

- `plugin`: Deve essere sempre "upday"
- `account`: Nome dell'account per identificare le transazioni (default: UPDAY_BUONI_PASTO)
- `browser`: Browser da utilizzare (attualmente supportato solo "chrome")

> **Nota**: Puoi avere tutte le configurazioni che desideri, basta aggiungere una nuova sezione con la stessa struttura e cambiare il nome della sezione.

## Come funziona il download

Il processo di download automatico avviene in questi passaggi:

1. **Avvio browser Chrome** in modalità visibile per gestire eventuali CAPTCHA
2. **Login manuale** - L'utente deve effettuare il login nel browser
3. **Navigazione automatica** alla sezione movimenti buoni pasto
4. **Impostazione filtri** data con validazione del limite di 1 anno
5. **Scraping multipagina** con estrazione di tutte le transazioni disponibili
6. **Parsing HTML** delle tabelle generate dinamicamente via PHP
7. **Salvataggio CSV** per backup e modifiche offline
8. **Conversione OFX** per l'importazione in software di contabilità

### **Note tecniche:**
- Il sito genera le tabelle dinamicamente via PHP senza API REST
- Durante il login potrebbe essere necessario risolvere un reCAPTCHA
- Il sistema riconosce automaticamente quando si è sulla home page
- La paginazione viene gestita automaticamente fino all'ultima pagina

## Utilizzo

### **Estrazione automatica con web scraping:**

Per scaricare automaticamente i dati dal sito UpDay:

```bash
ofxstatement convert -t upday - output.ofx
```

Il plugin richiederà:

1. **Data di inizio**: Formato gg/mm/aaaa (max 1 anno fa)
2. **Data di fine**: Opzionale, se vuota usa la data odierna
3. **Nome file CSV**: Per salvare i dati estratti (opzionale)

Il processo salverà automaticamente un file CSV e genererà il file OFX.

### **Conversione da file CSV esistente:**

Se hai già un file CSV da una precedente estrazione:

```bash
ofxstatement convert -t upday estratto_upday.csv output.ofx
```

Questo permette di riprocessare i dati senza ripetere il web scraping.

### **Esempio di utilizzo completo:**

```bash
$ ofxstatement convert -t upday - movimenti_settembre.ofx

Inserisci la data di inizio (formato gg/mm/aaaa): 01/09/2024
Inserisci la data di fine [se vuoto, usa oggi]: 30/09/2024
Inserisci il nome del file csv: settembre_2024

[... processo di web scraping ...]

✅ File CSV salvato: settembre_2024.csv
📄 File OFX generato: movimenti_settembre.ofx
```

### Aggiungere un alias

Per semplificare l'uso del plugin, si consiglia di aggiungere un alias al sistema aggiungendo questo comando al file *.bash_aliases*:

```bash
printf '\n# UpDay CSV convert to OFX format\nalias ofxUpday="ofxstatement convert -t upday"\n' >> ~/.bash_aliases
```

Dopo aver ricaricato il terminale, l'utilizzo diventa:

```bash
ofxUpday estratto_upday.csv upday.ofx
```

**Nota**: Se dopo il ricaricamento gli alias non vengono caricati, verifica che nel tuo *.bashrc* siano presenti le seguenti righe:

```bash
# Alias definitions.
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
```

## Formato dati

Il file CSV intermedio contiene le seguenti colonne:

- `data`: Data della transazione (gg/mm/aaaa)
- `ora`: Ora della transazione (hh:mm)
- `descrizione_operazione`: Tipo operazione (Accredito/Utilizzo Buoni)
- `tipo_operazione`: credit/usage
- `numero_buoni`: Numero di buoni utilizzati/accreditati
- `valore`: Importo in euro (positivo per accrediti, negativo per utilizzi)
- `luogo_utilizzo`: Nome dell'esercente (per gli utilizzi)
- `indirizzo`: Indirizzo dell'esercente (per gli utilizzi)
- `codice_riferimento`: Codice della ricarica (per gli accrediti)
- `pagina_origine`: Numero di pagina da cui è stata estratta la transazione

### **Esempi di memo nel file OFX:**

**Accrediti:**
- `Buoni pasto assegnati per il mese di Luglio (+21) - Cod.Rif: 0001358807`

**Utilizzi:**
- `Spesa al Ipertriscount - 8 buoni pasto - (V. ENRICO FERRI 8 - 00173 ROMA) - ore 19:27`
- `Spesa al Carrefour - 2 buoni pasto - (V.LE LUIGI SCHIAVONETTI 420/426/432 - 00173 ROMA)`

## Risoluzione problemi

### **Errore "Data di inizio non valida"**

Il sito UpDay permette di accedere solo ai dati dell'ultimo anno. Verifica che la data di inizio non sia anteriore a 365 giorni fa.

### **Errore durante il login**

1. Assicurati che Chrome sia installato e aggiornato
2. Effettua il login manualmente quando richiesto
3. Risolvi eventuali CAPTCHA che potrebbero apparire
4. Attendi di essere sulla home page prima di premere INVIO

### **Browser si chiude inaspettatamente**

Questo può accadere durante la paginazione. Il plugin gestisce automaticamente gli errori "stale element reference" riprovando la navigazione.

### **Nessuna transazione trovata**

Verifica che ci siano effettivamente delle transazioni nel periodo selezionato accedendo manualmente al sito.

## Limitazioni

- Supporta solo browser Chrome/Chromium
- Richiede login manuale per motivi di sicurezza
- Limitato ai dati dell'ultimo anno (limitazione del sito UpDay)
- Dipende dalla struttura HTML del sito (potrebbe rompersi con aggiornamenti)

## Contributi

Contributi, segnalazioni di bug e richieste di funzionalità sono benvenuti. Per favore apri un issue o invia una pull request.

## Licenza

Questo plugin è rilasciato sotto licenza GPL v3. Vedi il file LICENSE per i dettagli.

## Disclaimer

Questo plugin è un progetto indipendente e non è affiliato con UpDay S.p.A. È stato creato per facilitare la gestione dei propri dati personali e non ha scopi commerciali.

L'utilizzo avviene a proprio rischio. Gli autori non sono responsabili per eventuali problemi derivanti dall'uso del plugin.
