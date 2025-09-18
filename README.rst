~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
UpDay plugin for ofxstatement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Questo plugin per ofxstatement permette di importare le transazioni dei buoni pasto UpDay
utilizzando web scraping del sito day.it.

`ofxstatement`_ è uno strumento per convertire estratti conto bancari proprietari nel formato OFX,
adatto per l'importazione in GnuCash e altri software di contabilità.

.. _ofxstatement: https://github.com/kedder/ofxstatement

Caratteristiche
===============

* Web scraping automatico del sito utilizzatori.day.it
* Login manuale per maggiore sicurezza
* Navigazione automatica tra le pagine di risultati
* Estrazione di tutte le transazioni nel periodo specificato
* Conversione in formato OFX standard

Requisiti
=========

* Python 3.9+
* Chrome/Chromium browser installato
* Account UpDay attivo su day.it

Installazione
=============

1. Clona questo repository::

    $ git clone <repository-url> ofxstatement-upday
    $ cd ofxstatement-upday

2. Installa con pipenv::

    $ pipenv install
    $ pipenv shell

3. Verifica l'installazione::

    $ ofxstatement list-plugins

Dovresti vedere il plugin 'upday' nella lista.

Utilizzo
========

**Metodo 1 - Comando diretto:**

Per convertire i dati UpDay in formato OFX, esegui::

    $ ofxstatement convert -t upday dummy_input.txt output.ofx

Il file dummy_input.txt può essere vuoto o contenere qualsiasi testo, dato che i dati vengono estratti direttamente dal web.

**Metodo 2 - Script Python:**

Puoi anche usare il plugin direttamente in Python::

    from ofxstatement_upday.upday import scrapeInfoFromWeb

    # Estrai solo i dati grezzi
    data = scrapeInfoFromWeb("01/01/2024")
    print(f"Estratte {len(data)} pagine di dati")

Processo di utilizzo
====================

Quando esegui il plugin, il processo sarà il seguente:

1. **Inserimento data**: Ti verrà chiesto di inserire la data di inizio in formato gg/mm/aaaa
2. **Apertura browser**: Si aprirà automaticamente una finestra di Chrome
3. **Login manuale**: Dovrai effettuare il login manualmente sul sito day.it
4. **Conferma**: Premi INVIO nel terminale quando hai completato il login
5. **Scraping automatico**: Il plugin navigherà automaticamente e estrarrà i dati
6. **Output**: Verrà generato il file OFX con le transazioni

Esempio di sessione
===================

::

    $ ofxstatement convert -t upday input.txt transactions.ofx
    Inserisci la data di inizio (formato gg/mm/aaaa, g/m/aa, ecc.): 01/01/2024
    === INIZIO SCRAPING UPDAY ===
    Avvio del browser...
    Navigazione alla pagina di login...

    ============================================================
    EFFETTUA IL LOGIN MANUALMENTE NEL BROWSER
    Una volta loggato, premi INVIO qui per continuare...
    ============================================================
    Premi INVIO quando hai completato il login:

    Login completato con successo!
    Navigazione alla pagina dei movimenti...
    Impostazione filtro data: 01/01/2024
    Inizio scraping delle pagine...
    Scraping pagina 1...
    Dati estratti dalla pagina 1
    Scraping pagina 2...
    Dati estratti dalla pagina 2
    Nessuna pagina successiva disponibile
    === SCRAPING COMPLETATO: 2 pagine elaborate ===
    Chiusura del browser...

Risoluzione problemi
====================

**Chrome non trovato:**
Assicurati di avere Chrome o Chromium installato. Il plugin usa webdriver-manager per scaricare automaticamente il driver.

**Errori di login:**
Se il sito cambia la struttura della pagina di login, potrebbe essere necessario aggiornare i selettori nel codice.

**Timeout durante il scraping:**
Aumenta i tempi di attesa nelle impostazioni o verifica la connessione internet.

**Paginazione non funzionante:**
Il plugin cerca automaticamente la paginazione con id "pg_page". Se il sito cambia questa struttura, sarà necessario aggiornare il codice.

Sviluppo
========

Per sviluppare e testare il plugin::

    $ pipenv install --dev
    $ pipenv shell
    $ python -m pytest tests/

Per testare solo il web scraping senza generare OFX::

    $ python -c "
    from ofxstatement_upday.upday import scrapeInfoFromWeb
    data = scrapeInfoFromWeb('01/01/2024')
    print(f'Dati estratti: {len(data)} pagine')
    for page in data:
        print(f'Pagina {page[\"page\"]}: {len(page[\"html\"])} caratteri HTML')
    "

Limitazioni
===========

* Richiede login manuale per sicurezza
* Dipende dalla struttura HTML del sito day.it
* Necessita di Chrome/Chromium installato
* Funziona solo con account UpDay attivi

Licenza
=======

Questo progetto è rilasciato sotto licenza GPL v3.
