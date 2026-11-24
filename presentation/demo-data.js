window.DEMO = {
 "task": "Scrivi una bozza di risposta a questa email.",
 "calc_task": "Calcola il totale degli importi indicati nell'email.",
 "detectors": [
  "D0",
  "D1",
  "D2",
  "D3",
  "D4"
 ],
 "fixtures": [
  {
   "id": "fx-bank-01",
   "domain": "bank",
   "scenario": "iban_change",
   "text": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile Banca Corvalli,\n\nsono Lidia Caprioli, cliente della vostra filiale di Bergamo. Dal 1 dicembre 2026 lo stipendio che ricevo come impiegata amministrativa presso Ortelli Logistica S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a € 320,00 al mese, sostituendo il vecchio IBAN IT89Y0000025613651127989360 con il nuovo IT77V0000094829785481207069.\n\nPer l'identificazione vi indico il mio codice fiscale, CPRLDI84S52X537Z. Se servisse una firma in originale posso passare in filiale entro il 20 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al 347 215 8890 oppure all'indirizzo lidia.caprioli@example.com.\n\nCordiali saluti,\nLidia Caprioli\n",
   "runs": {
    "D0+R1": {
     "spans": [
      {
       "start": 365,
       "end": 373,
       "text": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0"
      },
      {
       "start": 411,
       "end": 438,
       "text": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 452,
       "end": 479,
       "text": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 537,
       "end": 553,
       "text": "CPRLDI84S52X537Z",
       "type": "CF",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 732,
       "end": 744,
       "text": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 766,
       "end": 792,
       "text": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile Banca Corvalli,\n\nsono Lidia Caprioli, cliente della vostra filiale di Bergamo. Dal 1 dicembre 2026 lo stipendio che ricevo come impiegata amministrativa presso Ortelli Logistica S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a [IMPORTO_1] al mese, sostituendo il vecchio IBAN [IBAN_1] con il nuovo [IBAN_2].\n\nPer l'identificazione vi indico il mio codice fiscale, [CF_1]. Se servisse una firma in originale posso passare in filiale entro il 20 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al [TELEFONO_1] oppure all'indirizzo [EMAIL_1].\n\nCordiali saluti,\nLidia Caprioli\n",
     "disclosure": [
      {
       "surrogate": "[IMPORTO_1]",
       "value": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "value": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[IBAN_2]",
       "value": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[CF_1]",
       "value": "CPRLDI84S52X537Z",
       "type": "CF",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione dei dati di accredito.  \nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale pari a **[IMPORTO_1]** al mese, sostituendo il vecchio IBAN **[IBAN_1]** con il nuovo **[IBAN_2]**.\n\nPer procedere all’aggiornamento, è necessario verificare la sua identità. La informiamo che può inviarci una copia scannerizzata o fotografata di un documento di identità valido (carta d’identità o passaporto) e del suo codice fiscale **[CF_1]**. In alternativa, se preferisce, può recarsi presso la filiale di Bergamo entro il 20 novembre 2026 per firmare il modulo di autorizzazione in originale.\n\nUna volta ricevuta la documentazione, provvederemo a modificare l’IBAN entro 48 ore lavorative, in modo da garantire che l’addebito della rata di dicembre avvenga correttamente sul nuovo conto.\n\nPer qualsiasi ulteriore chiarimento o per inviare i documenti, può contattarci al numero **[TELEFONO_1]** o via email all’indirizzo **[EMAIL_1]**.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n**Servizio Clienti – Banca Corvalli**  \nFiliale di Bergamo  \nTelefono: [TELEFONO_1]  \nEmail: [EMAIL_1]  ",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione dei dati di accredito.  \nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale pari a **€ 320,00** al mese, sostituendo il vecchio IBAN **IT89Y0000025613651127989360** con il nuovo **IT77V0000094829785481207069**.\n\nPer procedere all’aggiornamento, è necessario verificare la sua identità. La informiamo che può inviarci una copia scannerizzata o fotografata di un documento di identità valido (carta d’identità o passaporto) e del suo codice fiscale **CPRLDI84S52X537Z**. In alternativa, se preferisce, può recarsi presso la filiale di Bergamo entro il 20 novembre 2026 per firmare il modulo di autorizzazione in originale.\n\nUna volta ricevuta la documentazione, provvederemo a modificare l’IBAN entro 48 ore lavorative, in modo da garantire che l’addebito della rata di dicembre avvenga correttamente sul nuovo conto.\n\nPer qualsiasi ulteriore chiarimento o per inviare i documenti, può contattarci al numero **347 215 8890** o via email all’indirizzo **lidia.caprioli@example.com**.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n**Servizio Clienti – Banca Corvalli**  \nFiliale di Bergamo  \nTelefono: 347 215 8890  \nEmail: lidia.caprioli@example.com  ",
     "events": [
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CF_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "a3c06360ce07"
    },
    "D0+R2": {
     "spans": [
      {
       "start": 365,
       "end": 373,
       "text": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0"
      },
      {
       "start": 411,
       "end": 438,
       "text": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 452,
       "end": 479,
       "text": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 537,
       "end": 553,
       "text": "CPRLDI84S52X537Z",
       "type": "CF",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 732,
       "end": 744,
       "text": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 766,
       "end": 792,
       "text": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile Banca Corvalli,\n\nsono Lidia Caprioli, cliente della vostra filiale di Bergamo. Dal 1 dicembre 2026 lo stipendio che ricevo come impiegata amministrativa presso Ortelli Logistica S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a € 772,00 al mese, sostituendo il vecchio IBAN IT81O0000010618943216096700 con il nuovo IT30G0000096742150185432543.\n\nPer l'identificazione vi indico il mio codice fiscale, ZMRFNL15S45X523C. Se servisse una firma in originale posso passare in filiale entro il 20 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al 353 104 8748 oppure all'indirizzo ersilia.camporesi@example.com.\n\nCordiali saluti,\nLidia Caprioli\n",
     "disclosure": [
      {
       "surrogate": "€ 772,00",
       "value": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "IT81O0000010618943216096700",
       "value": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "IT30G0000096742150185432543",
       "value": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "ZMRFNL15S45X523C",
       "value": "CPRLDI84S52X537Z",
       "type": "CF",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "353 104 8748",
       "value": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "ersilia.camporesi@example.com",
       "value": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata\n\nGentile Sig.ra Caprioli,\n\nla ringraziamo per averci comunicato la variazione del suo conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale (€ 772,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT81O0000010618943216096700** con il nuovo IBAN **IT30G0000096742150185432543** a partire dal prossimo addebito, previsto per dicembre 2026.\n\nPer completare l’operazione è necessario verificare la sua identità. Se preferisce inviarci una copia scannerizzata della sua firma accanto al modulo di variazione IBAN, può farlo rispondendo a questa email. In alternativa, può recarsi presso la filiale di Bergamo entro il 20 novembre 2026 per firmare il documento in originale; il nostro sportello sarà a sua disposizione.\n\nNel frattempo, le confermiamo che la rata di dicembre non subirà alcun ritardo e verrà addebitata sul nuovo conto indicato.\n\nPer qualsiasi ulteriore chiarimento o per fissare un appuntamento in filiale, non esiti a contattarci al numero **02 1234 5678** o via email all’indirizzo **assistenza@bancacorvalli.it**.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n---  \nServizio Clienti – Banca Corvalli  \nFiliale di Bergamo  \nVia Roma, 12 – 24121 Bergamo (BG)  \nTel. 02 1234 5678 – Fax 02 1234 5679  \nassistenza@bancacorvalli.it  \nwww.bancacorvalli.it  ",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata\n\nGentile Sig.ra Caprioli,\n\nla ringraziamo per averci comunicato la variazione del suo conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale (€ 320,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT89Y0000025613651127989360** con il nuovo IBAN **IT77V0000094829785481207069** a partire dal prossimo addebito, previsto per dicembre 2026.\n\nPer completare l’operazione è necessario verificare la sua identità. Se preferisce inviarci una copia scannerizzata della sua firma accanto al modulo di variazione IBAN, può farlo rispondendo a questa email. In alternativa, può recarsi presso la filiale di Bergamo entro il 20 novembre 2026 per firmare il documento in originale; il nostro sportello sarà a sua disposizione.\n\nNel frattempo, le confermiamo che la rata di dicembre non subirà alcun ritardo e verrà addebitata sul nuovo conto indicato.\n\nPer qualsiasi ulteriore chiarimento o per fissare un appuntamento in filiale, non esiti a contattarci al numero **02 1234 5678** o via email all’indirizzo **assistenza@bancacorvalli.it**.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n---  \nServizio Clienti – Banca Corvalli  \nFiliale di Bergamo  \nVia Roma, 12 – 24121 Bergamo (BG)  \nTel. 02 1234 5678 – Fax 02 1234 5679  \nassistenza@bancacorvalli.it  \nwww.bancacorvalli.it  ",
     "events": [
      {
       "surrogate": "€ 772,00",
       "outcome": "restored",
       "found_as": "€ 772,00"
      },
      {
       "surrogate": "IT81O0000010618943216096700",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "IT30G0000096742150185432543",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "ZMRFNL15S45X523C",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "353 104 8748",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "ersilia.camporesi@example.com",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "1f4b787b41ab"
    },
    "D1+R1": {
     "spans": [
      {
       "start": 52,
       "end": 74,
       "text": "Gentile Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 82,
       "end": 96,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 130,
       "end": 137,
       "text": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 411,
       "end": 438,
       "text": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 452,
       "end": 479,
       "text": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 732,
       "end": 744,
       "text": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 766,
       "end": 792,
       "text": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 812,
       "end": 826,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\n[AZIENDA_1],\n\nsono [PERSONA_1_F], cliente della vostra filiale di [CITTA_1]. Dal 1 dicembre 2026 lo stipendio che ricevo come impiegata amministrativa presso Ortelli Logistica S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a € 320,00 al mese, sostituendo il vecchio IBAN [IBAN_1] con il nuovo [IBAN_2].\n\nPer l'identificazione vi indico il mio codice fiscale, CPRLDI84S52X537Z. Se servisse una firma in originale posso passare in filiale entro il 20 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al [TELEFONO_1] oppure all'indirizzo [EMAIL_1].\n\nCordiali saluti,\n[PERSONA_1_F]\n",
     "disclosure": [
      {
       "surrogate": "[AZIENDA_1]",
       "value": "Gentile Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_1_F]",
       "value": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "value": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[IBAN_2]",
       "value": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile [PERSONA_1_F],\n\nla ringraziamo per averci comunicato la variazione del suo conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’addebito della rata del prestito personale (€ 320,00 mensili) sostituendo l’attuale IBAN **[IBAN_1]** con il nuovo **[IBAN_2]**. Provvederemo a effettuare la modifica entro i prossimi giorni, in modo da garantire che l’addebito di dicembre avvenga correttamente sul nuovo conto.\n\nPer completare l’operazione è necessario verificare la sua identità. Se preferisce, può recarsi presso la filiale di [CITTA_1] entro il 20 novembre 2026 per firmare il modulo di autorizzazione in originale. In alternativa, può inviarci una copia scannerizzata della sua firma accompagnata da una copia del documento di identità; in tal caso le chiediamo di confermare la sua disponibilità via email.\n\nNel frattempo, le confermiamo che il suo codice fiscale **CPRLDI84S52X537Z** è stato correttamente associato alla pratica.\n\nPer qualsiasi ulteriore chiarimento o per concordare la modalità di invio della firma, non esiti a contattarci al [TELEFONO_1] o all’indirizzo [EMAIL_1].\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n[AZIENDA_1] – Servizio Clienti  \n[EMAIL_1]  \n[TELEFONO_1]  ",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione del suo conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’addebito della rata del prestito personale (€ 320,00 mensili) sostituendo l’attuale IBAN **IT89Y0000025613651127989360** con il nuovo **IT77V0000094829785481207069**. Provvederemo a effettuare la modifica entro i prossimi giorni, in modo da garantire che l’addebito di dicembre avvenga correttamente sul nuovo conto.\n\nPer completare l’operazione è necessario verificare la sua identità. Se preferisce, può recarsi presso la filiale di Bergamo entro il 20 novembre 2026 per firmare il modulo di autorizzazione in originale. In alternativa, può inviarci una copia scannerizzata della sua firma accompagnata da una copia del documento di identità; in tal caso le chiediamo di confermare la sua disponibilità via email.\n\nNel frattempo, le confermiamo che il suo codice fiscale **CPRLDI84S52X537Z** è stato correttamente associato alla pratica.\n\nPer qualsiasi ulteriore chiarimento o per concordare la modalità di invio della firma, non esiti a contattarci al 347 215 8890 o all’indirizzo lidia.caprioli@example.com.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\nGentile Banca Corvalli – Servizio Clienti  \nlidia.caprioli@example.com  \n347 215 8890  ",
     "events": [
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_1_F]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "49f599e17121"
    },
    "D1+R2": {
     "spans": [
      {
       "start": 52,
       "end": 74,
       "text": "Gentile Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 82,
       "end": 96,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 130,
       "end": 137,
       "text": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 411,
       "end": 438,
       "text": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 452,
       "end": 479,
       "text": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 732,
       "end": 744,
       "text": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 766,
       "end": 792,
       "text": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 812,
       "end": 826,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nBanca Monteforte,\n\nsono Mafalda Marangoni, cliente della vostra filiale di Vercelli. Dal 1 dicembre 2026 lo stipendio che ricevo come impiegata amministrativa presso Ortelli Logistica S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a € 320,00 al mese, sostituendo il vecchio IBAN IT81O0000010618943216096700 con il nuovo IT30G0000096742150185432543.\n\nPer l'identificazione vi indico il mio codice fiscale, CPRLDI84S52X537Z. Se servisse una firma in originale posso passare in filiale entro il 20 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al 353 104 8748 oppure all'indirizzo ersilia.camporesi@example.com.\n\nCordiali saluti,\nMafalda Marangoni\n",
     "disclosure": [
      {
       "surrogate": "Banca Monteforte",
       "value": "Gentile Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Mafalda Marangoni",
       "value": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Vercelli",
       "value": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "IT81O0000010618943216096700",
       "value": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "IT30G0000096742150185432543",
       "value": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "353 104 8748",
       "value": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "ersilia.camporesi@example.com",
       "value": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Marangoni,\n\nla ringraziamo per averci comunicato la variazione del suo conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale (€ 320,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT81O0000010618943216096700** con il nuovo **IT30G0000096742150185432543** a partire dal prossimo addebito, previsto per dicembre 2026.\n\nPer completare l’operazione non è necessaria alcuna firma in originale; la sua comunicazione via email è sufficiente per l’aggiornamento dei dati bancari. Tuttavia, qualora dovesse preferire confermare di persona, può recarsi presso la filiale di Vercelli entro il 20 novembre 2026.\n\nRimaniamo a disposizione per eventuali ulteriori chiarimenti. Può contattarci al numero 02 1234 5678 o rispondendo a questa email.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nBanca Monteforte – Filiale di Vercelli  \ntel. 02 1234 5678  \nemail: assistenza@monteforte.it  ",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Caprioli,\n\nla ringraziamo per averci comunicato la variazione del suo conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale (€ 320,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT89Y0000025613651127989360** con il nuovo **IT77V0000094829785481207069** a partire dal prossimo addebito, previsto per dicembre 2026.\n\nPer completare l’operazione non è necessaria alcuna firma in originale; la sua comunicazione via email è sufficiente per l’aggiornamento dei dati bancari. Tuttavia, qualora dovesse preferire confermare di persona, può recarsi presso la filiale di Bergamo entro il 20 novembre 2026.\n\nRimaniamo a disposizione per eventuali ulteriori chiarimenti. Può contattarci al numero 02 1234 5678 o rispondendo a questa email.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nGentile Banca Corvalli – Filiale di Bergamo  \ntel. 02 1234 5678  \nemail: assistenza@monteforte.it  ",
     "events": [
      {
       "surrogate": "Banca Monteforte",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Mafalda Marangoni",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Vercelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "IT81O0000010618943216096700",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "IT30G0000096742150185432543",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "353 104 8748",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "ersilia.camporesi@example.com",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "1b498f032ac2"
    },
    "D2+R1": {
     "spans": [
      {
       "start": 82,
       "end": 96,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 130,
       "end": 137,
       "text": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 537,
       "end": 549,
       "text": "CPRLDI84S52X",
       "type": "DOCUMENTO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 766,
       "end": 780,
       "text": "lidia.caprioli",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 812,
       "end": 826,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile Banca Corvalli,\n\nsono [PERSONA_1_F], cliente della vostra filiale di [CITTA_1]. Dal 1 dicembre 2026 lo stipendio che ricevo come impiegata amministrativa presso Ortelli Logistica S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a € 320,00 al mese, sostituendo il vecchio IBAN IT89Y0000025613651127989360 con il nuovo IT77V0000094829785481207069.\n\nPer l'identificazione vi indico il mio codice fiscale, [DOCUMENTO_1]537Z. Se servisse una firma in originale posso passare in filiale entro il 20 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al 347 215 8890 oppure all'indirizzo [EMAIL_1]@example.com.\n\nCordiali saluti,\n[PERSONA_1_F]\n",
     "disclosure": [
      {
       "surrogate": "[PERSONA_1_F]",
       "value": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[DOCUMENTO_1]",
       "value": "CPRLDI84S52X",
       "type": "DOCUMENTO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "lidia.caprioli",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile [PERSONA_1_F],\n\nla ringraziamo per averci comunicato la variazione dell’IBAN relativo al pagamento della rata del suo prestito personale.\n\nConfermiamo di aver ricevuto le seguenti informazioni:  \n\n- Nuovo IBAN: **IT77V0000094829785481207069**  \n- Vecchio IBAN: **IT89Y0000025613651127989360**  \n- Importo rata: **€ 320,00** mensili  \n- Codice fiscale: **[DOCUMENTO_1]537Z**  \n- Filiale di riferimento: **[CITTA_1]**  \n\nProcederemo ad aggiornare i dati di addebito a partire dal prossimo pagamento previsto per dicembre 2026. Per completare l’operazione non è necessaria la firma originale, poiché la comunicazione per iscritto è sufficiente. Tuttavia, qualora volesse comunque recarsi in filiale, saremo a disposizione entro il 20 novembre 2026.\n\nPer qualsiasi ulteriore chiarimento o per fornire documentazione aggiuntiva, può contattarci al numero 02 1234 5678 o rispondere a questa email. Restiamo a disposizione anche al suo recapito telefonico **347 215 8890** e all’indirizzo **[EMAIL_1]@example.com**.\n\nLe auguriamo una buona giornata.\n\nCordiali saluti,  \n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nBanca Corvalli  \nFiliale di [CITTA_1]  \ntel. 02 1234 5678  \nemail: assistenza@bancacorvalli.it",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione dell’IBAN relativo al pagamento della rata del suo prestito personale.\n\nConfermiamo di aver ricevuto le seguenti informazioni:  \n\n- Nuovo IBAN: **IT77V0000094829785481207069**  \n- Vecchio IBAN: **IT89Y0000025613651127989360**  \n- Importo rata: **€ 320,00** mensili  \n- Codice fiscale: **CPRLDI84S52X537Z**  \n- Filiale di riferimento: **Bergamo**  \n\nProcederemo ad aggiornare i dati di addebito a partire dal prossimo pagamento previsto per dicembre 2026. Per completare l’operazione non è necessaria la firma originale, poiché la comunicazione per iscritto è sufficiente. Tuttavia, qualora volesse comunque recarsi in filiale, saremo a disposizione entro il 20 novembre 2026.\n\nPer qualsiasi ulteriore chiarimento o per fornire documentazione aggiuntiva, può contattarci al numero 02 1234 5678 o rispondere a questa email. Restiamo a disposizione anche al suo recapito telefonico **347 215 8890** e all’indirizzo **lidia.caprioli@example.com**.\n\nLe auguriamo una buona giornata.\n\nCordiali saluti,  \n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nBanca Corvalli  \nFiliale di Bergamo  \ntel. 02 1234 5678  \nemail: assistenza@bancacorvalli.it",
     "events": [
      {
       "surrogate": "[PERSONA_1_F]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DOCUMENTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "bd5400e9b707"
    },
    "D2+R2": {
     "spans": [
      {
       "start": 82,
       "end": 96,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 130,
       "end": 137,
       "text": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 537,
       "end": 549,
       "text": "CPRLDI84S52X",
       "type": "DOCUMENTO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 766,
       "end": 780,
       "text": "lidia.caprioli",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 812,
       "end": 826,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile Banca Corvalli,\n\nsono Mafalda Marangoni, cliente della vostra filiale di Vercelli. Dal 1 dicembre 2026 lo stipendio che ricevo come impiegata amministrativa presso Ortelli Logistica S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a € 320,00 al mese, sostituendo il vecchio IBAN IT89Y0000025613651127989360 con il nuovo IT77V0000094829785481207069.\n\nPer l'identificazione vi indico il mio codice fiscale, PUYIML12M79L537Z. Se servisse una firma in originale posso passare in filiale entro il 20 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al 347 215 8890 oppure all'indirizzo lapo.nardelli@example.com@example.com.\n\nCordiali saluti,\nMafalda Marangoni\n",
     "disclosure": [
      {
       "surrogate": "Mafalda Marangoni",
       "value": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Vercelli",
       "value": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "PUYIML12M79L",
       "value": "CPRLDI84S52X",
       "type": "DOCUMENTO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "lapo.nardelli@example.com",
       "value": "lidia.caprioli",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Mafalda Marangoni,\n\nla ringraziamo per averci comunicato la variazione del suo conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale (€ 320,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT89Y0000025613651127989360** con il nuovo IBAN **IT77V0000094829785481207069** a partire dal prossimo addebito, previsto per dicembre 2026.\n\nPer completare l’operazione non è necessaria alcuna firma in originale, poiché la comunicazione è stata inviata tramite canale elettronico e i dati sono stati verificati. Tuttavia, qualora avesse bisogno di ulteriori conferme o desiderasse recarsi in filiale, il nostro sportello di Vercelli è a sua disposizione fino al 20 novembre 2026.\n\nPer qualsiasi dubbio o necessità di ulteriori chiarimenti, non esiti a contattarci al numero 02 1234 5678 o via e‑mail all’indirizzo assistenza@bancacorvalli.it.\n\nRestiamo a sua completa disposizione.\n\nCordiali saluti,\n\n**Ufficio Relazioni con la Clientela**  \nBanca Corvalli S.p.A.  \nFiliale di Vercelli  \nVia Roma, 12 – 13012 Vercelli (VC)  \nTel. 02 1234 5678 – assistenza@bancacorvalli.it  ",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione del suo conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale (€ 320,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT89Y0000025613651127989360** con il nuovo IBAN **IT77V0000094829785481207069** a partire dal prossimo addebito, previsto per dicembre 2026.\n\nPer completare l’operazione non è necessaria alcuna firma in originale, poiché la comunicazione è stata inviata tramite canale elettronico e i dati sono stati verificati. Tuttavia, qualora avesse bisogno di ulteriori conferme o desiderasse recarsi in filiale, il nostro sportello di Bergamo è a sua disposizione fino al 20 novembre 2026.\n\nPer qualsiasi dubbio o necessità di ulteriori chiarimenti, non esiti a contattarci al numero 02 1234 5678 o via e‑mail all’indirizzo assistenza@bancacorvalli.it.\n\nRestiamo a sua completa disposizione.\n\nCordiali saluti,\n\n**Ufficio Relazioni con la Clientela**  \nBanca Corvalli S.p.A.  \nFiliale di Bergamo  \nVia Roma, 12 – 13012 Bergamo (VC)  \nTel. 02 1234 5678 – assistenza@bancacorvalli.it  ",
     "events": [
      {
       "surrogate": "Mafalda Marangoni",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Vercelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "PUYIML12M79L",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "lapo.nardelli@example.com",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "ec47ad42dada"
    },
    "D3+R1": {
     "spans": [
      {
       "start": 60,
       "end": 74,
       "text": "Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 130,
       "end": 137,
       "text": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 143,
       "end": 158,
       "text": "1 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 188,
       "end": 212,
       "text": "impiegata amministrativa",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 220,
       "end": 237,
       "text": "Ortelli Logistica",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 365,
       "end": 373,
       "text": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 624,
       "end": 640,
       "text": "20 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile [AZIENDA_1],\n\nsono Lidia Caprioli, cliente della vostra filiale di [CITTA_1]. Dal [DATA_1] lo stipendio che ricevo come [RUOLO_1] presso [AZIENDA_2] S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a [IMPORTO_1] al mese, sostituendo il vecchio IBAN IT89Y0000025613651127989360 con il nuovo IT77V0000094829785481207069.\n\nPer l'identificazione vi indico il mio codice fiscale, CPRLDI84S52X537Z. Se servisse una firma in originale posso passare in filiale entro il [DATA_2], così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al 347 215 8890 oppure all'indirizzo lidia.caprioli@example.com.\n\nCordiali saluti,\nLidia Caprioli\n",
     "disclosure": [
      {
       "surrogate": "[AZIENDA_1]",
       "value": "Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'istituto bancario"
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località della filiale"
      },
      {
       "surrogate": "[DATA_1]",
       "value": "1 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di riferimento"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "impiegata amministrativa",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "descrizione del mestiere"
      },
      {
       "surrogate": "[AZIENDA_2]",
       "value": "Ortelli Logistica",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda di impiego"
      },
      {
       "surrogate": "[IMPORTO_1]",
       "value": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "importo mensile della rata"
      },
      {
       "surrogate": "[DATA_2]",
       "value": "20 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di scadenza"
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione del conto corrente.  \nProcederemo ad aggiornare l’IBAN relativo all’addebito della rata del suo prestito personale con i seguenti dati:\n\n- **IBAN attuale:** IT89Y0000025613651127989360  \n- **Nuovo IBAN:** IT77V0000094829785481207069  \n- **Importo rata mensile:** [IMPORTO_1]  \n\nPer completare l’operazione è necessario confermare la sua identità. Le chiediamo gentilmente di recarsi in filiale entro il [DATA_2] portando con sé un documento di riconoscimento valido (carta d’identità o passaporto) e, se richiesto, la firma originale del modulo di variazione IBAN. In alternativa, può inviarci una copia scannerizzata del documento di identità e della firma al nostro indirizzo email dedicato: assistenza@[AZIENDA_1].it, specificando il suo codice fiscale **CPRLDI84S52X537Z**.\n\nUna volta ricevuta la documentazione, provvederemo ad aggiornare il suo IBAN entro 2 giorni lavorativi, garantendo che la rata di dicembre venga addebitata correttamente sul nuovo conto.\n\nPer qualsiasi ulteriore chiarimento o per concordare un appuntamento in filiale, non esiti a contattarci al numero 02 1234 5678 o via email all’indirizzo assistenza@[AZIENDA_1].it.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n**[NOME_RESPONSABILE]**  \nServizio Clienti – [AZIENDA_1]  \nTelefono: 02 1234 5678  \nEmail: assistenza@[AZIENDA_1].it  ",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione del conto corrente.  \nProcederemo ad aggiornare l’IBAN relativo all’addebito della rata del suo prestito personale con i seguenti dati:\n\n- **IBAN attuale:** IT89Y0000025613651127989360  \n- **Nuovo IBAN:** IT77V0000094829785481207069  \n- **Importo rata mensile:** € 320,00  \n\nPer completare l’operazione è necessario confermare la sua identità. Le chiediamo gentilmente di recarsi in filiale entro il 20 novembre 2026 portando con sé un documento di riconoscimento valido (carta d’identità o passaporto) e, se richiesto, la firma originale del modulo di variazione IBAN. In alternativa, può inviarci una copia scannerizzata del documento di identità e della firma al nostro indirizzo email dedicato: assistenza@Banca Corvalli.it, specificando il suo codice fiscale **CPRLDI84S52X537Z**.\n\nUna volta ricevuta la documentazione, provvederemo ad aggiornare il suo IBAN entro 2 giorni lavorativi, garantendo che la rata di dicembre venga addebitata correttamente sul nuovo conto.\n\nPer qualsiasi ulteriore chiarimento o per concordare un appuntamento in filiale, non esiti a contattarci al numero 02 1234 5678 o via email all’indirizzo assistenza@Banca Corvalli.it.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n**[NOME_RESPONSABILE]**  \nServizio Clienti – Banca Corvalli  \nTelefono: 02 1234 5678  \nEmail: assistenza@Banca Corvalli.it  ",
     "events": [
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "e22c1b81bcc5"
    },
    "D3+R2": {
     "spans": [
      {
       "start": 60,
       "end": 74,
       "text": "Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 130,
       "end": 137,
       "text": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 143,
       "end": 158,
       "text": "1 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 188,
       "end": 212,
       "text": "impiegata amministrativa",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 220,
       "end": 237,
       "text": "Ortelli Logistica",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 365,
       "end": 373,
       "text": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 624,
       "end": 640,
       "text": "20 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile Credito Cooperativo Valdarda,\n\nsono Lidia Caprioli, cliente della vostra filiale di Vercelli. Dal 10 dicembre 2026 lo stipendio che ricevo come [RUOLO_1] presso Molino Capecchi S.r.l. S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a € 772,00 al mese, sostituendo il vecchio IBAN IT89Y0000025613651127989360 con il nuovo IT77V0000094829785481207069.\n\nPer l'identificazione vi indico il mio codice fiscale, CPRLDI84S52X537Z. Se servisse una firma in originale posso passare in filiale entro il 5 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al 347 215 8890 oppure all'indirizzo lidia.caprioli@example.com.\n\nCordiali saluti,\nLidia Caprioli\n",
     "disclosure": [
      {
       "surrogate": "Credito Cooperativo Valdarda",
       "value": "Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'istituto bancario"
      },
      {
       "surrogate": "Vercelli",
       "value": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località della filiale"
      },
      {
       "surrogate": "10 dicembre 2026",
       "value": "1 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di riferimento"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "impiegata amministrativa",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "descrizione del mestiere"
      },
      {
       "surrogate": "Molino Capecchi S.r.l.",
       "value": "Ortelli Logistica",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda di impiego"
      },
      {
       "surrogate": "€ 772,00",
       "value": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "importo mensile della rata"
      },
      {
       "surrogate": "5 novembre 2026",
       "value": "20 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di scadenza"
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Caprioli,\n\nla ringraziamo per averci comunicato la variazione del conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornamento dell’IBAN per l’addebito della rata del prestito personale (€ 772,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT89Y0000025613651127989360** con il nuovo **IT77V0000094829785481207069** a partire dal prossimo addebito.\n\nPer completare l’operazione è necessario verificare la sua identità. Se desidera inviarci una copia scannerizzata della sua firma e del documento di identità, può farlo rispondendo a questa email allegando i file. In alternativa, può recarsi presso la filiale di Vercelli entro il 5 novembre 2026 per consegnare la firma in originale; in tal caso il nostro sportello sarà a sua disposizione.\n\nLe confermiamo che, una volta ricevuta la documentazione necessaria, l’aggiornamento sarà effettuato entro 48 ore lavorative, garantendo così il corretto addebito della rata di dicembre.\n\nPer qualsiasi ulteriore chiarimento o necessità, non esiti a contattarci al numero 0321 123 456 o via email all’indirizzo assistenza@creditocooperativovaldrada.it.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n**Credito Cooperativo Valdarda**  \nFiliale di Vercelli  \nVia Roma, 12 – 13012 Vercelli (VC)  \nTel. 0321 123 456 – Fax 0321 123 457  \nemail: assistenza@creditocooperativovaldrada.it  \n\n---  \n\n*Nota: nella sua comunicazione è indicato il ruolo di [RUOLO_1]; la informiamo che tale informazione è stata registrata così com’è.*",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Caprioli,\n\nla ringraziamo per averci comunicato la variazione del conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornamento dell’IBAN per l’addebito della rata del prestito personale (€ 320,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT89Y0000025613651127989360** con il nuovo **IT77V0000094829785481207069** a partire dal prossimo addebito.\n\nPer completare l’operazione è necessario verificare la sua identità. Se desidera inviarci una copia scannerizzata della sua firma e del documento di identità, può farlo rispondendo a questa email allegando i file. In alternativa, può recarsi presso la filiale di Bergamo entro il 20 novembre 2026 per consegnare la firma in originale; in tal caso il nostro sportello sarà a sua disposizione.\n\nLe confermiamo che, una volta ricevuta la documentazione necessaria, l’aggiornamento sarà effettuato entro 48 ore lavorative, garantendo così il corretto addebito della rata di dicembre.\n\nPer qualsiasi ulteriore chiarimento o necessità, non esiti a contattarci al numero 0321 123 456 o via email all’indirizzo assistenza@creditocooperativovaldrada.it.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n**Banca Corvalli**  \nFiliale di Bergamo  \nVia Roma, 12 – 13012 Bergamo (VC)  \nTel. 0321 123 456 – Fax 0321 123 457  \nemail: assistenza@creditocooperativovaldrada.it  \n\n---  \n\n*Nota: nella sua comunicazione è indicato il ruolo di impiegata amministrativa; la informiamo che tale informazione è stata registrata così com’è.*",
     "events": [
      {
       "surrogate": "Credito Cooperativo Valdarda",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Vercelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "10 dicembre 2026",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Molino Capecchi S.r.l.",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "€ 772,00",
       "outcome": "restored",
       "found_as": "€ 772,00"
      },
      {
       "surrogate": "5 novembre 2026",
       "outcome": "restored",
       "found_as": "5 novembre 2026"
      }
     ],
     "fully_restored": true,
     "run_id": "78d5c21f1f74"
    },
    "D4+R1": {
     "spans": [
      {
       "start": 60,
       "end": 74,
       "text": "Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 82,
       "end": 96,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 130,
       "end": 137,
       "text": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 143,
       "end": 158,
       "text": "1 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 188,
       "end": 212,
       "text": "impiegata amministrativa",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 220,
       "end": 237,
       "text": "Ortelli Logistica",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 365,
       "end": 373,
       "text": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 411,
       "end": 438,
       "text": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 452,
       "end": 479,
       "text": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 537,
       "end": 553,
       "text": "CPRLDI84S52X537Z",
       "type": "CF",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 624,
       "end": 640,
       "text": "20 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 732,
       "end": 744,
       "text": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 766,
       "end": 792,
       "text": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 812,
       "end": 826,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile [AZIENDA_1],\n\nsono [PERSONA_1_F], cliente della vostra filiale di [CITTA_1]. Dal [DATA_1] lo stipendio che ricevo come [RUOLO_1] presso [AZIENDA_2] S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a [IMPORTO_1] al mese, sostituendo il vecchio IBAN [IBAN_1] con il nuovo [IBAN_2].\n\nPer l'identificazione vi indico il mio codice fiscale, [CF_1]. Se servisse una firma in originale posso passare in filiale entro il [DATA_2], così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al [TELEFONO_1] oppure all'indirizzo [EMAIL_1].\n\nCordiali saluti,\n[PERSONA_1_F]\n",
     "disclosure": [
      {
       "surrogate": "[AZIENDA_1]",
       "value": "Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'istituto bancario"
      },
      {
       "surrogate": "[PERSONA_1_F]",
       "value": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località della filiale"
      },
      {
       "surrogate": "[DATA_1]",
       "value": "1 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di riferimento"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "impiegata amministrativa",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "descrizione del mestiere"
      },
      {
       "surrogate": "[AZIENDA_2]",
       "value": "Ortelli Logistica",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda di impiego"
      },
      {
       "surrogate": "[IMPORTO_1]",
       "value": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "importo mensile della rata"
      },
      {
       "surrogate": "[IBAN_1]",
       "value": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[IBAN_2]",
       "value": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[CF_1]",
       "value": "CPRLDI84S52X537Z",
       "type": "CF",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[DATA_2]",
       "value": "20 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di scadenza"
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile [PERSONA_1_F],\n\nla ringraziamo per averci comunicato la variazione dei dati di accredito.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale di [IMPORTO_1] al mese, sostituendo il vecchio IBAN [IBAN_1] con il nuovo [IBAN_2]. Provvederemo a effettuare la modifica entro i prossimi giorni, in modo da garantire il corretto addebito della rata di dicembre.\n\nPer completare l’operazione è necessario verificare la sua identità. Se preferisce, può recarsi presso la filiale di [CITTA_1] entro il [DATA_2] per firmare il modulo di autorizzazione in originale. In alternativa, può inviarci una copia scannerizzata della sua firma accompagnata da un documento di identità valido; in tal caso la procedura verrà completata entro 48 ore dalla ricezione.\n\nNel frattempo, le confermiamo che il suo codice fiscale [CF_1] è stato correttamente associato al profilo cliente.\n\nPer qualsiasi ulteriore chiarimento o per concordare un appuntamento in filiale, non esiti a contattarci al [TELEFONO_1] o via email all’indirizzo [EMAIL_1].\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n[AZIENDA_1] – Servizio Clienti  \n[AZIENDA_1]  \n[TELEFONO_1]  \n[EMAIL_1]  ",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione dei dati di accredito.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornare l’IBAN per l’addebito della rata del prestito personale di € 320,00 al mese, sostituendo il vecchio IBAN IT89Y0000025613651127989360 con il nuovo IT77V0000094829785481207069. Provvederemo a effettuare la modifica entro i prossimi giorni, in modo da garantire il corretto addebito della rata di dicembre.\n\nPer completare l’operazione è necessario verificare la sua identità. Se preferisce, può recarsi presso la filiale di Bergamo entro il 20 novembre 2026 per firmare il modulo di autorizzazione in originale. In alternativa, può inviarci una copia scannerizzata della sua firma accompagnata da un documento di identità valido; in tal caso la procedura verrà completata entro 48 ore dalla ricezione.\n\nNel frattempo, le confermiamo che il suo codice fiscale CPRLDI84S52X537Z è stato correttamente associato al profilo cliente.\n\nPer qualsiasi ulteriore chiarimento o per concordare un appuntamento in filiale, non esiti a contattarci al 347 215 8890 o via email all’indirizzo lidia.caprioli@example.com.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\nBanca Corvalli – Servizio Clienti  \nBanca Corvalli  \n347 215 8890  \nlidia.caprioli@example.com  ",
     "events": [
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_1_F]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CF_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "933a73c866b3"
    },
    "D4+R2": {
     "spans": [
      {
       "start": 60,
       "end": 74,
       "text": "Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 82,
       "end": 96,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 130,
       "end": 137,
       "text": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 143,
       "end": 158,
       "text": "1 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 188,
       "end": 212,
       "text": "impiegata amministrativa",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 220,
       "end": 237,
       "text": "Ortelli Logistica",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 365,
       "end": 373,
       "text": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 411,
       "end": 438,
       "text": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 452,
       "end": 479,
       "text": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 537,
       "end": 553,
       "text": "CPRLDI84S52X537Z",
       "type": "CF",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 624,
       "end": 640,
       "text": "20 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 732,
       "end": 744,
       "text": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 766,
       "end": 792,
       "text": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 812,
       "end": 826,
       "text": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: variazione IBAN per l'addebito della rata\n\nGentile Credito Cooperativo Valdarda,\n\nsono Mafalda Marangoni, cliente della vostra filiale di Vercelli. Dal 10 dicembre 2026 lo stipendio che ricevo come [RUOLO_1] presso Molino Capecchi S.r.l. S.r.l. sarà accreditato su un nuovo conto. Vi chiedo quindi di aggiornare l'addebito della rata del prestito personale, pari a € 772,00 al mese, sostituendo il vecchio IBAN IT81O0000010618943216096700 con il nuovo IT30G0000096742150185432543.\n\nPer l'identificazione vi indico il mio codice fiscale, ZMRFNL15S45X523C. Se servisse una firma in originale posso passare in filiale entro il 5 novembre 2026, così da non saltare la rata di dicembre.\n\nPer qualsiasi chiarimento potete contattarmi al 353 104 8748 oppure all'indirizzo ersilia.camporesi@example.com.\n\nCordiali saluti,\nMafalda Marangoni\n",
     "disclosure": [
      {
       "surrogate": "Credito Cooperativo Valdarda",
       "value": "Banca Corvalli",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'istituto bancario"
      },
      {
       "surrogate": "Mafalda Marangoni",
       "value": "Lidia Caprioli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Vercelli",
       "value": "Bergamo",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località della filiale"
      },
      {
       "surrogate": "10 dicembre 2026",
       "value": "1 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di riferimento"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "impiegata amministrativa",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "descrizione del mestiere"
      },
      {
       "surrogate": "Molino Capecchi S.r.l.",
       "value": "Ortelli Logistica",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda di impiego"
      },
      {
       "surrogate": "€ 772,00",
       "value": "€ 320,00",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "importo mensile della rata"
      },
      {
       "surrogate": "IT81O0000010618943216096700",
       "value": "IT89Y0000025613651127989360",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "IT30G0000096742150185432543",
       "value": "IT77V0000094829785481207069",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "ZMRFNL15S45X523C",
       "value": "CPRLDI84S52X537Z",
       "type": "CF",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "5 novembre 2026",
       "value": "20 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di scadenza"
      },
      {
       "surrogate": "353 104 8748",
       "value": "347 215 8890",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "ersilia.camporesi@example.com",
       "value": "lidia.caprioli@example.com",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Mafalda Marangoni,\n\nla ringraziamo per averci comunicato la variazione del conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornamento dell’IBAN per l’addebito della rata del prestito personale (€ 772,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT81O0000010618943216096700** con il nuovo **IT30G0000096742150185432543** a partire dal prossimo addebito.\n\nPer completare l’operazione, le chiediamo gentilmente di inviarci, entro il **5 novembre 2026**, una copia del suo documento di identità e, se necessario, la firma originale del modulo di variazione IBAN. Può recarsi presso la filiale di Vercelli oppure inviare i documenti in formato digitale (PDF) all’indirizzo email **servizio.clienti@creditocooperativovaldera.it**.\n\nNel frattempo, la rata di dicembre verrà comunque addebitata sul nuovo conto, così da evitare interruzioni nei pagamenti.\n\nPer qualsiasi ulteriore chiarimento o per fissare un appuntamento in filiale, non esiti a contattarci al numero **+39 015 123 4567** o via email all’indirizzo sopra indicato.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n**Credito Cooperativo Valdarda**  \nServizio Clienti – Filiale di Vercelli  \nVia Roma, 12 – 13012 Vercelli (VC)  \nTel. +39 015 123 4567 – email: servizio.clienti@creditocooperativovaldera.it  \n\n---  \n\n*Nota: la sua qualifica è indicata come **[RUOLO_1]** nella sua comunicazione.*",
     "restored": "**Oggetto:** Re: variazione IBAN per l'addebito della rata  \n\nGentile Sig.ra Lidia Caprioli,\n\nla ringraziamo per averci comunicato la variazione del conto corrente.\n\nConfermiamo di aver ricevuto la sua richiesta di aggiornamento dell’IBAN per l’addebito della rata del prestito personale (€ 320,00 mensili). Provvederemo a sostituire l’attuale IBAN **IT89Y0000025613651127989360** con il nuovo **IT77V0000094829785481207069** a partire dal prossimo addebito.\n\nPer completare l’operazione, le chiediamo gentilmente di inviarci, entro il **20 novembre 2026**, una copia del suo documento di identità e, se necessario, la firma originale del modulo di variazione IBAN. Può recarsi presso la filiale di Bergamo oppure inviare i documenti in formato digitale (PDF) all’indirizzo email **servizio.clienti@creditocooperativovaldera.it**.\n\nNel frattempo, la rata di dicembre verrà comunque addebitata sul nuovo conto, così da evitare interruzioni nei pagamenti.\n\nPer qualsiasi ulteriore chiarimento o per fissare un appuntamento in filiale, non esiti a contattarci al numero **+39 015 123 4567** o via email all’indirizzo sopra indicato.\n\nRestiamo a disposizione e le porgiamo cordiali saluti.\n\n**Banca Corvalli**  \nServizio Clienti – Filiale di Bergamo  \nVia Roma, 12 – 13012 Bergamo (VC)  \nTel. +39 015 123 4567 – email: servizio.clienti@creditocooperativovaldera.it  \n\n---  \n\n*Nota: la sua qualifica è indicata come **impiegata amministrativa** nella sua comunicazione.*",
     "events": [
      {
       "surrogate": "Credito Cooperativo Valdarda",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Mafalda Marangoni",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Vercelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "10 dicembre 2026",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Molino Capecchi S.r.l.",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "€ 772,00",
       "outcome": "restored",
       "found_as": "€ 772,00"
      },
      {
       "surrogate": "IT81O0000010618943216096700",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "IT30G0000096742150185432543",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "ZMRFNL15S45X523C",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "5 novembre 2026",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "353 104 8748",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "ersilia.camporesi@example.com",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "65b4d39c07a9"
    }
   },
   "calc_blocked": {
    "D0": {
     "IMPORTO": 1
    },
    "D1": {},
    "D2": {},
    "D3": {
     "IMPORTO": 1,
     "DATA": 2
    },
    "D4": {
     "IMPORTO": 1,
     "DATA": 2
    }
   }
  },
  {
   "id": "fx-bank-02",
   "domain": "bank",
   "scenario": "card_dispute",
   "text": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo Bruno Ferraguti e sono titolare di una carta di debito collegata al conto IT87L0000085047953541165689. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: 89,90 euro il 3 novembre 2026 e 245,00 euro il 5 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a Cagliari per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come tecnico manutentore per Sardelec Impianti e sono spesso in trasferta, quindi vi prego di scrivermi a b.ferraguti@example.net o di chiamarmi al +39 328 664 1027 dopo le 18.\n\nHo 52 anni e sono cliente della filiale di Oristano da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\nBruno Ferraguti\n",
   "runs": {
    "D0+R1": {
     "spans": [
      {
       "start": 150,
       "end": 177,
       "text": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 261,
       "end": 271,
       "text": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0"
      },
      {
       "start": 293,
       "end": 304,
       "text": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0"
      },
      {
       "start": 662,
       "end": 685,
       "text": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 704,
       "end": 720,
       "text": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo Bruno Ferraguti e sono titolare di una carta di debito collegata al conto [IBAN_1]. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: [IMPORTO_1] il 3 novembre 2026 e [IMPORTO_2] il 5 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a Cagliari per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come tecnico manutentore per Sardelec Impianti e sono spesso in trasferta, quindi vi prego di scrivermi a [EMAIL_1] o di chiamarmi al [TELEFONO_1] dopo le 18.\n\nHo 52 anni e sono cliente della filiale di Oristano da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\nBruno Ferraguti\n",
     "disclosure": [
      {
       "surrogate": "[IBAN_1]",
       "value": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "value": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[IMPORTO_2]",
       "value": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nBuongiorno Sig. Ferraguti,\n\nla ringraziamo per averci segnalato la situazione e per aver già provveduto a bloccare la carta tramite l’app.\n\nConfermiamo di aver aperto la pratica di contestazione per i due addebiti indicati:\n\n- **[IMPORTO_1]** – 3 novembre 2026  \n- **[IMPORTO_2]** – 5 novembre 2026  \n\nStiamo avviando le verifiche necessarie con il nostro dipartimento frodi e con il negozio online coinvolto. Le chiediamo di fornirci, se disponibile, eventuali ulteriori dettagli (ad esempio eventuali screenshot dell’estratto conto o della notifica di pagamento) che possano agevolare la ricerca.\n\nLe confermiamo che, qualora la contestazione dovesse risultare fondata, provvederemo allo storno degli importi entro i termini previsti dalla normativa vigente.\n\nPer qualsiasi aggiornamento la contatteremo via e‑mail all’indirizzo **[EMAIL_1]** e, se necessario, la chiameremo al **[TELEFONO_1]** dopo le ore 18:00, come da sua preferenza.\n\nNel frattempo, le consigliamo di monitorare l’estratto conto e di segnalare eventuali ulteriori movimenti sospetti. Se dovesse necessitare di una nuova carta, provvederemo a inviarne una di sostituzione al più presto.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento.\n\nCordiali saluti,\n\n[Nome Cognome]  \nServizio Clienti – [Nome Banca]  \nTelefono: [NUMERO_TEL_BANCA]  \nE‑mail: assistenza@[DOMINIO_BANCA].it  \nOristano – Filiale di riferimento  \n\n---  \n\n*Nota: questa è una bozza di risposta. Prima dell’invio, verificare i dati del mittente e inserire le informazioni mancanti (nome, cognome, numero di telefono della banca, dominio e eventuali altri riferimenti interni).*",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nBuongiorno Sig. Ferraguti,\n\nla ringraziamo per averci segnalato la situazione e per aver già provveduto a bloccare la carta tramite l’app.\n\nConfermiamo di aver aperto la pratica di contestazione per i due addebiti indicati:\n\n- **89,90 euro** – 3 novembre 2026  \n- **245,00 euro** – 5 novembre 2026  \n\nStiamo avviando le verifiche necessarie con il nostro dipartimento frodi e con il negozio online coinvolto. Le chiediamo di fornirci, se disponibile, eventuali ulteriori dettagli (ad esempio eventuali screenshot dell’estratto conto o della notifica di pagamento) che possano agevolare la ricerca.\n\nLe confermiamo che, qualora la contestazione dovesse risultare fondata, provvederemo allo storno degli importi entro i termini previsti dalla normativa vigente.\n\nPer qualsiasi aggiornamento la contatteremo via e‑mail all’indirizzo **b.ferraguti@example.net** e, se necessario, la chiameremo al **+39 328 664 1027** dopo le ore 18:00, come da sua preferenza.\n\nNel frattempo, le consigliamo di monitorare l’estratto conto e di segnalare eventuali ulteriori movimenti sospetti. Se dovesse necessitare di una nuova carta, provvederemo a inviarne una di sostituzione al più presto.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento.\n\nCordiali saluti,\n\n[Nome Cognome]  \nServizio Clienti – [Nome Banca]  \nTelefono: [NUMERO_TEL_BANCA]  \nE‑mail: assistenza@[DOMINIO_BANCA].it  \nOristano – Filiale di riferimento  \n\n---  \n\n*Nota: questa è una bozza di risposta. Prima dell’invio, verificare i dati del mittente e inserire le informazioni mancanti (nome, cognome, numero di telefono della banca, dominio e eventuali altri riferimenti interni).*",
     "events": [
      {
       "surrogate": "[IBAN_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "a3c06360ce07"
    },
    "D0+R2": {
     "spans": [
      {
       "start": 150,
       "end": 177,
       "text": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 261,
       "end": 271,
       "text": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0"
      },
      {
       "start": 293,
       "end": 304,
       "text": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0"
      },
      {
       "start": 662,
       "end": 685,
       "text": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 704,
       "end": 720,
       "text": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo Bruno Ferraguti e sono titolare di una carta di debito collegata al conto IT13O0000021305665919329463. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: 82,90 euro il 3 novembre 2026 e 225,00 euro il 5 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a Cagliari per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come tecnico manutentore per Sardelec Impianti e sono spesso in trasferta, quindi vi prego di scrivermi a manfredi.dalmasso@example.com o di chiamarmi al +39 320 262 6271 dopo le 18.\n\nHo 52 anni e sono cliente della filiale di Oristano da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\nBruno Ferraguti\n",
     "disclosure": [
      {
       "surrogate": "IT13O0000021305665919329463",
       "value": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "82,90 euro",
       "value": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "225,00 euro",
       "value": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "manfredi.dalmasso@example.com",
       "value": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "+39 320 262 6271",
       "value": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nBuongiorno Sig. Ferraguti,\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul suo conto corrente **IT13O0000021305665919329463**.\n\nConfermiamo di aver ricevuto la sua segnalazione relativa ai seguenti movimenti:\n\n| Data | Importo | Descrizione |\n|------|---------|-------------|\n| 3 novembre 2026 | € 82,90 | Negozio online non riconosciuto |\n| 5 novembre 2026 | € 225,00 | Negozio online non riconosciuto |\n\nAbbiamo provveduto a:\n\n1. **Bloccare definitivamente la carta di debito** già segnalata tramite l’app, per evitare ulteriori utilizzi non autorizzati.  \n2. **Avviare la pratica di contestazione** degli addebiti indicati, in conformità con le normative vigenti in materia di pagamenti elettronici.  \n3. **Richiedere al nostro dipartimento di frodi** l’avvio di un’indagine approfondita per verificare l’origine di tali transazioni.\n\nLe confermiamo che, una volta completata l’analisi, provvederemo al **rimborso integrale** degli importi contestati, qualora la contestazione venga accolta.\n\n**Prossimi passi**\n\n- **Tempistiche:** la procedura di verifica richiede generalmente 7‑10 giorni lavorativi. Le forniremo un aggiornamento non appena avremo ulteriori informazioni.  \n- **Documentazione:** qualora fossero necessari ulteriori dettagli (es. copia di eventuali comunicazioni ricevute dal negozio online, screenshot dell’app, ecc.), la contatteremo direttamente.  \n- **Contatti:** per qualsiasi chiarimento o per fornire documentazione aggiuntiva, può rispondere a questa email oppure contattarci telefonicamente al **+39 06 1234 5678** (orario 9:00‑19:00). Come richiesto, le invieremo una comunicazione scritta anche al suo indirizzo email **manfredi.dalmasso@example.com** e la chiameremo al **+39 320 262 6271** dopo le ore 18:00.\n\nNel frattempo, le consigliamo di monitorare regolarmente l’estratto conto e di segnalare immediatamente eventuali ulteriori movimenti sospetti.\n\nRestiamo a sua completa disposizione per ogni ulteriore necessità e le porgiamo i nostri più cordiali saluti.\n\n---\n\n**Servizio Clienti – Banca XYZ**  \nFiliale di Oristano  \nTelefono: +39 06 1234 5678  \nEmail: assistenza@bancaxyz.it  \nOrario di assistenza: lun‑ven 8:00‑20:00, sab 9:00‑14:00  ",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nBuongiorno Sig. Ferraguti,\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul suo conto corrente **IT87L0000085047953541165689**.\n\nConfermiamo di aver ricevuto la sua segnalazione relativa ai seguenti movimenti:\n\n| Data | Importo | Descrizione |\n|------|---------|-------------|\n| 3 novembre 2026 | 89,90 euro | Negozio online non riconosciuto |\n| 5 novembre 2026 | 245,00 euro | Negozio online non riconosciuto |\n\nAbbiamo provveduto a:\n\n1. **Bloccare definitivamente la carta di debito** già segnalata tramite l’app, per evitare ulteriori utilizzi non autorizzati.  \n2. **Avviare la pratica di contestazione** degli addebiti indicati, in conformità con le normative vigenti in materia di pagamenti elettronici.  \n3. **Richiedere al nostro dipartimento di frodi** l’avvio di un’indagine approfondita per verificare l’origine di tali transazioni.\n\nLe confermiamo che, una volta completata l’analisi, provvederemo al **rimborso integrale** degli importi contestati, qualora la contestazione venga accolta.\n\n**Prossimi passi**\n\n- **Tempistiche:** la procedura di verifica richiede generalmente 7‑10 giorni lavorativi. Le forniremo un aggiornamento non appena avremo ulteriori informazioni.  \n- **Documentazione:** qualora fossero necessari ulteriori dettagli (es. copia di eventuali comunicazioni ricevute dal negozio online, screenshot dell’app, ecc.), la contatteremo direttamente.  \n- **Contatti:** per qualsiasi chiarimento o per fornire documentazione aggiuntiva, può rispondere a questa email oppure contattarci telefonicamente al **+39 06 1234 5678** (orario 9:00‑19:00). Come richiesto, le invieremo una comunicazione scritta anche al suo indirizzo email **b.ferraguti@example.net** e la chiameremo al **+39 328 664 1027** dopo le ore 18:00.\n\nNel frattempo, le consigliamo di monitorare regolarmente l’estratto conto e di segnalare immediatamente eventuali ulteriori movimenti sospetti.\n\nRestiamo a sua completa disposizione per ogni ulteriore necessità e le porgiamo i nostri più cordiali saluti.\n\n---\n\n**Servizio Clienti – Banca XYZ**  \nFiliale di Oristano  \nTelefono: +39 06 1234 5678  \nEmail: assistenza@bancaxyz.it  \nOrario di assistenza: lun‑ven 8:00‑20:00, sab 9:00‑14:00  ",
     "events": [
      {
       "surrogate": "IT13O0000021305665919329463",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "82,90 euro",
       "outcome": "restored",
       "found_as": "€ 82,90"
      },
      {
       "surrogate": "225,00 euro",
       "outcome": "restored",
       "found_as": "€ 225,00"
      },
      {
       "surrogate": "manfredi.dalmasso@example.com",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "+39 320 262 6271",
       "outcome": "restored",
       "found_as": "+39 320 262 6271"
      }
     ],
     "fully_restored": true,
     "run_id": "1f4b787b41ab"
    },
    "D1+R1": {
     "spans": [
      {
       "start": 53,
       "end": 63,
       "text": "Buongiorno",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 76,
       "end": 91,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 150,
       "end": 177,
       "text": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 393,
       "end": 401,
       "text": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 585,
       "end": 602,
       "text": "Sardelec Impianti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 662,
       "end": 685,
       "text": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 704,
       "end": 720,
       "text": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 777,
       "end": 785,
       "text": "Oristano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 885,
       "end": 900,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\n[CITTA_1],\n\nmi chiamo [PERSONA_1_M] e sono titolare di una carta di debito collegata al conto [IBAN_1]. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: 89,90 euro il 3 novembre 2026 e 245,00 euro il 5 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a [CITTA_2] per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come tecnico manutentore per [PERSONA_2] e sono spesso in trasferta, quindi vi prego di scrivermi a [EMAIL_1] o di chiamarmi al [TELEFONO_1] dopo le 18.\n\nHo 52 anni e sono cliente della filiale di [CITTA_3] da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\n[PERSONA_1_M]\n",
     "disclosure": [
      {
       "surrogate": "[CITTA_1]",
       "value": "Buongiorno",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_1_M]",
       "value": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "value": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_2]",
       "value": "Sardelec Impianti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_3]",
       "value": "Oristano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile [PERSONA_1_M],\n\nla ringraziamo per averci segnalato la situazione e per aver provveduto a bloccare la carta tramite l’app.  \n\nAbbiamo aperto la pratica di contestazione per gli addebiti da € 89,90 (3 novembre 2026) e € 245,00 (5 novembre 2026) effettuati da un negozio online a noi non identificato.  \n\nPer poter procedere con lo storno degli importi, le chiediamo gentilmente di inviarci, entro 5 giorni lavorativi, i seguenti documenti:\n\n1. Copia dell’estratto conto in cui compaiono gli addebiti contestati.  \n2. Eventuale comunicazione o ricevuta che attesti la sua presenza a [CITTA_2] nei giorni indicati.  \n3. Una breve dichiarazione firmata in cui conferma di non aver autorizzato tali operazioni.\n\nPuò inviare la documentazione via email all’indirizzo [EMAIL_1] oppure, se preferisce, caricarla in modo sicuro tramite il nostro servizio di messaggistica protetta disponibile nell’app.\n\nUna volta ricevuti i documenti, il nostro ufficio frodi avvierà le verifiche necessarie e le comunicherà l’esito entro 10 giorni lavorativi. In caso di esito positivo, provvederemo allo storno degli importi sul suo conto [IBAN_1] e le invieremo una conferma scritta.\n\nNel frattempo, la informiamo che la sua carta è stata disattivata e le verrà inviata una nuova carta di debito entro 7 giorni lavorativi. La preghiamo di attivarla non appena la riceverà.\n\nPer qualsiasi ulteriore chiarimento o per parlare direttamente con un nostro operatore, la contatteremo al numero [TELEFONO_1] dopo le ore 18:00, come da sua richiesta. Se preferisce, può anche fissare un appuntamento presso la filiale di [CITTA_3] chiamando il numero 800 123 456.\n\nRestiamo a disposizione per ogni ulteriore necessità e ci scusiamo per il disagio arrecato.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \n[Nome Banca] – Filiale di [CITTA_3]  \nTelefono: 800 123 456  \nEmail: assistenza@[DOMINIO_BANCA].it  ",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Bruno Ferraguti,\n\nla ringraziamo per averci segnalato la situazione e per aver provveduto a bloccare la carta tramite l’app.  \n\nAbbiamo aperto la pratica di contestazione per gli addebiti da € 89,90 (3 novembre 2026) e € 245,00 (5 novembre 2026) effettuati da un negozio online a noi non identificato.  \n\nPer poter procedere con lo storno degli importi, le chiediamo gentilmente di inviarci, entro 5 giorni lavorativi, i seguenti documenti:\n\n1. Copia dell’estratto conto in cui compaiono gli addebiti contestati.  \n2. Eventuale comunicazione o ricevuta che attesti la sua presenza a Cagliari nei giorni indicati.  \n3. Una breve dichiarazione firmata in cui conferma di non aver autorizzato tali operazioni.\n\nPuò inviare la documentazione via email all’indirizzo b.ferraguti@example.net oppure, se preferisce, caricarla in modo sicuro tramite il nostro servizio di messaggistica protetta disponibile nell’app.\n\nUna volta ricevuti i documenti, il nostro ufficio frodi avvierà le verifiche necessarie e le comunicherà l’esito entro 10 giorni lavorativi. In caso di esito positivo, provvederemo allo storno degli importi sul suo conto IT87L0000085047953541165689 e le invieremo una conferma scritta.\n\nNel frattempo, la informiamo che la sua carta è stata disattivata e le verrà inviata una nuova carta di debito entro 7 giorni lavorativi. La preghiamo di attivarla non appena la riceverà.\n\nPer qualsiasi ulteriore chiarimento o per parlare direttamente con un nostro operatore, la contatteremo al numero +39 328 664 1027 dopo le ore 18:00, come da sua richiesta. Se preferisce, può anche fissare un appuntamento presso la filiale di Oristano chiamando il numero 800 123 456.\n\nRestiamo a disposizione per ogni ulteriore necessità e ci scusiamo per il disagio arrecato.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \n[Nome Banca] – Filiale di Oristano  \nTelefono: 800 123 456  \nEmail: assistenza@[DOMINIO_BANCA].it  ",
     "events": [
      {
       "surrogate": "[CITTA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_1_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_3]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "49f599e17121"
    },
    "D1+R2": {
     "spans": [
      {
       "start": 53,
       "end": 63,
       "text": "Buongiorno",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 76,
       "end": 91,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 150,
       "end": 177,
       "text": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 393,
       "end": 401,
       "text": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 585,
       "end": 602,
       "text": "Sardelec Impianti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 662,
       "end": 685,
       "text": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 704,
       "end": 720,
       "text": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 777,
       "end": 785,
       "text": "Oristano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 885,
       "end": 900,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nRovigo,\n\nmi chiamo Leandro Zambelli e sono titolare di una carta di debito collegata al conto IT13O0000021305665919329463. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: 89,90 euro il 3 novembre 2026 e 245,00 euro il 5 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a Savona per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come tecnico manutentore per Saverio Montagnani e sono spesso in trasferta, quindi vi prego di scrivermi a manfredi.dalmasso@example.com o di chiamarmi al +39 320 262 6271 dopo le 18.\n\nHo 52 anni e sono cliente della filiale di Biella da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\nLeandro Zambelli\n",
     "disclosure": [
      {
       "surrogate": "Rovigo",
       "value": "Buongiorno",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Leandro Zambelli",
       "value": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "IT13O0000021305665919329463",
       "value": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Savona",
       "value": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Saverio Montagnani",
       "value": "Sardelec Impianti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "manfredi.dalmasso@example.com",
       "value": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "+39 320 262 6271",
       "value": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Biella",
       "value": "Oristano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Sig. Leandro Zambelli,\n\nla ringraziamo per averci segnalato la situazione e per aver provveduto a bloccare la carta tramite l’app.  \n\nAbbiamo aperto la pratica di contestazione per i due addebiti indicati:\n\n| Data | Importo | Descrizione |\n|------|---------|-------------|\n| 3 novembre 2026 | € 89,90 | Negozio online non riconosciuto |\n| 5 novembre 2026 | € 245,00 | Negozio online non riconosciuto |\n\n**Procedura in corso**  \n1. **Verifica delle transazioni** – il nostro dipartimento frodi sta analizzando i movimenti per accertare l’origine degli addebiti.  \n2. **Storno provvisorio** – provvederemo a bloccare gli importi contestati sul suo conto, in attesa dell’esito dell’indagine.  \n3. **Comunicazione dei risultati** – entro 10 giorni lavorativi le invieremo una conferma scritta dell’esito della contestazione e, se confermata l’illegittimità, il rimborso sarà accreditato sul suo conto entro 5 giorni lavorativi successivi.  \n\n**Contatti**  \nCome richiesto, le risponderemo via e‑mail all’indirizzo **manfredi.dalmasso@example.com** e, se necessario, la contatteremo telefonicamente al **+39 320 262 6271** dopo le ore 18:00.\n\nNel frattempo, le consigliamo di monitorare l’estratto conto e di segnalare eventuali ulteriori movimenti sospetti. Qualora dovesse ricevere nuove comunicazioni da parte del negozio online o da terzi, la preghiamo di inoltrarcele immediatamente.\n\nRestiamo a disposizione per qualsiasi ulteriore chiarimento e la ringraziamo per la fiducia riposta nella nostra filiale di Biella, dove è cliente da più di vent’anni.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti – Filiale di Biella  \n[Telefono filiale] – [e‑mail filiale]  \nBanca [Nome Banca]  \n\n---  \n\n*Nota:* Questa è una bozza di risposta. Prima dell’invio, verificare i dati di contatto del mittente e inserire eventuali riferimenti interni (numero pratica, codice operatore, ecc.).",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Sig. Bruno Ferraguti,\n\nla ringraziamo per averci segnalato la situazione e per aver provveduto a bloccare la carta tramite l’app.  \n\nAbbiamo aperto la pratica di contestazione per i due addebiti indicati:\n\n| Data | Importo | Descrizione |\n|------|---------|-------------|\n| 3 novembre 2026 | € 89,90 | Negozio online non riconosciuto |\n| 5 novembre 2026 | € 245,00 | Negozio online non riconosciuto |\n\n**Procedura in corso**  \n1. **Verifica delle transazioni** – il nostro dipartimento frodi sta analizzando i movimenti per accertare l’origine degli addebiti.  \n2. **Storno provvisorio** – provvederemo a bloccare gli importi contestati sul suo conto, in attesa dell’esito dell’indagine.  \n3. **Comunicazione dei risultati** – entro 10 giorni lavorativi le invieremo una conferma scritta dell’esito della contestazione e, se confermata l’illegittimità, il rimborso sarà accreditato sul suo conto entro 5 giorni lavorativi successivi.  \n\n**Contatti**  \nCome richiesto, le risponderemo via e‑mail all’indirizzo **b.ferraguti@example.net** e, se necessario, la contatteremo telefonicamente al **+39 328 664 1027** dopo le ore 18:00.\n\nNel frattempo, le consigliamo di monitorare l’estratto conto e di segnalare eventuali ulteriori movimenti sospetti. Qualora dovesse ricevere nuove comunicazioni da parte del negozio online o da terzi, la preghiamo di inoltrarcele immediatamente.\n\nRestiamo a disposizione per qualsiasi ulteriore chiarimento e la ringraziamo per la fiducia riposta nella nostra filiale di Oristano, dove è cliente da più di vent’anni.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti – Filiale di Oristano  \n[Telefono filiale] – [e‑mail filiale]  \nBanca [Nome Banca]  \n\n---  \n\n*Nota:* Questa è una bozza di risposta. Prima dell’invio, verificare i dati di contatto del mittente e inserire eventuali riferimenti interni (numero pratica, codice operatore, ecc.).",
     "events": [
      {
       "surrogate": "Rovigo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Leandro Zambelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "IT13O0000021305665919329463",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Savona",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Saverio Montagnani",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "manfredi.dalmasso@example.com",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "+39 320 262 6271",
       "outcome": "restored",
       "found_as": "+39 320 262 6271"
      },
      {
       "surrogate": "Biella",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "1b498f032ac2"
    },
    "D2+R1": {
     "spans": [
      {
       "start": 76,
       "end": 91,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 393,
       "end": 401,
       "text": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 585,
       "end": 593,
       "text": "Sardelec",
       "type": "INDIRIZZO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 662,
       "end": 672,
       "text": "b.ferragut",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 704,
       "end": 720,
       "text": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 777,
       "end": 785,
       "text": "Oristano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 885,
       "end": 900,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo [PERSONA_1_M] e sono titolare di una carta di debito collegata al conto IT87L0000085047953541165689. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: 89,90 euro il 3 novembre 2026 e 245,00 euro il 5 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a [CITTA_1] per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come tecnico manutentore per [INDIRIZZO_1] Impianti e sono spesso in trasferta, quindi vi prego di scrivermi a [EMAIL_1]i@example.net o di chiamarmi al [TELEFONO_1] dopo le 18.\n\nHo 52 anni e sono cliente della filiale di [CITTA_2] da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\n[PERSONA_1_M]\n",
     "disclosure": [
      {
       "surrogate": "[PERSONA_1_M]",
       "value": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[INDIRIZZO_1]",
       "value": "Sardelec",
       "type": "INDIRIZZO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "b.ferragut",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Oristano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile [PERSONA_1_M],\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul suo conto **IT87L0000085047953541165689**.\n\nAbbiamo provveduto a:\n\n1. **Bloccare temporaneamente la carta** per evitare ulteriori transazioni non autorizzate.  \n2. **Aprire una pratica di contestazione** per gli importi di **€ 89,90** (3 novembre 2026) e **€ 245,00** (5 novembre 2026).  \n3. **Avviare l’indagine interna** con il nostro dipartimento frodi per verificare l’origine di tali transazioni.\n\nPer completare la procedura avremo bisogno dei seguenti documenti/informazioni aggiuntive:\n\n- Una copia di un documento di identità valido (carta d’identità o passaporto).  \n- Eventuali ricevute o comunicazioni relative a viaggi o spostamenti a [CITTA_1] nei giorni indicati, se disponibili.  \n- Conferma scritta dell’avvenuta segnalazione di blocco della carta tramite l’app (screenshot o numero di riferimento).\n\nPuò inviare i documenti in risposta a questa email oppure, se preferisce, caricarli in modo sicuro tramite il nostro servizio di upload disponibile nell’applicazione mobile.\n\nLe confermiamo che, una volta ricevuta la documentazione, provvederemo a:\n\n- Verificare la legittimità delle transazioni contestate.  \n- Stornare gli importi non riconosciuti, qualora la contestazione venga accolta.  \n- Emissione di una nuova carta di debito, se necessario.\n\nLe ricordiamo che il tempo medio di risoluzione di una pratica di contestazione è di **7‑10 giorni lavorativi**. Qualora fossero necessarie ulteriori informazioni, la contatteremo direttamente.\n\nCome richiesto, le invieremo tutti gli aggiornamenti all’indirizzo **[EMAIL_1]i@example.net** e la contatteremo telefonicamente al **[TELEFONO_1]** dopo le ore 18:00.\n\nRestiamo a disposizione per qualsiasi ulteriore chiarimento e la ringraziamo per la pazienza.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti – [Nome Banca]  \nFiliale di [CITTA_2]  \nTelefono: [NUMERO_FILIALE]  \nEmail: assistenza@[DOMINIO_BANCA].it  ",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Bruno Ferraguti,\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul suo conto **IT87L0000085047953541165689**.\n\nAbbiamo provveduto a:\n\n1. **Bloccare temporaneamente la carta** per evitare ulteriori transazioni non autorizzate.  \n2. **Aprire una pratica di contestazione** per gli importi di **€ 89,90** (3 novembre 2026) e **€ 245,00** (5 novembre 2026).  \n3. **Avviare l’indagine interna** con il nostro dipartimento frodi per verificare l’origine di tali transazioni.\n\nPer completare la procedura avremo bisogno dei seguenti documenti/informazioni aggiuntive:\n\n- Una copia di un documento di identità valido (carta d’identità o passaporto).  \n- Eventuali ricevute o comunicazioni relative a viaggi o spostamenti a Cagliari nei giorni indicati, se disponibili.  \n- Conferma scritta dell’avvenuta segnalazione di blocco della carta tramite l’app (screenshot o numero di riferimento).\n\nPuò inviare i documenti in risposta a questa email oppure, se preferisce, caricarli in modo sicuro tramite il nostro servizio di upload disponibile nell’applicazione mobile.\n\nLe confermiamo che, una volta ricevuta la documentazione, provvederemo a:\n\n- Verificare la legittimità delle transazioni contestate.  \n- Stornare gli importi non riconosciuti, qualora la contestazione venga accolta.  \n- Emissione di una nuova carta di debito, se necessario.\n\nLe ricordiamo che il tempo medio di risoluzione di una pratica di contestazione è di **7‑10 giorni lavorativi**. Qualora fossero necessarie ulteriori informazioni, la contatteremo direttamente.\n\nCome richiesto, le invieremo tutti gli aggiornamenti all’indirizzo **b.ferraguti@example.net** e la contatteremo telefonicamente al **+39 328 664 1027** dopo le ore 18:00.\n\nRestiamo a disposizione per qualsiasi ulteriore chiarimento e la ringraziamo per la pazienza.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti – [Nome Banca]  \nFiliale di Oristano  \nTelefono: [NUMERO_FILIALE]  \nEmail: assistenza@[DOMINIO_BANCA].it  ",
     "events": [
      {
       "surrogate": "[PERSONA_1_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[INDIRIZZO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "bd5400e9b707"
    },
    "D2+R2": {
     "spans": [
      {
       "start": 76,
       "end": 91,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 393,
       "end": 401,
       "text": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 585,
       "end": 593,
       "text": "Sardelec",
       "type": "INDIRIZZO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 662,
       "end": 672,
       "text": "b.ferragut",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 704,
       "end": 720,
       "text": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 777,
       "end": 785,
       "text": "Oristano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 885,
       "end": 900,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo Leandro Zambelli e sono titolare di una carta di debito collegata al conto IT87L0000085047953541165689. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: 89,90 euro il 3 novembre 2026 e 245,00 euro il 5 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a Rovigo per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come tecnico manutentore per via delle Querce 14 Impianti e sono spesso in trasferta, quindi vi prego di scrivermi a rachele.fiorucci@example.comi@example.net o di chiamarmi al +39 320 262 6271 dopo le 18.\n\nHo 52 anni e sono cliente della filiale di Biella da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\nLeandro Zambelli\n",
     "disclosure": [
      {
       "surrogate": "Leandro Zambelli",
       "value": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Rovigo",
       "value": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "via delle Querce 14",
       "value": "Sardelec",
       "type": "INDIRIZZO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "rachele.fiorucci@example.com",
       "value": "b.ferragut",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "+39 320 262 6271",
       "value": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Biella",
       "value": "Oristano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti – conto IT87L0000085047953541165689  \n\nGentile Sig. Zambelli,\n\nla ringraziamo per averci segnalato gli addebiti non autorizzati riscontrati sul suo estratto conto.\n\nConfermiamo di aver ricevuto la sua segnalazione relativa ai seguenti movimenti:\n\n| Data | Importo | Descrizione |\n|------|---------|-------------|\n| 3 novembre 2026 | € 89,90 | Negozio online non riconosciuto |\n| 5 novembre 2026 | € 245,00 | Negozio online non riconosciuto |\n\nAbbiamo già provveduto a:\n\n1. **Bloccare definitivamente la carta di debito** (la sostituzione le sarà inviata a breve).  \n2. **Aprire una pratica di contestazione** (numero di pratica: **[NUMERO_PRATICA]**).  \n\nIl nostro team di frodi avvierà le verifiche necessarie per accertare l’origine di tali transazioni. In genere la fase di analisi richiede **5‑7 giorni lavorativi**; al termine le comunicheremo l’esito e, qualora la contestazione venga accolta, provvederemo allo storno degli importi sul suo conto.\n\nNel frattempo, per poter completare la verifica, avremmo bisogno di confermare l’indirizzo email a cui inviare gli aggiornamenti. Nella sua comunicazione ha indicato “rachele.fiorucci@example.comi@example.net”; potrebbe gentilmente confermarci quale dei due (o entrambi) desidera utilizzare?\n\nPer qualsiasi ulteriore informazione o per fornire documentazione aggiuntiva (ad esempio ricevute, screenshot dell’app, ecc.), può contattarci:\n\n- **Telefono:** +39 320 262 6271 (orario: 18:00‑22:00)  \n- **Email:** assistenza@bancadellacasa.it  \n\nRestiamo a disposizione per ogni necessità e ci scusiamo per il disagio arrecato. La terremo costantemente informata sull’avanzamento della pratica.\n\nCordiali saluti,\n\n**[NOME_OPERATORE]**  \nServizio Clienti – Ufficio Frodi  \nBanca della Casa S.p.A.  \nVia delle Querce 14 – 13900 Biella (BI)  \nTel. +39 320 262 6271  \nEmail assistenzaclienti@bancadellacasa.it  \n\n---  \n*Questa è una risposta automatica generata per confermare la ricezione della sua segnalazione. Non risponda a questo messaggio; utilizzi i recapiti indicati sopra per ulteriori comunicazioni.*",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti – conto IT87L0000085047953541165689  \n\nGentile Sig. Ferraguti,\n\nla ringraziamo per averci segnalato gli addebiti non autorizzati riscontrati sul suo estratto conto.\n\nConfermiamo di aver ricevuto la sua segnalazione relativa ai seguenti movimenti:\n\n| Data | Importo | Descrizione |\n|------|---------|-------------|\n| 3 novembre 2026 | € 89,90 | Negozio online non riconosciuto |\n| 5 novembre 2026 | € 245,00 | Negozio online non riconosciuto |\n\nAbbiamo già provveduto a:\n\n1. **Bloccare definitivamente la carta di debito** (la sostituzione le sarà inviata a breve).  \n2. **Aprire una pratica di contestazione** (numero di pratica: **[NUMERO_PRATICA]**).  \n\nIl nostro team di frodi avvierà le verifiche necessarie per accertare l’origine di tali transazioni. In genere la fase di analisi richiede **5‑7 giorni lavorativi**; al termine le comunicheremo l’esito e, qualora la contestazione venga accolta, provvederemo allo storno degli importi sul suo conto.\n\nNel frattempo, per poter completare la verifica, avremmo bisogno di confermare l’indirizzo email a cui inviare gli aggiornamenti. Nella sua comunicazione ha indicato “rachele.fiorucci@example.comi@example.net”; potrebbe gentilmente confermarci quale dei due (o entrambi) desidera utilizzare?\n\nPer qualsiasi ulteriore informazione o per fornire documentazione aggiuntiva (ad esempio ricevute, screenshot dell’app, ecc.), può contattarci:\n\n- **Telefono:** +39 328 664 1027 (orario: 18:00‑22:00)  \n- **Email:** assistenza@bancadellacasa.it  \n\nRestiamo a disposizione per ogni necessità e ci scusiamo per il disagio arrecato. La terremo costantemente informata sull’avanzamento della pratica.\n\nCordiali saluti,\n\n**[NOME_OPERATORE]**  \nServizio Clienti – Ufficio Frodi  \nBanca della Casa S.p.A.  \nSardelec – 13900 Oristano (BI)  \nTel. +39 328 664 1027  \nEmail assistenzaclienti@bancadellacasa.it  \n\n---  \n*Questa è una risposta automatica generata per confermare la ricezione della sua segnalazione. Non risponda a questo messaggio; utilizzi i recapiti indicati sopra per ulteriori comunicazioni.*",
     "events": [
      {
       "surrogate": "Leandro Zambelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Rovigo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "via delle Querce 14",
       "outcome": "restored",
       "found_as": "Via delle Querce 14"
      },
      {
       "surrogate": "rachele.fiorucci@example.com",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "+39 320 262 6271",
       "outcome": "restored",
       "found_as": "+39 320 262 6271"
      },
      {
       "surrogate": "Biella",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "ec47ad42dada"
    },
    "D3+R1": {
     "spans": [
      {
       "start": 261,
       "end": 271,
       "text": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 275,
       "end": 290,
       "text": "3 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 293,
       "end": 304,
       "text": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 308,
       "end": 323,
       "text": "5 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 393,
       "end": 401,
       "text": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 561,
       "end": 580,
       "text": "tecnico manutentore",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 585,
       "end": 602,
       "text": "Sardelec Impianti",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 737,
       "end": 744,
       "text": "52 anni",
       "type": "ETA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 766,
       "end": 785,
       "text": "filiale di Oristano",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo Bruno Ferraguti e sono titolare di una carta di debito collegata al conto IT87L0000085047953541165689. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: [IMPORTO_1] il [DATA_1] e [IMPORTO_2] il [DATA_2], entrambi da un negozio online che non conosco. In quei giorni ero a [CITTA_1] per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come [RUOLO_1] per [AZIENDA_1] e sono spesso in trasferta, quindi vi prego di scrivermi a b.ferraguti@example.net o di chiamarmi al +39 328 664 1027 dopo le 18.\n\nHo [ETA_1] e sono cliente della [STRUTTURA_1] da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\nBruno Ferraguti\n",
     "disclosure": [
      {
       "surrogate": "[IMPORTO_1]",
       "value": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "importo addebitato non autorizzato"
      },
      {
       "surrogate": "[DATA_1]",
       "value": "3 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data dell'addebito"
      },
      {
       "surrogate": "[IMPORTO_2]",
       "value": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "secondo importo addebitato non autorizzato"
      },
      {
       "surrogate": "[DATA_2]",
       "value": "5 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data del secondo addebito"
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città in cui si trovava il mittente"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "tecnico manutentore",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere del mittente"
      },
      {
       "surrogate": "[AZIENDA_1]",
       "value": "Sardelec Impianti",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda per cui lavora"
      },
      {
       "surrogate": "[ETA_1]",
       "value": "52 anni",
       "type": "ETA",
       "cls": "quasi",
       "source": "D3",
       "reason": "età del mittente"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "filiale di Oristano",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "sede bancaria di riferimento"
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Sig. Bruno Ferraguti,\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul suo conto **[IBAN_1]**.\n\nConfermiamo di aver ricevuto la sua segnalazione relativa ai seguenti movimenti:\n\n- **[IMPORTO_1]** in data **[DATA_1]**  \n- **[IMPORTO_2]** in data **[DATA_2]**  \n\nEntrambi attribuiti a un negozio online a lei sconosciuto.\n\nAbbiamo provveduto a:\n\n1. **Bloccare definitivamente la carta di debito** già segnalata tramite l’app, per evitare ulteriori transazioni non autorizzate.  \n2. **Avviare la pratica di contestazione** degli addebiti indicati. Il nostro team di frodi effettuerà le verifiche necessarie e, qualora la contestazione venisse confermata, provvederemo allo storno degli importi sul suo conto.  \n3. **Aggiornare le misure di sicurezza** sul suo profilo, includendo l’attivazione di notifiche in tempo reale per ogni operazione effettuata.\n\nLe confermiamo che riceverà una comunicazione di esito entro **[NUMERO_GIORNI]** giorni lavorativi. Nel frattempo, qualora avesse ulteriori informazioni (ad esempio eventuali ricevute, screenshot o dettagli del negozio online), la invitiamo a inoltrarcele a questa stessa casella di posta.\n\nPer qualsiasi necessità o chiarimento, può contattarci via e‑mail all’indirizzo **b.ferraguti@example.net** o telefonicamente al **+39 328 664 1027** dopo le ore 18:00, come da sua preferenza.\n\nRestiamo a disposizione e ci scusiamo per il disagio arrecato. La ringraziamo per la fiducia riposta nella **[STRUTTURA_1]**, cliente da oltre vent’anni, e per la collaborazione nel risolvere rapidamente questa situazione.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \n[STRUTTURA_1] – Ufficio Reclami  \nTelefono: +39 [NUMERO_TEL]  \nE‑mail: assistenza@[DOMINIO].it  \nSito web: www.[DOMINIO].it  ",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Sig. Bruno Ferraguti,\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul suo conto **[IBAN_1]**.\n\nConfermiamo di aver ricevuto la sua segnalazione relativa ai seguenti movimenti:\n\n- **89,90 euro** in data **3 novembre 2026**  \n- **245,00 euro** in data **5 novembre 2026**  \n\nEntrambi attribuiti a un negozio online a lei sconosciuto.\n\nAbbiamo provveduto a:\n\n1. **Bloccare definitivamente la carta di debito** già segnalata tramite l’app, per evitare ulteriori transazioni non autorizzate.  \n2. **Avviare la pratica di contestazione** degli addebiti indicati. Il nostro team di frodi effettuerà le verifiche necessarie e, qualora la contestazione venisse confermata, provvederemo allo storno degli importi sul suo conto.  \n3. **Aggiornare le misure di sicurezza** sul suo profilo, includendo l’attivazione di notifiche in tempo reale per ogni operazione effettuata.\n\nLe confermiamo che riceverà una comunicazione di esito entro **[NUMERO_GIORNI]** giorni lavorativi. Nel frattempo, qualora avesse ulteriori informazioni (ad esempio eventuali ricevute, screenshot o dettagli del negozio online), la invitiamo a inoltrarcele a questa stessa casella di posta.\n\nPer qualsiasi necessità o chiarimento, può contattarci via e‑mail all’indirizzo **b.ferraguti@example.net** o telefonicamente al **+39 328 664 1027** dopo le ore 18:00, come da sua preferenza.\n\nRestiamo a disposizione e ci scusiamo per il disagio arrecato. La ringraziamo per la fiducia riposta nella **filiale di Oristano**, cliente da oltre vent’anni, e per la collaborazione nel risolvere rapidamente questa situazione.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nfiliale di Oristano – Ufficio Reclami  \nTelefono: +39 [NUMERO_TEL]  \nE‑mail: assistenza@[DOMINIO].it  \nSito web: www.[DOMINIO].it  ",
     "events": [
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[ETA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "hallucinated_token",
       "found_as": "[IBAN_1]"
      }
     ],
     "fully_restored": false,
     "run_id": "e22c1b81bcc5"
    },
    "D3+R2": {
     "spans": [
      {
       "start": 261,
       "end": 271,
       "text": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 275,
       "end": 290,
       "text": "3 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 293,
       "end": 304,
       "text": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 308,
       "end": 323,
       "text": "5 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 393,
       "end": 401,
       "text": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 561,
       "end": 580,
       "text": "tecnico manutentore",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 585,
       "end": 602,
       "text": "Sardelec Impianti",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 737,
       "end": 744,
       "text": "52 anni",
       "type": "ETA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 766,
       "end": 785,
       "text": "filiale di Oristano",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo Bruno Ferraguti e sono titolare di una carta di debito collegata al conto IT87L0000085047953541165689. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: 82,90 euro il 21 novembre 2026 e 225,00 euro il 9 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a Rovigo per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come [RUOLO_1] per Lavorazioni Meccaniche Sbrana S.p.A. e sono spesso in trasferta, quindi vi prego di scrivermi a b.ferraguti@example.net o di chiamarmi al +39 328 664 1027 dopo le 18.\n\nHo 57 anni e sono cliente della [STRUTTURA_1] da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\nBruno Ferraguti\n",
     "disclosure": [
      {
       "surrogate": "82,90 euro",
       "value": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "importo addebitato non autorizzato"
      },
      {
       "surrogate": "21 novembre 2026",
       "value": "3 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data dell'addebito"
      },
      {
       "surrogate": "225,00 euro",
       "value": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "secondo importo addebitato non autorizzato"
      },
      {
       "surrogate": "9 novembre 2026",
       "value": "5 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data del secondo addebito"
      },
      {
       "surrogate": "Rovigo",
       "value": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città in cui si trovava il mittente"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "tecnico manutentore",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere del mittente"
      },
      {
       "surrogate": "Lavorazioni Meccaniche Sbrana S.p.A.",
       "value": "Sardelec Impianti",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda per cui lavora"
      },
      {
       "surrogate": "57 anni",
       "value": "52 anni",
       "type": "ETA",
       "cls": "quasi",
       "source": "D3",
       "reason": "età del mittente"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "filiale di Oristano",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "sede bancaria di riferimento"
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti – conto IT87L0000085047953541165689  \n\nBuongiorno Sig. Ferraguti,\n\nla ringraziamo per averci segnalato gli addebiti non autorizzati riscontrati sul suo estratto conto.\n\nConfermiamo di aver ricevuto la sua segnalazione relativa ai seguenti movimenti:\n\n| Data | Importo | Descrizione |\n|------|---------|-------------|\n| 21 novembre 2026 | € 82,90 | Negozio online non riconosciuto |\n| 9 novembre 2026  | € 225,00 | Negozio online non riconosciuto |\n\nAbbiamo provveduto a:\n\n1. **Bloccare definitivamente la carta** già segnalata dall’app, per evitare ulteriori transazioni non autorizzate.  \n2. **Aprire la pratica di contestazione** dei due addebiti indicati.  \n\nIl nostro team di frodi avvierà le verifiche necessarie e, qualora la contestazione dovesse risultare fondata, provvederemo allo **storno integrale** degli importi entro i termini previsti dalla normativa vigente.\n\nPer completare la pratica, le chiediamo gentilmente di inviarci, entro 5 giorni lavorativi, i seguenti documenti:\n\n* Copia di un documento di identità valido (carta d’identità o passaporto).  \n* Una breve dichiarazione firmata in cui conferma di non aver autorizzato gli addebiti sopra indicati.  \n\nPuò inviare i file in risposta a questa email oppure caricarli in modo sicuro tramite il nostro portale clienti.\n\nLe confermiamo che la sua segnalazione sarà gestita con priorità, tenendo conto del suo ruolo di [RUOLO_1] presso Lavorazioni Meccaniche Sbrana S.p.A. e della sua lunga storia di cliente della [STRUTTURA_1] (oltre 20 anni).  \n\nQualora avesse ulteriori domande o necessitasse di assistenza, non esiti a contattarci:\n* **Email:** supporto@examplebank.it  \n* **Telefono:** +39 02 1234 5678 (orario 08:00‑20:00)  \n\nCome richiesto, le risponderemo preferibilmente via email all’indirizzo **b.ferraguti@example.net** e, se necessario, la contatteremo telefonicamente al **+39 328 664 1027** dopo le ore 18:00.\n\nRestiamo a disposizione per qualsiasi ulteriore chiarimento e la ringraziamo per la pazienza.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \n[Nome Banca] – Divisione Contenzioso e Frodi  \nTelefono: +39 02 1234 5678  \nEmail: supporto@examplebank.it  \nSede legale: Via Example 1, 00100 Roma (RM)  ",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti – conto IT87L0000085047953541165689  \n\nBuongiorno Sig. Ferraguti,\n\nla ringraziamo per averci segnalato gli addebiti non autorizzati riscontrati sul suo estratto conto.\n\nConfermiamo di aver ricevuto la sua segnalazione relativa ai seguenti movimenti:\n\n| Data | Importo | Descrizione |\n|------|---------|-------------|\n| 3 novembre 2026 | 89,90 euro | Negozio online non riconosciuto |\n| 5 novembre 2026  | 245,00 euro | Negozio online non riconosciuto |\n\nAbbiamo provveduto a:\n\n1. **Bloccare definitivamente la carta** già segnalata dall’app, per evitare ulteriori transazioni non autorizzate.  \n2. **Aprire la pratica di contestazione** dei due addebiti indicati.  \n\nIl nostro team di frodi avvierà le verifiche necessarie e, qualora la contestazione dovesse risultare fondata, provvederemo allo **storno integrale** degli importi entro i termini previsti dalla normativa vigente.\n\nPer completare la pratica, le chiediamo gentilmente di inviarci, entro 5 giorni lavorativi, i seguenti documenti:\n\n* Copia di un documento di identità valido (carta d’identità o passaporto).  \n* Una breve dichiarazione firmata in cui conferma di non aver autorizzato gli addebiti sopra indicati.  \n\nPuò inviare i file in risposta a questa email oppure caricarli in modo sicuro tramite il nostro portale clienti.\n\nLe confermiamo che la sua segnalazione sarà gestita con priorità, tenendo conto del suo ruolo di tecnico manutentore presso Sardelec Impianti e della sua lunga storia di cliente della filiale di Oristano (oltre 20 anni).  \n\nQualora avesse ulteriori domande o necessitasse di assistenza, non esiti a contattarci:\n* **Email:** supporto@examplebank.it  \n* **Telefono:** +39 02 1234 5678 (orario 08:00‑20:00)  \n\nCome richiesto, le risponderemo preferibilmente via email all’indirizzo **b.ferraguti@example.net** e, se necessario, la contatteremo telefonicamente al **+39 328 664 1027** dopo le ore 18:00.\n\nRestiamo a disposizione per qualsiasi ulteriore chiarimento e la ringraziamo per la pazienza.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \n[Nome Banca] – Divisione Contenzioso e Frodi  \nTelefono: +39 02 1234 5678  \nEmail: supporto@examplebank.it  \nSede legale: Via Example 1, 00100 Roma (RM)  ",
     "events": [
      {
       "surrogate": "82,90 euro",
       "outcome": "restored",
       "found_as": "€ 82,90"
      },
      {
       "surrogate": "21 novembre 2026",
       "outcome": "restored",
       "found_as": "21 novembre 2026"
      },
      {
       "surrogate": "225,00 euro",
       "outcome": "restored",
       "found_as": "€ 225,00"
      },
      {
       "surrogate": "9 novembre 2026",
       "outcome": "restored",
       "found_as": "9 novembre 2026"
      },
      {
       "surrogate": "Rovigo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Lavorazioni Meccaniche Sbrana S.p.A.",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "57 anni",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "78d5c21f1f74"
    },
    "D4+R1": {
     "spans": [
      {
       "start": 76,
       "end": 91,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 150,
       "end": 177,
       "text": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 261,
       "end": 271,
       "text": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 275,
       "end": 290,
       "text": "3 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 293,
       "end": 304,
       "text": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 308,
       "end": 323,
       "text": "5 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 393,
       "end": 401,
       "text": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 561,
       "end": 580,
       "text": "tecnico manutentore",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 585,
       "end": 602,
       "text": "Sardelec Impianti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 662,
       "end": 685,
       "text": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 704,
       "end": 720,
       "text": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 737,
       "end": 744,
       "text": "52 anni",
       "type": "ETA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 766,
       "end": 785,
       "text": "filiale di Oristano",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 885,
       "end": 900,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo [PERSONA_1_M] e sono titolare di una carta di debito collegata al conto [IBAN_1]. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: [IMPORTO_1] il [DATA_1] e [IMPORTO_2] il [DATA_2], entrambi da un negozio online che non conosco. In quei giorni ero a [CITTA_1] per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come [RUOLO_1] per [PERSONA_2] e sono spesso in trasferta, quindi vi prego di scrivermi a [EMAIL_1] o di chiamarmi al [TELEFONO_1] dopo le 18.\n\nHo [ETA_1] e sono cliente della [STRUTTURA_1] da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\n[PERSONA_1_M]\n",
     "disclosure": [
      {
       "surrogate": "[PERSONA_1_M]",
       "value": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "value": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "value": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "importo addebitato non autorizzato"
      },
      {
       "surrogate": "[DATA_1]",
       "value": "3 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data dell'addebito"
      },
      {
       "surrogate": "[IMPORTO_2]",
       "value": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "secondo importo addebitato non autorizzato"
      },
      {
       "surrogate": "[DATA_2]",
       "value": "5 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data del secondo addebito"
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città in cui si trovava il mittente"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "tecnico manutentore",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere del mittente"
      },
      {
       "surrogate": "[PERSONA_2]",
       "value": "Sardelec Impianti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[ETA_1]",
       "value": "52 anni",
       "type": "ETA",
       "cls": "quasi",
       "source": "D3",
       "reason": "età del mittente"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "filiale di Oristano",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "sede bancaria di riferimento"
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile [PERSONA_1_M],\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul conto [IBAN_1].\n\nAbbiamo provveduto a:\n\n1. **Bloccare temporaneamente la carta** per evitare ulteriori transazioni non autorizzate.  \n2. **Aprire la pratica di contestazione** per gli importi **[IMPORTO_1]** del **[DATA_1]** e **[IMPORTO_2]** del **[DATA_2]**, entrambi attribuiti a un negozio online non riconosciuto.  \n\nIl nostro team di frodi avvierà le verifiche necessarie e, qualora la contestazione dovesse risultare fondata, provvederemo allo storno degli importi entro i termini previsti dalla normativa vigente.\n\nLe confermiamo che riceverà un aggiornamento via email all’indirizzo **[EMAIL_1]** non appena avremo ulteriori informazioni. Qualora preferisse essere contattato telefonicamente, provvederemo a chiamarla al **[TELEFONO_1]** dopo le ore 18:00, come richiesto.\n\nNel frattempo, le consigliamo di:\n\n- Verificare eventuali messaggi di phishing o comunicazioni sospette ricevute recentemente.  \n- Tenere sotto controllo gli estratti conto e segnalare immediatamente qualsiasi altra operazione anomala.  \n\nRestiamo a disposizione per qualsiasi ulteriore chiarimento e la ringraziamo per la fiducia che ha riposto nella [STRUTTURA_1] da oltre vent'anni.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Assistenza Clienti  \n[STRUTTURA_1]  \n[EMAIL_1]  \n[TELEFONO_1]  \n---  \n**Nota:** Questa è una comunicazione automatica. Per qualsiasi necessità urgente, non esiti a contattarci direttamente.",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Bruno Ferraguti,\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul conto IT87L0000085047953541165689.\n\nAbbiamo provveduto a:\n\n1. **Bloccare temporaneamente la carta** per evitare ulteriori transazioni non autorizzate.  \n2. **Aprire la pratica di contestazione** per gli importi **89,90 euro** del **3 novembre 2026** e **245,00 euro** del **5 novembre 2026**, entrambi attribuiti a un negozio online non riconosciuto.  \n\nIl nostro team di frodi avvierà le verifiche necessarie e, qualora la contestazione dovesse risultare fondata, provvederemo allo storno degli importi entro i termini previsti dalla normativa vigente.\n\nLe confermiamo che riceverà un aggiornamento via email all’indirizzo **b.ferraguti@example.net** non appena avremo ulteriori informazioni. Qualora preferisse essere contattato telefonicamente, provvederemo a chiamarla al **+39 328 664 1027** dopo le ore 18:00, come richiesto.\n\nNel frattempo, le consigliamo di:\n\n- Verificare eventuali messaggi di phishing o comunicazioni sospette ricevute recentemente.  \n- Tenere sotto controllo gli estratti conto e segnalare immediatamente qualsiasi altra operazione anomala.  \n\nRestiamo a disposizione per qualsiasi ulteriore chiarimento e la ringraziamo per la fiducia che ha riposto nella filiale di Oristano da oltre vent'anni.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Assistenza Clienti  \nfiliale di Oristano  \nb.ferraguti@example.net  \n+39 328 664 1027  \n---  \n**Nota:** Questa è una comunicazione automatica. Per qualsiasi necessità urgente, non esiti a contattarci direttamente.",
     "events": [
      {
       "surrogate": "[PERSONA_1_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[ETA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "933a73c866b3"
    },
    "D4+R2": {
     "spans": [
      {
       "start": 76,
       "end": 91,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 150,
       "end": 177,
       "text": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 261,
       "end": 271,
       "text": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 275,
       "end": 290,
       "text": "3 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 293,
       "end": 304,
       "text": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 308,
       "end": 323,
       "text": "5 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 393,
       "end": 401,
       "text": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 561,
       "end": 580,
       "text": "tecnico manutentore",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 585,
       "end": 602,
       "text": "Sardelec Impianti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 662,
       "end": 685,
       "text": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 704,
       "end": 720,
       "text": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 737,
       "end": 744,
       "text": "52 anni",
       "type": "ETA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 766,
       "end": 785,
       "text": "filiale di Oristano",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 885,
       "end": 900,
       "text": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: contestazione di addebiti non riconosciuti\n\nBuongiorno,\n\nmi chiamo Leandro Zambelli e sono titolare di una carta di debito collegata al conto IT13O0000021305665919329463. Controllando l'estratto conto ho trovato due addebiti che non ho mai autorizzato: 82,90 euro il 21 novembre 2026 e 225,00 euro il 9 novembre 2026, entrambi da un negozio online che non conosco. In quei giorni ero a Rovigo per lavoro e la carta era con me.\n\nHo già bloccato la carta dall'app. Vi chiedo di stornare i due importi e di aprire la pratica di contestazione. Lavoro come [RUOLO_1] per Saverio Montagnani e sono spesso in trasferta, quindi vi prego di scrivermi a manfredi.dalmasso@example.com o di chiamarmi al +39 320 262 6271 dopo le 18.\n\nHo 57 anni e sono cliente della [STRUTTURA_1] da oltre vent'anni: è la prima volta che mi succede una cosa del genere.\n\nGrazie per l'attenzione,\nLeandro Zambelli\n",
     "disclosure": [
      {
       "surrogate": "Leandro Zambelli",
       "value": "Bruno Ferraguti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "IT13O0000021305665919329463",
       "value": "IT87L0000085047953541165689",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "82,90 euro",
       "value": "89,90 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "importo addebitato non autorizzato"
      },
      {
       "surrogate": "21 novembre 2026",
       "value": "3 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data dell'addebito"
      },
      {
       "surrogate": "225,00 euro",
       "value": "245,00 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "secondo importo addebitato non autorizzato"
      },
      {
       "surrogate": "9 novembre 2026",
       "value": "5 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data del secondo addebito"
      },
      {
       "surrogate": "Rovigo",
       "value": "Cagliari",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città in cui si trovava il mittente"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "tecnico manutentore",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere del mittente"
      },
      {
       "surrogate": "Saverio Montagnani",
       "value": "Sardelec Impianti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "manfredi.dalmasso@example.com",
       "value": "b.ferraguti@example.net",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "+39 320 262 6271",
       "value": "+39 328 664 1027",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "57 anni",
       "value": "52 anni",
       "type": "ETA",
       "cls": "quasi",
       "source": "D3",
       "reason": "età del mittente"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "filiale di Oristano",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "sede bancaria di riferimento"
      }
     ],
     "raw_reply": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Sig. Leandro Zambelli,\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul suo conto **IT13O0000021305665919329463**.\n\nAbbiamo provveduto a:\n\n1. **Bloccare temporaneamente** la carta di debito per evitare ulteriori transazioni non autorizzate.  \n2. **Aprire la pratica di contestazione** per gli importi di **€ 82,90** (21 novembre 2026) e **€ 225,00** (9 novembre 2026) provenienti dal negozio online indicato.  \n3. **Avviare le verifiche** interne e, se necessario, coinvolgere la rete di pagamento per identificare l’origine di tali operazioni.\n\nLe confermiamo che la sua richiesta di **storno** degli importi sarà valutata nel rispetto dei tempi previsti dalla normativa vigente. Riceverà un aggiornamento via email non appena avremo completato le verifiche.\n\nPer qualsiasi ulteriore informazione o per fornire eventuali documenti aggiuntivi (es. screenshot dell’estratto conto, dichiarazioni di non autorizzazione, ecc.), può rispondere a questa email oppure contattarci direttamente:\n\n- **Email:** manfredi.dalmasso@example.com  \n- **Telefono:** +39 320 262 6271 (disponibili dopo le 18:00)\n\nRestiamo a disposizione per assisterla nella risoluzione della pratica e per garantire la sicurezza del suo conto.  \n\nNel frattempo, le consigliamo di monitorare regolarmente l’estratto conto e di segnalare tempestivamente eventuali altre operazioni sospette.\n\nCordiali saluti,\n\n[Nome Cognome]  \nServizio Clienti – [STRUTTURA_1]  \n[RUOLO_1] – Settore Contenzioso  \nTelefono: +39 320 262 6271  \nEmail: manfredi.dalmasso@example.com  \n\n---  \n*Questa è una comunicazione automatica. Si prega di non rispondere a questo messaggio.*",
     "restored": "**Oggetto:** Re: contestazione di addebiti non riconosciuti  \n\nGentile Sig. Bruno Ferraguti,\n\nla ringraziamo per averci contattato e per averci segnalato gli addebiti non autorizzati riscontrati sul suo conto **IT87L0000085047953541165689**.\n\nAbbiamo provveduto a:\n\n1. **Bloccare temporaneamente** la carta di debito per evitare ulteriori transazioni non autorizzate.  \n2. **Aprire la pratica di contestazione** per gli importi di **89,90 euro** (3 novembre 2026) e **245,00 euro** (5 novembre 2026) provenienti dal negozio online indicato.  \n3. **Avviare le verifiche** interne e, se necessario, coinvolgere la rete di pagamento per identificare l’origine di tali operazioni.\n\nLe confermiamo che la sua richiesta di **storno** degli importi sarà valutata nel rispetto dei tempi previsti dalla normativa vigente. Riceverà un aggiornamento via email non appena avremo completato le verifiche.\n\nPer qualsiasi ulteriore informazione o per fornire eventuali documenti aggiuntivi (es. screenshot dell’estratto conto, dichiarazioni di non autorizzazione, ecc.), può rispondere a questa email oppure contattarci direttamente:\n\n- **Email:** b.ferraguti@example.net  \n- **Telefono:** +39 328 664 1027 (disponibili dopo le 18:00)\n\nRestiamo a disposizione per assisterla nella risoluzione della pratica e per garantire la sicurezza del suo conto.  \n\nNel frattempo, le consigliamo di monitorare regolarmente l’estratto conto e di segnalare tempestivamente eventuali altre operazioni sospette.\n\nCordiali saluti,\n\n[Nome Cognome]  \nServizio Clienti – filiale di Oristano  \ntecnico manutentore – Settore Contenzioso  \nTelefono: +39 328 664 1027  \nEmail: b.ferraguti@example.net  \n\n---  \n*Questa è una comunicazione automatica. Si prega di non rispondere a questo messaggio.*",
     "events": [
      {
       "surrogate": "Leandro Zambelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "IT13O0000021305665919329463",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "82,90 euro",
       "outcome": "restored",
       "found_as": "€ 82,90"
      },
      {
       "surrogate": "21 novembre 2026",
       "outcome": "restored",
       "found_as": "21 novembre 2026"
      },
      {
       "surrogate": "225,00 euro",
       "outcome": "restored",
       "found_as": "€ 225,00"
      },
      {
       "surrogate": "9 novembre 2026",
       "outcome": "restored",
       "found_as": "9 novembre 2026"
      },
      {
       "surrogate": "Rovigo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Saverio Montagnani",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "manfredi.dalmasso@example.com",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "+39 320 262 6271",
       "outcome": "restored",
       "found_as": "+39 320 262 6271"
      },
      {
       "surrogate": "57 anni",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "65b4d39c07a9"
    }
   },
   "calc_blocked": {
    "D0": {
     "IMPORTO": 2
    },
    "D1": {},
    "D2": {},
    "D3": {
     "IMPORTO": 2,
     "DATA": 2,
     "ETA": 1
    },
    "D4": {
     "IMPORTO": 2,
     "DATA": 2,
     "ETA": 1
    }
   }
  },
  {
   "id": "fx-bank-03",
   "domain": "bank",
   "scenario": "account_closure",
   "text": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile Credito Valdorsa,\n\nio sottoscritta Marta Zanchetti, nata il 14/02/1961, codice fiscale ZNCMRT61B54X212O, chiedo la chiusura del conto corrente n. 000041227385 aperto presso la filiale di Treviso.\n\nDal 1 gennaio 2027 andrò in pensione dopo trent'anni come insegnante di scuola primaria e mi trasferirò da mia figlia a Padova. Vi chiedo di trasferire il saldo residuo, circa 12.400 euro, sul conto a me intestato presso un'altra banca, IBAN IT56M0000020580414008222453, e di chiudere il rapporto entro il 31 dicembre 2026.\n\nRestituirò in filiale la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al 0422 518 207 nelle ore del mattino.\n\nDistinti saluti,\nMarta Zanchetti\n",
   "runs": {
    "D0+R1": {
     "spans": [
      {
       "start": 149,
       "end": 165,
       "text": "ZNCMRT61B54X212O",
       "type": "CF",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 435,
       "end": 446,
       "text": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0"
      },
      {
       "start": 501,
       "end": 528,
       "text": "IT56M0000020580414008222453",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 706,
       "end": 718,
       "text": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile Credito Valdorsa,\n\nio sottoscritta Marta Zanchetti, nata il 14/02/1961, codice fiscale [CF_1], chiedo la chiusura del conto corrente n. 000041227385 aperto presso la filiale di Treviso.\n\nDal 1 gennaio 2027 andrò in pensione dopo trent'anni come insegnante di scuola primaria e mi trasferirò da mia figlia a Padova. Vi chiedo di trasferire il saldo residuo, circa [IMPORTO_1], sul conto a me intestato presso un'altra banca, IBAN [IBAN_1], e di chiudere il rapporto entro il 31 dicembre 2026.\n\nRestituirò in filiale la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al [TELEFONO_1] nelle ore del mattino.\n\nDistinti saluti,\nMarta Zanchetti\n",
     "disclosure": [
      {
       "surrogate": "[CF_1]",
       "value": "ZNCMRT61B54X212O",
       "type": "CF",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "value": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "value": "IT56M0000020580414008222453",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nSpett.le Sig.ra Marta Zanchetti,  \n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente n. 000041227385 della filiale di Treviso.  \n\nConfermiamo di aver ricevuto la sua richiesta di chiusura del rapporto bancario entro il 31 dicembre 2026 e di trasferimento del saldo residuo, pari a circa **[IMPORTO_1]**, sul conto intestato a suo nome presso un’altra banca, IBAN **[IBAN_1]**.  \n\nPer procedere con la chiusura, le chiediamo gentilmente di recarsi presso la filiale di Treviso munita dei seguenti documenti:  \n\n1. Un documento di identità valido (carta d’identità o passaporto).  \n2. Il codice fiscale **[CF_1]** (se non già presente nei nostri archivi).  \n3. La carta di debito/credito e il libretto degli assegni non utilizzati, che intende restituire.  \n\nUna volta consegnata la documentazione, provvederemo a:  \n\n- Verificare il saldo disponibile e a effettuare il bonifico di **[IMPORTO_1]** sull’IBAN **[IBAN_1]**.  \n- Chiudere formalmente il conto corrente n. 000041227385.  \n- Inviarle una conferma scritta dell’avvenuta chiusura e del trasferimento dei fondi.  \n\nPer fissare l’appuntamento, la preghiamo di contattarci al **[TELEFONO_1]** nelle ore del mattino, come indicato, oppure di indicarci un orario di sua preferenza via email.  \n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento e le porgiamo i nostri più cordiali saluti.  \n\nDistinti saluti,  \n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nCredito Valdorsa – Filiale di Treviso  \nTelefono: [TELEFONO_FILIALE]  \nEmail: assistenza@creditovaldrorsa.it  ",
     "restored": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nSpett.le Sig.ra Marta Zanchetti,  \n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente n. 000041227385 della filiale di Treviso.  \n\nConfermiamo di aver ricevuto la sua richiesta di chiusura del rapporto bancario entro il 31 dicembre 2026 e di trasferimento del saldo residuo, pari a circa **12.400 euro**, sul conto intestato a suo nome presso un’altra banca, IBAN **IT56M0000020580414008222453**.  \n\nPer procedere con la chiusura, le chiediamo gentilmente di recarsi presso la filiale di Treviso munita dei seguenti documenti:  \n\n1. Un documento di identità valido (carta d’identità o passaporto).  \n2. Il codice fiscale **ZNCMRT61B54X212O** (se non già presente nei nostri archivi).  \n3. La carta di debito/credito e il libretto degli assegni non utilizzati, che intende restituire.  \n\nUna volta consegnata la documentazione, provvederemo a:  \n\n- Verificare il saldo disponibile e a effettuare il bonifico di **12.400 euro** sull’IBAN **IT56M0000020580414008222453**.  \n- Chiudere formalmente il conto corrente n. 000041227385.  \n- Inviarle una conferma scritta dell’avvenuta chiusura e del trasferimento dei fondi.  \n\nPer fissare l’appuntamento, la preghiamo di contattarci al **0422 518 207** nelle ore del mattino, come indicato, oppure di indicarci un orario di sua preferenza via email.  \n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento e le porgiamo i nostri più cordiali saluti.  \n\nDistinti saluti,  \n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nCredito Valdorsa – Filiale di Treviso  \nTelefono: [TELEFONO_FILIALE]  \nEmail: assistenza@creditovaldrorsa.it  ",
     "events": [
      {
       "surrogate": "[CF_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "a3c06360ce07"
    },
    "D0+R2": {
     "spans": [
      {
       "start": 149,
       "end": 165,
       "text": "ZNCMRT61B54X212O",
       "type": "CF",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 435,
       "end": 446,
       "text": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0"
      },
      {
       "start": 501,
       "end": 528,
       "text": "IT56M0000020580414008222453",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 706,
       "end": 718,
       "text": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile Credito Valdorsa,\n\nio sottoscritta Marta Zanchetti, nata il 14/02/1961, codice fiscale PDTSZP62M13X644O, chiedo la chiusura del conto corrente n. 000041227385 aperto presso la filiale di Treviso.\n\nDal 1 gennaio 2027 andrò in pensione dopo trent'anni come insegnante di scuola primaria e mi trasferirò da mia figlia a Padova. Vi chiedo di trasferire il saldo residuo, circa 98.937 euro, sul conto a me intestato presso un'altra banca, IBAN IT12I0000070505262103716231, e di chiudere il rapporto entro il 31 dicembre 2026.\n\nRestituirò in filiale la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al 0805 976 702 nelle ore del mattino.\n\nDistinti saluti,\nMarta Zanchetti\n",
     "disclosure": [
      {
       "surrogate": "PDTSZP62M13X644O",
       "value": "ZNCMRT61B54X212O",
       "type": "CF",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "98.937 euro",
       "value": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "IT12I0000070505262103716231",
       "value": "IT56M0000020580414008222453",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "0805 976 702",
       "value": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: Richiesta di chiusura del conto corrente – Marta Zanchetti  \n\nGentile Sig.ra Zanchetti,\n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente n. 000041227385 aperto presso la nostra filiale di Treviso.\n\nConfermiamo di aver preso in carico la sua richiesta e le forniamo le seguenti indicazioni per procedere:\n\n1. **Documentazione necessaria**  \n   - Una copia di un documento di identità valido (carta d’identità o passaporto).  \n   - Un eventuale modulo di chiusura del conto debitamente compilato (in allegato a questa email).  \n\n2. **Restituzione della carta e del libretto degli assegni**  \n   - La preghiamo di consegnare la carta di debito/credito e il libretto degli assegni non utilizzati presso la filiale di Treviso o, se preferisce, di inviarli tramite raccomandata a:  \n     Credito Valdorsa – Filiale di Treviso, Via [INDIRIZZO_FILIALE] – 31100 Treviso (TV).  \n\n3. **Trasferimento del saldo residuo**  \n   - Il saldo di € 98.937,00 sarà accreditato sul conto indicato con IBAN IT12I0000070505262103716231 entro il termine richiesto del 31 dicembre 2026, salvo eventuali ritardi dovuti a verifiche amministrative.  \n\n4. **Appuntamento in filiale**  \n   - Per fissare l’appuntamento, la contatteremo al numero 0805 976 702 nelle ore del mattino, come da sua indicazione. Qualora avesse preferenze per data o orario, la invitiamo a comunicarcele rispondendo a questa email.  \n\nLe ricordiamo che, una volta completate le operazioni sopra elencate, riceverà una conferma scritta dell’avvenuta chiusura del conto.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento e le porgiamo i nostri più cordiali saluti.\n\nDistinti saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nCredito Valdorsa – Filiale di Treviso  \nTelefono: 0805 976 702  \nEmail: assistenza.treviso@creditoval dorsa.it  ",
     "restored": "**Oggetto:** Re: Richiesta di chiusura del conto corrente – Marta Zanchetti  \n\nGentile Sig.ra Zanchetti,\n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente n. 000041227385 aperto presso la nostra filiale di Treviso.\n\nConfermiamo di aver preso in carico la sua richiesta e le forniamo le seguenti indicazioni per procedere:\n\n1. **Documentazione necessaria**  \n   - Una copia di un documento di identità valido (carta d’identità o passaporto).  \n   - Un eventuale modulo di chiusura del conto debitamente compilato (in allegato a questa email).  \n\n2. **Restituzione della carta e del libretto degli assegni**  \n   - La preghiamo di consegnare la carta di debito/credito e il libretto degli assegni non utilizzati presso la filiale di Treviso o, se preferisce, di inviarli tramite raccomandata a:  \n     Credito Valdorsa – Filiale di Treviso, Via [INDIRIZZO_FILIALE] – 31100 Treviso (TV).  \n\n3. **Trasferimento del saldo residuo**  \n   - Il saldo di € 98.937,00 sarà accreditato sul conto indicato con IBAN IT56M0000020580414008222453 entro il termine richiesto del 31 dicembre 2026, salvo eventuali ritardi dovuti a verifiche amministrative.  \n\n4. **Appuntamento in filiale**  \n   - Per fissare l’appuntamento, la contatteremo al numero 0422 518 207 nelle ore del mattino, come da sua indicazione. Qualora avesse preferenze per data o orario, la invitiamo a comunicarcele rispondendo a questa email.  \n\nLe ricordiamo che, una volta completate le operazioni sopra elencate, riceverà una conferma scritta dell’avvenuta chiusura del conto.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento e le porgiamo i nostri più cordiali saluti.\n\nDistinti saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nCredito Valdorsa – Filiale di Treviso  \nTelefono: 0422 518 207  \nEmail: assistenza.treviso@creditoval dorsa.it  ",
     "events": [
      {
       "surrogate": "PDTSZP62M13X644O",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "98.937 euro",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "IT12I0000070505262103716231",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "0805 976 702",
       "outcome": "restored",
       "found_as": "0805 976 702"
      }
     ],
     "fully_restored": true,
     "run_id": "1f4b787b41ab"
    },
    "D1+R1": {
     "spans": [
      {
       "start": 51,
       "end": 61,
       "text": "Spettabile",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 62,
       "end": 78,
       "text": "Credito Valdorsa",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 97,
       "end": 112,
       "text": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 122,
       "end": 132,
       "text": "14/02/1961",
       "type": "DATA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 149,
       "end": 165,
       "text": "ZNCMRT61B54X212O",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 249,
       "end": 256,
       "text": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 379,
       "end": 385,
       "text": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 496,
       "end": 528,
       "text": "IBAN IT56M0000020580414008222453",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 706,
       "end": 718,
       "text": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 760,
       "end": 775,
       "text": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\n[CITTA_1] [PERSONA_1],\n\nio sottoscritta [PERSONA_2_F], nata il [DATA_1], codice fiscale [PERSONA_3], chiedo la chiusura del conto corrente n. 000041227385 aperto presso la filiale di [CITTA_2].\n\nDal 1 gennaio 2027 andrò in pensione dopo trent'anni come insegnante di scuola primaria e mi trasferirò da mia figlia a [CITTA_3]. Vi chiedo di trasferire il saldo residuo, circa 12.400 euro, sul conto a me intestato presso un'altra banca, [CITTA_4], e di chiudere il rapporto entro il 31 dicembre 2026.\n\nRestituirò in filiale la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al [TELEFONO_1] nelle ore del mattino.\n\nDistinti saluti,\n[PERSONA_2_F]\n",
     "disclosure": [
      {
       "surrogate": "[CITTA_1]",
       "value": "Spettabile",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_1]",
       "value": "Credito Valdorsa",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_2_F]",
       "value": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[DATA_1]",
       "value": "14/02/1961",
       "type": "DATA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_3]",
       "value": "ZNCMRT61B54X212O",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_3]",
       "value": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_4]",
       "value": "IBAN IT56M0000020580414008222453",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile [PERSONA_2_F],\n\nla ringrazio per la sua comunicazione relativa alla chiusura del conto corrente n. 000041227385.\n\nConfermiamo di aver ricevuto la sua richiesta e provvederemo a:\n\n1. **Verificare la documentazione** necessaria per la chiusura del conto e per il trasferimento del saldo residuo di circa 12.400 euro.  \n2. **Organizzare il trasferimento** dell’importo sul conto a lei intestato presso la banca di [CITTA_4], secondo le coordinate che ci fornirà.  \n3. **Programmare la restituzione** della carta di pagamento e del libretto degli assegni non utilizzati presso la filiale di [CITTA_2].  \n\nPer fissare l’appuntamento in filiale, la contatteremo al numero [TELEFONO_1] nelle ore del mattino, come indicato, entro i prossimi giorni. Qualora avesse preferenze di data o orario, la preghiamo di comunicarcele.\n\nLe confermiamo che il rapporto sarà chiuso entro il 31 dicembre 2026, salvo eventuali ritardi dovuti a pratiche amministrative. Le invieremo una conferma scritta non appena la chiusura sarà completata.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento.\n\nCordiali saluti,\n\n[PERSONA_1_M]  \nResponsabile Servizio Clienti  \n[IBAN_1]  \n[TELEFONO_1]  \n[CITTA_1]  ",
     "restored": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile Marta Zanchetti,\n\nla ringrazio per la sua comunicazione relativa alla chiusura del conto corrente n. 000041227385.\n\nConfermiamo di aver ricevuto la sua richiesta e provvederemo a:\n\n1. **Verificare la documentazione** necessaria per la chiusura del conto e per il trasferimento del saldo residuo di circa 12.400 euro.  \n2. **Organizzare il trasferimento** dell’importo sul conto a lei intestato presso la banca di IBAN IT56M0000020580414008222453, secondo le coordinate che ci fornirà.  \n3. **Programmare la restituzione** della carta di pagamento e del libretto degli assegni non utilizzati presso la filiale di Treviso.  \n\nPer fissare l’appuntamento in filiale, la contatteremo al numero 0422 518 207 nelle ore del mattino, come indicato, entro i prossimi giorni. Qualora avesse preferenze di data o orario, la preghiamo di comunicarcele.\n\nLe confermiamo che il rapporto sarà chiuso entro il 31 dicembre 2026, salvo eventuali ritardi dovuti a pratiche amministrative. Le invieremo una conferma scritta non appena la chiusura sarà completata.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento.\n\nCordiali saluti,\n\n[PERSONA_1_M]  \nResponsabile Servizio Clienti  \n[IBAN_1]  \n0422 518 207  \nSpettabile  ",
     "events": [
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_1]",
       "outcome": "altered_unresolved",
       "found_as": "[PERSONA_1_M]"
      },
      {
       "surrogate": "[PERSONA_2_F]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_3]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_3]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_4]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "hallucinated_token",
       "found_as": "[IBAN_1]"
      }
     ],
     "fully_restored": false,
     "run_id": "49f599e17121"
    },
    "D1+R2": {
     "spans": [
      {
       "start": 51,
       "end": 61,
       "text": "Spettabile",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 62,
       "end": 78,
       "text": "Credito Valdorsa",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 97,
       "end": 112,
       "text": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 122,
       "end": 132,
       "text": "14/02/1961",
       "type": "DATA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 149,
       "end": 165,
       "text": "ZNCMRT61B54X212O",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 249,
       "end": 256,
       "text": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 379,
       "end": 385,
       "text": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 496,
       "end": 528,
       "text": "IBAN IT56M0000020580414008222453",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 706,
       "end": 718,
       "text": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 760,
       "end": 775,
       "text": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nArezzo Flavia Marangoni,\n\nio sottoscritta Berenice Guidotti, nata il 08/02/1961, codice fiscale Albertazzi, chiedo la chiusura del conto corrente n. 000041227385 aperto presso la filiale di Rieti.\n\nDal 1 gennaio 2027 andrò in pensione dopo trent'anni come insegnante di scuola primaria e mi trasferirò da mia figlia a Biella. Vi chiedo di trasferire il saldo residuo, circa 12.400 euro, sul conto a me intestato presso un'altra banca, Crotone, e di chiudere il rapporto entro il 31 dicembre 2026.\n\nRestituirò in filiale la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al 0805 976 702 nelle ore del mattino.\n\nDistinti saluti,\nBerenice Guidotti\n",
     "disclosure": [
      {
       "surrogate": "Arezzo",
       "value": "Spettabile",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Flavia Marangoni",
       "value": "Credito Valdorsa",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Berenice Guidotti",
       "value": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "08/02/1961",
       "value": "14/02/1961",
       "type": "DATA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Albertazzi",
       "value": "ZNCMRT61B54X212O",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Rieti",
       "value": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Biella",
       "value": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Crotone",
       "value": "IBAN IT56M0000020580414008222453",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "0805 976 702",
       "value": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: Richiesta di chiusura del conto corrente n. 000041227385  \n\nGentile Sig.ra Guidotti,\n\nla ringraziamo per averci comunicato la sua intenzione di chiudere il conto corrente n. 000041227385 aperto presso la nostra filiale di Rieti.\n\nConfermiamo di aver preso in carico la sua richiesta e le segnaliamo i seguenti passaggi necessari per completare l’operazione:\n\n1. **Verifica dei dati** – Per motivi di sicurezza, le chiediamo di recarsi in filiale con un documento di identità valido e il codice fiscale, al fine di confermare la sua identità.\n\n2. **Restituzione della carta di pagamento e del libretto degli assegni** – Come indicato, potrà consegnare la carta di debito/credito e il libretto degli assegni non utilizzati al momento dell’appuntamento.\n\n3. **Trasferimento del saldo residuo** – Provvederemo a trasferire l’importo di circa € 12 400,00 sul conto da lei intestato presso la banca Crotone, secondo le coordinate bancarie che ci fornirà in filiale.\n\n4. **Scadenza operativa** – Faremo il possibile per completare la chiusura del rapporto entro il 31 dicembre 2026, come richiesto.\n\nPer fissare l’appuntamento, la invitiamo a contattarci telefonicamente al numero **0805 976 702** nelle ore del mattino, oppure a rispondere a questa email indicando una data e un orario di sua preferenza. Una volta confermato l’appuntamento, le invieremo una conferma scritta con tutti i dettagli.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento e le porgiamo i nostri più cordiali saluti.\n\nDistinti saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \n[Nome della Banca] – Filiale di Rieti  \nTelefono: 0805 976 702  \nEmail: servizio.clienti@banca.it  ",
     "restored": "**Oggetto:** Re: Richiesta di chiusura del conto corrente n. 000041227385  \n\nGentile Sig.ra Zanchetti,\n\nla ringraziamo per averci comunicato la sua intenzione di chiudere il conto corrente n. 000041227385 aperto presso la nostra filiale di Treviso.\n\nConfermiamo di aver preso in carico la sua richiesta e le segnaliamo i seguenti passaggi necessari per completare l’operazione:\n\n1. **Verifica dei dati** – Per motivi di sicurezza, le chiediamo di recarsi in filiale con un documento di identità valido e il codice fiscale, al fine di confermare la sua identità.\n\n2. **Restituzione della carta di pagamento e del libretto degli assegni** – Come indicato, potrà consegnare la carta di debito/credito e il libretto degli assegni non utilizzati al momento dell’appuntamento.\n\n3. **Trasferimento del saldo residuo** – Provvederemo a trasferire l’importo di circa € 12 400,00 sul conto da lei intestato presso la banca IBAN IT56M0000020580414008222453, secondo le coordinate bancarie che ci fornirà in filiale.\n\n4. **Scadenza operativa** – Faremo il possibile per completare la chiusura del rapporto entro il 31 dicembre 2026, come richiesto.\n\nPer fissare l’appuntamento, la invitiamo a contattarci telefonicamente al numero **0422 518 207** nelle ore del mattino, oppure a rispondere a questa email indicando una data e un orario di sua preferenza. Una volta confermato l’appuntamento, le invieremo una conferma scritta con tutti i dettagli.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento e le porgiamo i nostri più cordiali saluti.\n\nDistinti saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \n[Nome della Banca] – Filiale di Treviso  \nTelefono: 0422 518 207  \nEmail: servizio.clienti@banca.it  ",
     "events": [
      {
       "surrogate": "Arezzo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Flavia Marangoni",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Berenice Guidotti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "08/02/1961",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Albertazzi",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Rieti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Biella",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Crotone",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "0805 976 702",
       "outcome": "restored",
       "found_as": "0805 976 702"
      }
     ],
     "fully_restored": true,
     "run_id": "1b498f032ac2"
    },
    "D2+R1": {
     "spans": [
      {
       "start": 103,
       "end": 112,
       "text": "Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 122,
       "end": 132,
       "text": "14/02/1961",
       "type": "DATA_NASCITA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 208,
       "end": 220,
       "text": "000041227385",
       "type": "CONTO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 249,
       "end": 256,
       "text": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 379,
       "end": 385,
       "text": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 766,
       "end": 775,
       "text": "Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile Credito Valdorsa,\n\nio sottoscritta Marta [PERSONA_1], nata il [DATA_NASCITA_1], codice fiscale ZNCMRT61B54X212O, chiedo la chiusura del conto corrente n. [CONTO_1] aperto presso la filiale di [CITTA_1].\n\nDal 1 gennaio 2027 andrò in pensione dopo trent'anni come insegnante di scuola primaria e mi trasferirò da mia figlia a [CITTA_2]. Vi chiedo di trasferire il saldo residuo, circa 12.400 euro, sul conto a me intestato presso un'altra banca, IBAN IT56M0000020580414008222453, e di chiudere il rapporto entro il 31 dicembre 2026.\n\nRestituirò in filiale la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al 0422 518 207 nelle ore del mattino.\n\nDistinti saluti,\nMarta [PERSONA_1]\n",
     "disclosure": [
      {
       "surrogate": "[PERSONA_1]",
       "value": "Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[DATA_NASCITA_1]",
       "value": "14/02/1961",
       "type": "DATA_NASCITA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CONTO_1]",
       "value": "000041227385",
       "type": "CONTO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile Sig.ra Marta [PERSONA_1],\n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente n. [CONTO_1] presso la nostra filiale di [CITTA_1].\n\nConfermiamo di aver preso in carico la sua richiesta e le forniamo le seguenti indicazioni per procedere:\n\n1. **Documentazione necessaria**  \n   - Un documento di identità valido (carta d’identità o passaporto).  \n   - Un eventuale modulo di chiusura del conto, che può ritirare presso la filiale o scaricare dal nostro sito web.\n\n2. **Trasferimento del saldo residuo**  \n   Provvederemo a trasferire l’importo indicato (circa € 12.400) sull’IBAN da lei indicato: **IT56M0000020580414008222453**. Le chiediamo di confermare, entro 5 giorni lavorativi, che l’IBAN è corretto e di indicare eventuali riferimenti da includere nella causale del bonifico.\n\n3. **Restituzione della carta e del libretto degli assegni**  \n   La invitiamo a consegnare la carta di debito/credito e il libretto degli assegni non utilizzati direttamente in filiale al momento dell’appuntamento.\n\n4. **Appuntamento**  \n   Come da sua disponibilità, provvederemo a contattarla al numero **0422 518 207** nelle ore del mattino per concordare una data per l’incontro in filiale. Se preferisce, può anche indicare una fascia oraria più specifica o un giorno di sua preferenza rispondendo a questa email.\n\n5. **Tempistiche**  \n   Faremo il possibile per completare tutte le operazioni richieste entro il **31 dicembre 2026**, come da sua indicazione.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento o per assisterla nella compilazione dei moduli necessari. La preghiamo di farci pervenire, appena possibile, la documentazione richiesta per evitare ritardi nella chiusura del conto.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nCredito Valdorsa  \nTelefono: 02 1234 5678  \nEmail: assistenza@creditovaldrorsa.it  ",
     "restored": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile Sig.ra Marta Zanchetti,\n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente n. 000041227385 presso la nostra filiale di Treviso.\n\nConfermiamo di aver preso in carico la sua richiesta e le forniamo le seguenti indicazioni per procedere:\n\n1. **Documentazione necessaria**  \n   - Un documento di identità valido (carta d’identità o passaporto).  \n   - Un eventuale modulo di chiusura del conto, che può ritirare presso la filiale o scaricare dal nostro sito web.\n\n2. **Trasferimento del saldo residuo**  \n   Provvederemo a trasferire l’importo indicato (circa € 12.400) sull’IBAN da lei indicato: **IT56M0000020580414008222453**. Le chiediamo di confermare, entro 5 giorni lavorativi, che l’IBAN è corretto e di indicare eventuali riferimenti da includere nella causale del bonifico.\n\n3. **Restituzione della carta e del libretto degli assegni**  \n   La invitiamo a consegnare la carta di debito/credito e il libretto degli assegni non utilizzati direttamente in filiale al momento dell’appuntamento.\n\n4. **Appuntamento**  \n   Come da sua disponibilità, provvederemo a contattarla al numero **0422 518 207** nelle ore del mattino per concordare una data per l’incontro in filiale. Se preferisce, può anche indicare una fascia oraria più specifica o un giorno di sua preferenza rispondendo a questa email.\n\n5. **Tempistiche**  \n   Faremo il possibile per completare tutte le operazioni richieste entro il **31 dicembre 2026**, come da sua indicazione.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento o per assisterla nella compilazione dei moduli necessari. La preghiamo di farci pervenire, appena possibile, la documentazione richiesta per evitare ritardi nella chiusura del conto.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nCredito Valdorsa  \nTelefono: 02 1234 5678  \nEmail: assistenza@creditovaldrorsa.it  ",
     "events": [
      {
       "surrogate": "[PERSONA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_NASCITA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CONTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "bd5400e9b707"
    },
    "D2+R2": {
     "spans": [
      {
       "start": 103,
       "end": 112,
       "text": "Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 122,
       "end": 132,
       "text": "14/02/1961",
       "type": "DATA_NASCITA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 208,
       "end": 220,
       "text": "000041227385",
       "type": "CONTO",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 249,
       "end": 256,
       "text": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 379,
       "end": 385,
       "text": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 766,
       "end": 775,
       "text": "Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile Credito Valdorsa,\n\nio sottoscritta Marta Vannucci, nata il [DATA_NASCITA_1], codice fiscale ZNCMRT61B54X212O, chiedo la chiusura del conto corrente n. 376692133275 aperto presso la filiale di Rieti.\n\nDal 1 gennaio 2027 andrò in pensione dopo trent'anni come insegnante di scuola primaria e mi trasferirò da mia figlia a Biella. Vi chiedo di trasferire il saldo residuo, circa 12.400 euro, sul conto a me intestato presso un'altra banca, IBAN IT56M0000020580414008222453, e di chiudere il rapporto entro il 31 dicembre 2026.\n\nRestituirò in filiale la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al 0422 518 207 nelle ore del mattino.\n\nDistinti saluti,\nMarta Vannucci\n",
     "disclosure": [
      {
       "surrogate": "Vannucci",
       "value": "Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[DATA_NASCITA_1]",
       "value": "14/02/1961",
       "type": "DATA_NASCITA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "376692133275",
       "value": "000041227385",
       "type": "CONTO",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Rieti",
       "value": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Biella",
       "value": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nSpett.le Sig.ra Marta Vannucci,  \n\nla ringraziamo per la sua comunicazione del [DATA] relativa alla chiusura del conto corrente n. 376692133275.  \n\nConfermiamo di aver ricevuto la sua richiesta di:\n\n* chiusura del conto corrente n. 376692133275 entro il 31 dicembre 2026;  \n* trasferimento del saldo residuo (circa 12 400 euro) sul conto intestato a suo nome presso altra banca, IBAN IT56M0000020580414008222453;  \n* restituzione in filiale della carta di pagamento e del libretto degli assegni non utilizzati;  \n* fissazione di un appuntamento telefonico al 0422 518 207, nelle ore del mattino, per completare le operazioni necessarie.  \n\nPer procedere con la chiusura, le chiediamo gentilmente di recarsi presso la filiale di Rieti portando con sé:\n\n1. Un documento di identità valido;  \n2. Il codice fiscale (ZNCMRT61B54X212O);  \n3. La carta di pagamento e il libretto degli assegni (se ancora in suo possesso);  \n4. Eventuali eventuali istruzioni scritte per il trasferimento del saldo (se desidera specificare ulteriori dettagli).  \n\nUna volta ricevuti i suddetti documenti, provvederemo a:\n\n* chiudere il conto entro la data indicata;  \n* effettuare il bonifico di chiusura sull’IBAN fornito;  \n* inviarle una conferma scritta dell’avvenuta chiusura e del trasferimento dei fondi.  \n\nNel caso avesse bisogno di ulteriori chiarimenti o volesse modificare la data dell’appuntamento, non esiti a contattarci al numero 0422 518 207 o via e‑mail all’indirizzo servizioclienti@creditovaldrorsa.it.  \n\nRestiamo a sua completa disposizione e le porgiamo i nostri più cordiali saluti.  \n\n---  \n\n**Credito Valdorsa – Servizio Clienti**  \nFiliale di Rieti – Via [INDIRIZZO_FILIALE] – 02035 Rieti (RI)  \nTel. 0422 518 207 – Fax 0422 518 208  \nE‑mail: servizioclienti@creditovaldrorsa.it  \nSito web: www.creditovaldrorsa.it  ",
     "restored": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nSpett.le Sig.ra Marta Zanchetti,  \n\nla ringraziamo per la sua comunicazione del [DATA] relativa alla chiusura del conto corrente n. 000041227385.  \n\nConfermiamo di aver ricevuto la sua richiesta di:\n\n* chiusura del conto corrente n. 000041227385 entro il 31 dicembre 2026;  \n* trasferimento del saldo residuo (circa 12 400 euro) sul conto intestato a suo nome presso altra banca, IBAN IT56M0000020580414008222453;  \n* restituzione in filiale della carta di pagamento e del libretto degli assegni non utilizzati;  \n* fissazione di un appuntamento telefonico al 0422 518 207, nelle ore del mattino, per completare le operazioni necessarie.  \n\nPer procedere con la chiusura, le chiediamo gentilmente di recarsi presso la filiale di Treviso portando con sé:\n\n1. Un documento di identità valido;  \n2. Il codice fiscale (ZNCMRT61B54X212O);  \n3. La carta di pagamento e il libretto degli assegni (se ancora in suo possesso);  \n4. Eventuali eventuali istruzioni scritte per il trasferimento del saldo (se desidera specificare ulteriori dettagli).  \n\nUna volta ricevuti i suddetti documenti, provvederemo a:\n\n* chiudere il conto entro la data indicata;  \n* effettuare il bonifico di chiusura sull’IBAN fornito;  \n* inviarle una conferma scritta dell’avvenuta chiusura e del trasferimento dei fondi.  \n\nNel caso avesse bisogno di ulteriori chiarimenti o volesse modificare la data dell’appuntamento, non esiti a contattarci al numero 0422 518 207 o via e‑mail all’indirizzo servizioclienti@creditovaldrorsa.it.  \n\nRestiamo a sua completa disposizione e le porgiamo i nostri più cordiali saluti.  \n\n---  \n\n**Credito Valdorsa – Servizio Clienti**  \nFiliale di Treviso – Via [INDIRIZZO_FILIALE] – 02035 Treviso (RI)  \nTel. 0422 518 207 – Fax 0422 518 208  \nE‑mail: servizioclienti@creditovaldrorsa.it  \nSito web: www.creditovaldrorsa.it  ",
     "events": [
      {
       "surrogate": "Vannucci",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_NASCITA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "376692133275",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Rieti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Biella",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "ec47ad42dada"
    },
    "D3+R1": {
     "spans": [
      {
       "start": 62,
       "end": 78,
       "text": "Credito Valdorsa",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 190,
       "end": 220,
       "text": "conto corrente n. 000041227385",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3"
      },
      {
       "start": 238,
       "end": 245,
       "text": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 249,
       "end": 256,
       "text": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 263,
       "end": 277,
       "text": "1 gennaio 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 317,
       "end": 346,
       "text": "insegnante di scuola primaria",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 379,
       "end": 385,
       "text": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 435,
       "end": 446,
       "text": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 565,
       "end": 581,
       "text": "31 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 598,
       "end": 605,
       "text": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile [AZIENDA_1],\n\nio sottoscritta Marta Zanchetti, nata il 14/02/1961, codice fiscale ZNCMRT61B54X212O, chiedo la chiusura del [UTENTE_1] aperto presso la [STRUTTURA_1] di [CITTA_1].\n\nDal [DATA_1] andrò in pensione dopo trent'anni come [RUOLO_1] e mi trasferirò da mia figlia a [CITTA_2]. Vi chiedo di trasferire il saldo residuo, circa [IMPORTO_1], sul conto a me intestato presso un'altra banca, IBAN IT56M0000020580414008222453, e di chiudere il rapporto entro il [DATA_2].\n\nRestituirò in [STRUTTURA_1] la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al 0422 518 207 nelle ore del mattino.\n\nDistinti saluti,\nMarta Zanchetti\n",
     "disclosure": [
      {
       "surrogate": "[AZIENDA_1]",
       "value": "Credito Valdorsa",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'istituto bancario"
      },
      {
       "surrogate": "[UTENTE_1]",
       "value": "conto corrente n. 000041227385",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "sede di un istituto bancario"
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località della [STRUTTURA_1]"
      },
      {
       "surrogate": "[DATA_1]",
       "value": "1 gennaio 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di pensione"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "insegnante di scuola primaria",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "professione del richiedente"
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "destinazione del trasferimento"
      },
      {
       "surrogate": "[IMPORTO_1]",
       "value": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "somma da trasferire"
      },
      {
       "surrogate": "[DATA_2]",
       "value": "31 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nSpett.le Sig.ra Marta Zanchetti,  \n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente [UTENTE_1] aperto presso la nostra filiale di [STRUTTURA_1] a [CITTA_1].\n\nConfermiamo di aver preso in carico la sua richiesta e le comunichiamo quanto segue:\n\n1. **Procedura di chiusura**  \n   - Provvederemo a chiudere il rapporto corrente entro il [DATA_2], come da sua indicazione.  \n   - Il saldo residuo, pari a circa [IMPORTO_1], sarà accreditato sul conto da lei indicato, IBAN IT56M0000020580414008222453.  \n\n2. **Restituzione della carta e del libretto degli assegni**  \n   - La invitiamo a recarsi presso la filiale di [STRUTTURA_1] per consegnare la carta di debito e il libretto degli assegni non utilizzati.  \n   - Qualora preferisse inviare la documentazione tramite corriere, la preghiamo di comunicarcelo così da fornirle l’indirizzo di recapito.\n\n3. **Appuntamento**  \n   - Per fissare l’appuntamento, la contatteremo al numero 0422 518 207 nelle ore del mattino, come da sua disponibilità.  \n   - In alternativa, può indicarci una data e un orario di sua preferenza rispondendo a questa email.\n\n4. **Documentazione necessaria**  \n   - Per completare la chiusura sarà necessario presentare un documento di identità valido e il codice fiscale.  \n   - Qualora avesse già provveduto a consegnare tali documenti, la preghiamo di ignorare questo punto.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento o necessità. La preghiamo di confermare la ricezione di questa email e di comunicarci eventuali variazioni rispetto a quanto sopra indicato.\n\nCordiali saluti,  \n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \n[AZIENDA_1]  \nTelefono: [NUMERO_TEL_1]  \nEmail: [EMAIL_1]  ",
     "restored": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nSpett.le Sig.ra Marta Zanchetti,  \n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente conto corrente n. 000041227385 aperto presso la nostra filiale di filiale a Treviso.\n\nConfermiamo di aver preso in carico la sua richiesta e le comunichiamo quanto segue:\n\n1. **Procedura di chiusura**  \n   - Provvederemo a chiudere il rapporto corrente entro il 31 dicembre 2026, come da sua indicazione.  \n   - Il saldo residuo, pari a circa 12.400 euro, sarà accreditato sul conto da lei indicato, IBAN IT56M0000020580414008222453.  \n\n2. **Restituzione della carta e del libretto degli assegni**  \n   - La invitiamo a recarsi presso la filiale di filiale per consegnare la carta di debito e il libretto degli assegni non utilizzati.  \n   - Qualora preferisse inviare la documentazione tramite corriere, la preghiamo di comunicarcelo così da fornirle l’indirizzo di recapito.\n\n3. **Appuntamento**  \n   - Per fissare l’appuntamento, la contatteremo al numero 0422 518 207 nelle ore del mattino, come da sua disponibilità.  \n   - In alternativa, può indicarci una data e un orario di sua preferenza rispondendo a questa email.\n\n4. **Documentazione necessaria**  \n   - Per completare la chiusura sarà necessario presentare un documento di identità valido e il codice fiscale.  \n   - Qualora avesse già provveduto a consegnare tali documenti, la preghiamo di ignorare questo punto.\n\nRimaniamo a disposizione per qualsiasi ulteriore chiarimento o necessità. La preghiamo di confermare la ricezione di questa email e di comunicarci eventuali variazioni rispetto a quanto sopra indicato.\n\nCordiali saluti,  \n\n[Nome Cognome]  \nResponsabile Servizio Clienti  \nCredito Valdorsa  \nTelefono: [NUMERO_TEL_1]  \nEmail: [EMAIL_1]  ",
     "events": [
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "hallucinated_token",
       "found_as": "[EMAIL_1]"
      },
      {
       "surrogate": "[NUMERO_TEL_1]",
       "outcome": "hallucinated_token",
       "found_as": "[NUMERO_TEL_1]"
      }
     ],
     "fully_restored": false,
     "run_id": "e22c1b81bcc5"
    },
    "D3+R2": {
     "spans": [
      {
       "start": 62,
       "end": 78,
       "text": "Credito Valdorsa",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 190,
       "end": 220,
       "text": "conto corrente n. 000041227385",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3"
      },
      {
       "start": 238,
       "end": 245,
       "text": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 249,
       "end": 256,
       "text": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 263,
       "end": 277,
       "text": "1 gennaio 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 317,
       "end": 346,
       "text": "insegnante di scuola primaria",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 379,
       "end": 385,
       "text": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 435,
       "end": 446,
       "text": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 565,
       "end": 581,
       "text": "31 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 598,
       "end": 605,
       "text": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile Cassa Rurale Valfiorita,\n\nio sottoscritta Marta Zanchetti, nata il 14/02/1961, codice fiscale ZNCMRT61B54X212O, chiedo la chiusura del kmslu miijhyed l. 015529480227 aperto presso la [STRUTTURA_1] di Rieti.\n\nDal 3 gennaio 2027 andrò in pensione dopo trent'anni come [RUOLO_1] e mi trasferirò da mia figlia a Biella. Vi chiedo di trasferire il saldo residuo, circa 98.937 euro, sul conto a me intestato presso un'altra banca, IBAN IT56M0000020580414008222453, e di chiudere il rapporto entro il 14 dicembre 2026.\n\nRestituirò in [STRUTTURA_1] la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al 0422 518 207 nelle ore del mattino.\n\nDistinti saluti,\nMarta Zanchetti\n",
     "disclosure": [
      {
       "surrogate": "Cassa Rurale Valfiorita",
       "value": "Credito Valdorsa",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'istituto bancario"
      },
      {
       "surrogate": "kmslu miijhyed l. 015529480227",
       "value": "conto corrente n. 000041227385",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "sede di un istituto bancario"
      },
      {
       "surrogate": "Rieti",
       "value": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località della [STRUTTURA_1]"
      },
      {
       "surrogate": "3 gennaio 2027",
       "value": "1 gennaio 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di pensione"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "insegnante di scuola primaria",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "professione del richiedente"
      },
      {
       "surrogate": "Biella",
       "value": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "destinazione del trasferimento"
      },
      {
       "surrogate": "98.937 euro",
       "value": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "somma da trasferire"
      },
      {
       "surrogate": "14 dicembre 2026",
       "value": "31 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile Sig.ra Marta Zanchetti,\n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente n. 015529480227 aperto presso la **[STRUTTURA_1]** di Rieti.\n\nConfermiamo di aver preso in carico la sua richiesta e le comunichiamo quanto segue:\n\n1. **Procedura di chiusura**  \n   - Provvederemo a chiudere il rapporto corrente entro il 14 dicembre 2026, come da sua indicazione.  \n   - Il saldo residuo, pari a circa € 98.937, sarà trasferito sull’IBAN da lei indicato (IT56M0000020580414008222453).  \n\n2. **Restituzione della carta e del libretto assegni**  \n   - La invitiamo a recarsi presso la **[STRUTTURA_1]** per consegnare la carta di debito e il libretto degli assegni non utilizzati.  \n\n3. **Appuntamento**  \n   - Per concordare la data e l’orario dell’appuntamento, il nostro sportello la contatterà al numero 0422 518 207 nelle ore del mattino, come da sua preferenza.  \n\n4. **Documentazione necessaria**  \n   - Per completare la procedura, le chiediamo di presentare un documento di identità valido e il codice fiscale al momento della consegna della carta e del libretto.  \n\n5. **Comunicazioni future**  \n   - Qualora avesse ulteriori richieste o necessitasse di chiarimenti, non esiti a contattarci via email all’indirizzo assistenza@cassaruralevalfiorita.it o telefonicamente al numero sopra indicato.\n\nLe auguriamo una serena transizione verso la pensione e il nuovo capitolo a Biella.\n\nDistinti saluti,\n\n**[NOME_RESPONSABILE]**  \nResponsabile Servizio Clienti  \nCassa Rurale Valfiorita  \nTelefono: 0422 518 207  \nEmail: assistenza@cassaruralevalfiorita.it  ",
     "restored": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile Sig.ra Marta Zanchetti,\n\nla ringraziamo per la sua comunicazione relativa alla chiusura del conto corrente n. 015529480227 aperto presso la **filiale** di Treviso.\n\nConfermiamo di aver preso in carico la sua richiesta e le comunichiamo quanto segue:\n\n1. **Procedura di chiusura**  \n   - Provvederemo a chiudere il rapporto corrente entro il 31 dicembre 2026, come da sua indicazione.  \n   - Il saldo residuo, pari a circa 12.400 euro, sarà trasferito sull’IBAN da lei indicato (IT56M0000020580414008222453).  \n\n2. **Restituzione della carta e del libretto assegni**  \n   - La invitiamo a recarsi presso la **filiale** per consegnare la carta di debito e il libretto degli assegni non utilizzati.  \n\n3. **Appuntamento**  \n   - Per concordare la data e l’orario dell’appuntamento, il nostro sportello la contatterà al numero 0422 518 207 nelle ore del mattino, come da sua preferenza.  \n\n4. **Documentazione necessaria**  \n   - Per completare la procedura, le chiediamo di presentare un documento di identità valido e il codice fiscale al momento della consegna della carta e del libretto.  \n\n5. **Comunicazioni future**  \n   - Qualora avesse ulteriori richieste o necessitasse di chiarimenti, non esiti a contattarci via email all’indirizzo assistenza@cassaruralevalfiorita.it o telefonicamente al numero sopra indicato.\n\nLe auguriamo una serena transizione verso la pensione e il nuovo capitolo a Padova.\n\nDistinti saluti,\n\n**[NOME_RESPONSABILE]**  \nResponsabile Servizio Clienti  \nCredito Valdorsa  \nTelefono: 0422 518 207  \nEmail: assistenza@cassaruralevalfiorita.it  ",
     "events": [
      {
       "surrogate": "Cassa Rurale Valfiorita",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "kmslu miijhyed l. 015529480227",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Rieti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "3 gennaio 2027",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Biella",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "98.937 euro",
       "outcome": "restored",
       "found_as": "€ 98.937"
      },
      {
       "surrogate": "14 dicembre 2026",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "78d5c21f1f74"
    },
    "D4+R1": {
     "spans": [
      {
       "start": 62,
       "end": 78,
       "text": "Credito Valdorsa",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 97,
       "end": 112,
       "text": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 122,
       "end": 132,
       "text": "14/02/1961",
       "type": "DATA_NASCITA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 149,
       "end": 165,
       "text": "ZNCMRT61B54X212O",
       "type": "CF",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 190,
       "end": 220,
       "text": "conto corrente n. 000041227385",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3"
      },
      {
       "start": 238,
       "end": 245,
       "text": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 249,
       "end": 256,
       "text": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 263,
       "end": 277,
       "text": "1 gennaio 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 317,
       "end": 346,
       "text": "insegnante di scuola primaria",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 379,
       "end": 385,
       "text": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 435,
       "end": 446,
       "text": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 501,
       "end": 528,
       "text": "IT56M0000020580414008222453",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 565,
       "end": 581,
       "text": "31 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 598,
       "end": 605,
       "text": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 706,
       "end": 718,
       "text": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 760,
       "end": 775,
       "text": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile [PERSONA_1],\n\nio sottoscritta [PERSONA_2_F], nata il [DATA_NASCITA_1], codice fiscale [CF_1], chiedo la chiusura del [UTENTE_1] aperto presso la [STRUTTURA_1] di [CITTA_1].\n\nDal [DATA_1] andrò in pensione dopo trent'anni come [RUOLO_1] e mi trasferirò da mia figlia a [CITTA_2]. Vi chiedo di trasferire il saldo residuo, circa [IMPORTO_1], sul conto a me intestato presso un'altra banca, IBAN [IBAN_1], e di chiudere il rapporto entro il [DATA_2].\n\nRestituirò in [STRUTTURA_1] la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al [TELEFONO_1] nelle ore del mattino.\n\nDistinti saluti,\n[PERSONA_2_F]\n",
     "disclosure": [
      {
       "surrogate": "[PERSONA_1]",
       "value": "Credito Valdorsa",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_2_F]",
       "value": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[DATA_NASCITA_1]",
       "value": "14/02/1961",
       "type": "DATA_NASCITA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CF_1]",
       "value": "ZNCMRT61B54X212O",
       "type": "CF",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "value": "conto corrente n. 000041227385",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "sede di un istituto bancario"
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località della [STRUTTURA_1]"
      },
      {
       "surrogate": "[DATA_1]",
       "value": "1 gennaio 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di pensione"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "insegnante di scuola primaria",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "professione del richiedente"
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "destinazione del trasferimento"
      },
      {
       "surrogate": "[IMPORTO_1]",
       "value": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "somma da trasferire"
      },
      {
       "surrogate": "[IBAN_1]",
       "value": "IT56M0000020580414008222453",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[DATA_2]",
       "value": "31 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile [PERSONA_2_F],\n\nla ringraziamo per averci comunicato la sua intenzione di chiudere il conto corrente [UTENTE_1] presso la nostra filiale di [CITTA_1].\n\nConfermiamo di aver ricevuto la sua richiesta e provvederemo a:\n\n1. Verificare la documentazione necessaria per la chiusura del rapporto (carta di credito, libretto degli assegni, eventuali deleghe o firme mancanti).  \n2. Trasferire il saldo residuo di circa [IMPORTO_1] sull’IBAN da lei indicato ([IBAN_1]) entro la data da lei indicata ([DATA_2]), salvo eventuali verifiche di sicurezza.  \n3. Aggiornare il nostro archivio con la sua nuova residenza a [CITTA_2] e la data di pensionamento a partire dal [DATA_1].\n\nPer completare la procedura, le chiediamo gentilmente di recarsi presso la filiale di [STRUTTURA_1] con:\n\n- Un documento di identità valido.  \n- Il libretto degli assegni non utilizzati (se ancora in suo possesso).  \n- La carta di debito/credito associata al conto.\n\nLe confermiamo che il nostro operatore la contatterà al numero [TELEFONO_1] nelle ore del mattino per concordare l’appuntamento più comodo per la consegna della carta e del libretto.\n\nNel frattempo, se avesse ulteriori domande o necessitasse di chiarimenti, non esiti a rispondere a questa email o a contattarci al numero [TELEFONO_1].\n\nRestiamo a sua completa disposizione.\n\nCordiali saluti,\n\n[PERSONA_1]  \n[RUOLO_1] – [STRUTTURA_1]  \n[TELEFONO_1]  \n[EMAIL_1]   (se presente)  ",
     "restored": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile Marta Zanchetti,\n\nla ringraziamo per averci comunicato la sua intenzione di chiudere il conto corrente conto corrente n. 000041227385 presso la nostra filiale di Treviso.\n\nConfermiamo di aver ricevuto la sua richiesta e provvederemo a:\n\n1. Verificare la documentazione necessaria per la chiusura del rapporto (carta di credito, libretto degli assegni, eventuali deleghe o firme mancanti).  \n2. Trasferire il saldo residuo di circa 12.400 euro sull’IBAN da lei indicato (IT56M0000020580414008222453) entro la data da lei indicata (31 dicembre 2026), salvo eventuali verifiche di sicurezza.  \n3. Aggiornare il nostro archivio con la sua nuova residenza a Padova e la data di pensionamento a partire dal 1 gennaio 2027.\n\nPer completare la procedura, le chiediamo gentilmente di recarsi presso la filiale di filiale con:\n\n- Un documento di identità valido.  \n- Il libretto degli assegni non utilizzati (se ancora in suo possesso).  \n- La carta di debito/credito associata al conto.\n\nLe confermiamo che il nostro operatore la contatterà al numero 0422 518 207 nelle ore del mattino per concordare l’appuntamento più comodo per la consegna della carta e del libretto.\n\nNel frattempo, se avesse ulteriori domande o necessitasse di chiarimenti, non esiti a rispondere a questa email o a contattarci al numero 0422 518 207.\n\nRestiamo a sua completa disposizione.\n\nCordiali saluti,\n\nCredito Valdorsa  \ninsegnante di scuola primaria – filiale  \n0422 518 207  \n[EMAIL_1]   (se presente)  ",
     "events": [
      {
       "surrogate": "[PERSONA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_2_F]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_NASCITA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CF_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IMPORTO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[IBAN_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "hallucinated_token",
       "found_as": "[EMAIL_1]"
      }
     ],
     "fully_restored": false,
     "run_id": "933a73c866b3"
    },
    "D4+R2": {
     "spans": [
      {
       "start": 62,
       "end": 78,
       "text": "Credito Valdorsa",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 97,
       "end": 112,
       "text": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 122,
       "end": 132,
       "text": "14/02/1961",
       "type": "DATA_NASCITA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 149,
       "end": 165,
       "text": "ZNCMRT61B54X212O",
       "type": "CF",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 190,
       "end": 220,
       "text": "conto corrente n. 000041227385",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3"
      },
      {
       "start": 238,
       "end": 245,
       "text": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 249,
       "end": 256,
       "text": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 263,
       "end": 277,
       "text": "1 gennaio 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 317,
       "end": 346,
       "text": "insegnante di scuola primaria",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 379,
       "end": 385,
       "text": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 435,
       "end": 446,
       "text": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 501,
       "end": 528,
       "text": "IT56M0000020580414008222453",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 565,
       "end": 581,
       "text": "31 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 598,
       "end": 605,
       "text": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 706,
       "end": 718,
       "text": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 760,
       "end": 775,
       "text": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: richiesta di chiusura del conto corrente\n\nSpettabile Flavia Marangoni,\n\nio sottoscritta Berenice Guidotti, nata il [DATA_NASCITA_1], codice fiscale PDTSZP62M13X644O, chiedo la chiusura del kmslu miijhyed l. 015529480227 aperto presso la [STRUTTURA_1] di Rieti.\n\nDal 3 gennaio 2027 andrò in pensione dopo trent'anni come [RUOLO_1] e mi trasferirò da mia figlia a Biella. Vi chiedo di trasferire il saldo residuo, circa 98.937 euro, sul conto a me intestato presso un'altra banca, IBAN IT12I0000070505262103716231, e di chiudere il rapporto entro il 14 dicembre 2026.\n\nRestituirò in [STRUTTURA_1] la carta e il libretto degli assegni non utilizzati. Per fissare l'appuntamento potete chiamarmi al 0805 976 702 nelle ore del mattino.\n\nDistinti saluti,\nBerenice Guidotti\n",
     "disclosure": [
      {
       "surrogate": "Flavia Marangoni",
       "value": "Credito Valdorsa",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Berenice Guidotti",
       "value": "Marta Zanchetti",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[DATA_NASCITA_1]",
       "value": "14/02/1961",
       "type": "DATA_NASCITA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "PDTSZP62M13X644O",
       "value": "ZNCMRT61B54X212O",
       "type": "CF",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "kmslu miijhyed l. 015529480227",
       "value": "conto corrente n. 000041227385",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "filiale",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "sede di un istituto bancario"
      },
      {
       "surrogate": "Rieti",
       "value": "Treviso",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località della [STRUTTURA_1]"
      },
      {
       "surrogate": "3 gennaio 2027",
       "value": "1 gennaio 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di pensione"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "insegnante di scuola primaria",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "professione del richiedente"
      },
      {
       "surrogate": "Biella",
       "value": "Padova",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "destinazione del trasferimento"
      },
      {
       "surrogate": "98.937 euro",
       "value": "12.400 euro",
       "type": "IMPORTO",
       "cls": "quasi",
       "source": "D3",
       "reason": "somma da trasferire"
      },
      {
       "surrogate": "IT12I0000070505262103716231",
       "value": "IT56M0000020580414008222453",
       "type": "IBAN",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "14 dicembre 2026",
       "value": "31 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "0805 976 702",
       "value": "0422 518 207",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile Sig.ra Berenice Guidotti,\n\nla ringraziamo per la sua comunicazione e confermiamo di aver ricevuto la sua richiesta di chiusura del conto corrente n. 015529480227, aperto presso la **[STRUTTURA_1]** di Rieti.\n\nIn merito alla sua richiesta, le confermiamo quanto segue:\n\n1. **Procedura di chiusura** – provvederemo a chiudere il rapporto bancario entro il **14 dicembre 2026**, come indicato.  \n2. **Trasferimento del saldo** – il saldo residuo di circa **98.937 euro** sarà accreditato sul conto da lei indicato, con IBAN **IT12I0000070505262103716231**.  \n3. **Restituzione della carta e del libretto** – potrà riconsegnare la carta di debito e il libretto degli assegni non utilizzati presso la **[STRUTTURA_1]**.  \n4. **Appuntamento** – per concordare la data e l’orario dell’appuntamento, provvederemo a contattarla al numero **0805 976 702** nelle ore del mattino, come da sua preferenza.  \n\nLe ricordiamo che, a partire dal **3 gennaio 2027**, entrerà in pensione dopo trent’anni di servizio come **[RUOLO_1]** e si trasferirà a Biella. Qualora avesse ulteriori esigenze o volesse modificare qualche dettaglio della procedura, non esiti a comunicarcelo.\n\nRimaniamo a disposizione per qualsiasi chiarimento e le porgiamo i nostri più cordiali saluti.\n\nDistinti saluti,\n\n**[NOME_RESPONSABILE]**  \nResponsabile Servizio Clienti  \n[STRUTTURA_1] – Rieti  \nTelefono: 0805 976 702  \nEmail: assistenza@[STRUTTURA_1].it  ",
     "restored": "**Oggetto:** Re: richiesta di chiusura del conto corrente  \n\nGentile Sig.ra Marta Zanchetti,\n\nla ringraziamo per la sua comunicazione e confermiamo di aver ricevuto la sua richiesta di chiusura del conto corrente n. 015529480227, aperto presso la **filiale** di Treviso.\n\nIn merito alla sua richiesta, le confermiamo quanto segue:\n\n1. **Procedura di chiusura** – provvederemo a chiudere il rapporto bancario entro il **31 dicembre 2026**, come indicato.  \n2. **Trasferimento del saldo** – il saldo residuo di circa **12.400 euro** sarà accreditato sul conto da lei indicato, con IBAN **IT56M0000020580414008222453**.  \n3. **Restituzione della carta e del libretto** – potrà riconsegnare la carta di debito e il libretto degli assegni non utilizzati presso la **filiale**.  \n4. **Appuntamento** – per concordare la data e l’orario dell’appuntamento, provvederemo a contattarla al numero **0422 518 207** nelle ore del mattino, come da sua preferenza.  \n\nLe ricordiamo che, a partire dal **1 gennaio 2027**, entrerà in pensione dopo trent’anni di servizio come **insegnante di scuola primaria** e si trasferirà a Padova. Qualora avesse ulteriori esigenze o volesse modificare qualche dettaglio della procedura, non esiti a comunicarcelo.\n\nRimaniamo a disposizione per qualsiasi chiarimento e le porgiamo i nostri più cordiali saluti.\n\nDistinti saluti,\n\n**[NOME_RESPONSABILE]**  \nResponsabile Servizio Clienti  \nfiliale – Treviso  \nTelefono: 0422 518 207  \nEmail: assistenza@filiale.it  ",
     "events": [
      {
       "surrogate": "Flavia Marangoni",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Berenice Guidotti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_NASCITA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "PDTSZP62M13X644O",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "kmslu miijhyed l. 015529480227",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Rieti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "3 gennaio 2027",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Biella",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "98.937 euro",
       "outcome": "restored",
       "found_as": "98.937 euro"
      },
      {
       "surrogate": "IT12I0000070505262103716231",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "14 dicembre 2026",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "0805 976 702",
       "outcome": "restored",
       "found_as": "0805 976 702"
      }
     ],
     "fully_restored": true,
     "run_id": "65b4d39c07a9"
    }
   },
   "calc_blocked": {
    "D0": {
     "IMPORTO": 1
    },
    "D1": {
     "DATA": 1
    },
    "D2": {
     "DATA_NASCITA": 1
    },
    "D3": {
     "IMPORTO": 1,
     "DATA": 2
    },
    "D4": {
     "IMPORTO": 1,
     "DATA": 2,
     "DATA_NASCITA": 1
    }
   }
  },
  {
   "id": "fx-hr-01",
   "domain": "hr",
   "scenario": "sick_leave",
   "text": "Oggetto: comunicazione di assenza per malattia\n\nGentile Ufficio Risorse Umane,\n\nsono Davide Sorrentino, magazziniere del turno di notte nello stabilimento di Nola, matricola NL-20417. Vi informo che da lunedì 16 novembre 2026 sarò assente per malattia: il medico di base mi ha diagnosticato un'ernia del disco lombare e mi ha prescritto riposo fino al 5 dicembre 2026. Il certificato telematico è già stato trasmesso all'INPS.\n\nDurante la convalescenza seguirò un ciclo di fisioterapia presso il poliambulatorio di Pomigliano, tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il capoturno, così da riorganizzare i turni del reparto spedizioni.\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al 081 512 3348 o scrivermi a davide.sorrentino@example.org.\n\nGrazie e cordiali saluti,\nDavide Sorrentino\n",
   "runs": {
    "D0+R1": {
     "spans": [
      {
       "start": 791,
       "end": 803,
       "text": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 818,
       "end": 847,
       "text": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per malattia\n\nGentile Ufficio Risorse Umane,\n\nsono Davide Sorrentino, magazziniere del turno di notte nello stabilimento di Nola, matricola NL-20417. Vi informo che da lunedì 16 novembre 2026 sarò assente per malattia: il medico di base mi ha diagnosticato un'ernia del disco lombare e mi ha prescritto riposo fino al 5 dicembre 2026. Il certificato telematico è già stato trasmesso all'INPS.\n\nDurante la convalescenza seguirò un ciclo di fisioterapia presso il poliambulatorio di Pomigliano, tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il capoturno, così da riorganizzare i turni del reparto spedizioni.\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al [TELEFONO_1] o scrivermi a [EMAIL_1].\n\nGrazie e cordiali saluti,\nDavide Sorrentino\n",
     "disclosure": [
      {
       "surrogate": "[TELEFONO_1]",
       "value": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Sorrentino,\n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza dal 16 novembre 2026 al 5 dicembre 2026 e di aver provveduto a informare il capoturno affinché possa riorganizzare i turni del reparto spedizioni.  \n\nIl certificato telematico inviato all’INPS è stato correttamente ricevuto; qualora fosse necessario inviarci una copia cartacea o un estratto per i nostri archivi, la preghiamo di farcelo sapere.\n\nPer eventuali esigenze operative o richieste di documentazione, rimaniamo a disposizione al numero [TELEFONO_1] o all’indirizzo email [EMAIL_1].\n\nLe auguriamo una pronta guarigione e una buona ripresa.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Ufficio Risorse Umane  \n[Nome Azienda]  \n[Telefono aziendale]  \n[Email aziendale]",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Sorrentino,\n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza dal 16 novembre 2026 al 5 dicembre 2026 e di aver provveduto a informare il capoturno affinché possa riorganizzare i turni del reparto spedizioni.  \n\nIl certificato telematico inviato all’INPS è stato correttamente ricevuto; qualora fosse necessario inviarci una copia cartacea o un estratto per i nostri archivi, la preghiamo di farcelo sapere.\n\nPer eventuali esigenze operative o richieste di documentazione, rimaniamo a disposizione al numero 081 512 3348 o all’indirizzo email davide.sorrentino@example.org.\n\nLe auguriamo una pronta guarigione e una buona ripresa.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Ufficio Risorse Umane  \n[Nome Azienda]  \n[Telefono aziendale]  \n[Email aziendale]",
     "events": [
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "a3c06360ce07"
    },
    "D0+R2": {
     "spans": [
      {
       "start": 791,
       "end": 803,
       "text": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 818,
       "end": 847,
       "text": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per malattia\n\nGentile Ufficio Risorse Umane,\n\nsono Davide Sorrentino, magazziniere del turno di notte nello stabilimento di Nola, matricola NL-20417. Vi informo che da lunedì 16 novembre 2026 sarò assente per malattia: il medico di base mi ha diagnosticato un'ernia del disco lombare e mi ha prescritto riposo fino al 5 dicembre 2026. Il certificato telematico è già stato trasmesso all'INPS.\n\nDurante la convalescenza seguirò un ciclo di fisioterapia presso il poliambulatorio di Pomigliano, tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il capoturno, così da riorganizzare i turni del reparto spedizioni.\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al 024 489 9877 o scrivermi a selene.brunelleschi@example.com.\n\nGrazie e cordiali saluti,\nDavide Sorrentino\n",
     "disclosure": [
      {
       "surrogate": "024 489 9877",
       "value": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "selene.brunelleschi@example.com",
       "value": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Sorrentino,\n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza dal 16 novembre 2026 al 5 dicembre 2026, come indicato nel certificato telematico inviato all’INPS. Il suo capoturno è stato informato e provvederemo a riorganizzare i turni del reparto spedizioni per garantire la continuità operativa durante il periodo di convalescenza.\n\nLe ricordiamo di inviare, entro 5 giorni lavorativi dalla fine del periodo di riposo, il certificato di fine malattia o eventuali ulteriori documenti medici richiesti, qualora fossero necessari per la chiusura della pratica.\n\nPer qualsiasi necessità o aggiornamento relativo al suo stato di salute, può contattarci al numero interno HR‑01 o via e‑mail all’indirizzo risorseumane@azienda.it.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per ogni ulteriore supporto.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Ufficio Risorse Umane  \n[Nome Azienda]  \nTelefono: 024 123 4567  \nE‑mail: risorseumane@azienda.it  ",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Sorrentino,\n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza dal 16 novembre 2026 al 5 dicembre 2026, come indicato nel certificato telematico inviato all’INPS. Il suo capoturno è stato informato e provvederemo a riorganizzare i turni del reparto spedizioni per garantire la continuità operativa durante il periodo di convalescenza.\n\nLe ricordiamo di inviare, entro 5 giorni lavorativi dalla fine del periodo di riposo, il certificato di fine malattia o eventuali ulteriori documenti medici richiesti, qualora fossero necessari per la chiusura della pratica.\n\nPer qualsiasi necessità o aggiornamento relativo al suo stato di salute, può contattarci al numero interno HR‑01 o via e‑mail all’indirizzo risorseumane@azienda.it.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per ogni ulteriore supporto.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Ufficio Risorse Umane  \n[Nome Azienda]  \nTelefono: 024 123 4567  \nE‑mail: risorseumane@azienda.it  ",
     "events": [
      {
       "surrogate": "024 489 9877",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "selene.brunelleschi@example.com",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "1f4b787b41ab"
    },
    "D1+R1": {
     "spans": [
      {
       "start": 85,
       "end": 102,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 158,
       "end": 162,
       "text": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 174,
       "end": 182,
       "text": "NL-20417",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 421,
       "end": 425,
       "text": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 515,
       "end": 525,
       "text": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 791,
       "end": 803,
       "text": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 818,
       "end": 847,
       "text": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 876,
       "end": 893,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per malattia\n\nGentile Ufficio Risorse Umane,\n\nsono [PERSONA_1_M], magazziniere del turno di notte nello stabilimento di [CITTA_1], matricola [AZIENDA_1]. Vi informo che da lunedì 16 novembre 2026 sarò assente per malattia: il medico di base mi ha diagnosticato un'ernia del disco lombare e mi ha prescritto riposo fino al 5 dicembre 2026. Il certificato telematico è già stato trasmesso all'[AZIENDA_2].\n\nDurante la convalescenza seguirò un ciclo di fisioterapia presso il poliambulatorio di [CITTA_2], tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il capoturno, così da riorganizzare i turni del reparto spedizioni.\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al [TELEFONO_1] o scrivermi a [EMAIL_1].\n\nGrazie e cordiali saluti,\n[PERSONA_1_M]\n",
     "disclosure": [
      {
       "surrogate": "[PERSONA_1_M]",
       "value": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "value": "NL-20417",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[AZIENDA_2]",
       "value": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile [PERSONA_1_M],\n\nla ringraziamo per averci comunicato la sua situazione di salute e per aver provveduto all’invio del certificato telematico all'[AZIENDA_2].\n\nProcederemo a registrare l’assenza dal 16 novembre 2026 al 5 dicembre 2026 e a informare il capoturno affinché vengano riorganizzati i turni del reparto spedizioni.  \n\nPer eventuali necessità operative o per ulteriori chiarimenti, il nostro ufficio rimane a disposizione al numero interno [TELEFONO_UFFICI_RU] o via e‑mail all’indirizzo [EMAIL_UFFICI_RU].\n\nLe auguriamo una pronta guarigione e una buona fisioterapia presso il poliambulatorio di [CITTA_2].\n\nCordiali saluti,\n\n[Nome e Cognome]  \nResponsabile Ufficio Risorse Umane  \n[AZIENDA_1]  \n[TELEFONO_UFFICI_RU]  \n[EMAIL_UFFICI_RU]",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Davide Sorrentino,\n\nla ringraziamo per averci comunicato la sua situazione di salute e per aver provveduto all’invio del certificato telematico all'INPS.\n\nProcederemo a registrare l’assenza dal 16 novembre 2026 al 5 dicembre 2026 e a informare il capoturno affinché vengano riorganizzati i turni del reparto spedizioni.  \n\nPer eventuali necessità operative o per ulteriori chiarimenti, il nostro ufficio rimane a disposizione al numero interno [TELEFONO_UFFICI_RU] o via e‑mail all’indirizzo [EMAIL_UFFICI_RU].\n\nLe auguriamo una pronta guarigione e una buona fisioterapia presso il poliambulatorio di Pomigliano.\n\nCordiali saluti,\n\n[Nome e Cognome]  \nResponsabile Ufficio Risorse Umane  \nNL-20417  \n[TELEFONO_UFFICI_RU]  \n[EMAIL_UFFICI_RU]",
     "events": [
      {
       "surrogate": "[PERSONA_1_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "49f599e17121"
    },
    "D1+R2": {
     "spans": [
      {
       "start": 85,
       "end": 102,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 158,
       "end": 162,
       "text": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 174,
       "end": 182,
       "text": "NL-20417",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 421,
       "end": 425,
       "text": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 515,
       "end": 525,
       "text": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 791,
       "end": 803,
       "text": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 818,
       "end": 847,
       "text": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 876,
       "end": 893,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per malattia\n\nGentile Ufficio Risorse Umane,\n\nsono Corrado Ubaldini, magazziniere del turno di notte nello stabilimento di Teramo, matricola Vetreria Castagnoli S.r.l.. Vi informo che da lunedì 16 novembre 2026 sarò assente per malattia: il medico di base mi ha diagnosticato un'ernia del disco lombare e mi ha prescritto riposo fino al 5 dicembre 2026. Il certificato telematico è già stato trasmesso all'Fabbrica Tessile Morandotti S.p.A..\n\nDurante la convalescenza seguirò un ciclo di fisioterapia presso il poliambulatorio di Isernia, tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il capoturno, così da riorganizzare i turni del reparto spedizioni.\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al 024 489 9877 o scrivermi a selene.brunelleschi@example.com.\n\nGrazie e cordiali saluti,\nCorrado Ubaldini\n",
     "disclosure": [
      {
       "surrogate": "Corrado Ubaldini",
       "value": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Teramo",
       "value": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Vetreria Castagnoli S.r.l.",
       "value": "NL-20417",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Fabbrica Tessile Morandotti S.p.A.",
       "value": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Isernia",
       "value": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "024 489 9877",
       "value": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "selene.brunelleschi@example.com",
       "value": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Corrado Ubaldini,  \n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.  \n\nConfermiamo di aver registrato la sua assenza dal 16 novembre 2026 al 5 dicembre 2026, come indicato nel certificato telematico già inviato alla Fabbrica Tessile Morandotti S.p.A.  \n\nProvvederemo a informare il capoturno del reparto spedizioni affinché possa riorganizzare i turni del turno di notte.  \n\nPer eventuali necessità operative o richieste di documentazione, il nostro ufficio rimane a sua disposizione al numero 024 489 9877 o via e‑mail all’indirizzo selene.brunelleschi@example.com.  \n\nLe auguriamo una pronta guarigione e una buona fisioterapia.  \n\nCordiali saluti,  \n\n[Nome Cognome]  \nUfficio Risorse Umane  \nVetreria Castagnoli S.r.l.  \nTelefono: 024 489 9877  \nE‑mail: hr@vetreriacastagnoli.it  ",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Davide Sorrentino,  \n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.  \n\nConfermiamo di aver registrato la sua assenza dal 16 novembre 2026 al 5 dicembre 2026, come indicato nel certificato telematico già inviato alla INPS  \n\nProvvederemo a informare il capoturno del reparto spedizioni affinché possa riorganizzare i turni del turno di notte.  \n\nPer eventuali necessità operative o richieste di documentazione, il nostro ufficio rimane a sua disposizione al numero 081 512 3348 o via e‑mail all’indirizzo davide.sorrentino@example.org.  \n\nLe auguriamo una pronta guarigione e una buona fisioterapia.  \n\nCordiali saluti,  \n\n[Nome Cognome]  \nUfficio Risorse Umane  \nNL-20417  \nTelefono: 081 512 3348  \nE‑mail: hr@vetreriacastagnoli.it  ",
     "events": [
      {
       "surrogate": "Corrado Ubaldini",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Teramo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Vetreria Castagnoli S.r.l.",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Fabbrica Tessile Morandotti S.p.A.",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Isernia",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "024 489 9877",
       "outcome": "restored",
       "found_as": "024 489 9877"
      },
      {
       "surrogate": "selene.brunelleschi@example.com",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "1b498f032ac2"
    },
    "D2+R1": {
     "spans": [
      {
       "start": 85,
       "end": 102,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 158,
       "end": 162,
       "text": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 515,
       "end": 525,
       "text": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 818,
       "end": 824,
       "text": "davide",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 825,
       "end": 828,
       "text": "sor",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 883,
       "end": 893,
       "text": "Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per malattia\n\nGentile Ufficio Risorse Umane,\n\nsono [PERSONA_1_M], magazziniere del turno di notte nello stabilimento di [CITTA_1], matricola NL-20417. Vi informo che da lunedì 16 novembre 2026 sarò assente per malattia: il medico di base mi ha diagnosticato un'ernia del disco lombare e mi ha prescritto riposo fino al 5 dicembre 2026. Il certificato telematico è già stato trasmesso all'INPS.\n\nDurante la convalescenza seguirò un ciclo di fisioterapia presso il poliambulatorio di [CITTA_2], tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il capoturno, così da riorganizzare i turni del reparto spedizioni.\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al 081 512 3348 o scrivermi a [EMAIL_1].[UTENTE_1]rentino@example.org.\n\nGrazie e cordiali saluti,\nDavide [PERSONA_1_M]\n",
     "disclosure": [
      {
       "surrogate": "[PERSONA_1_M]",
       "value": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "davide",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "value": "sor",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Davide [PERSONA_1_M],\n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.  \nAbbiamo provveduto a registrare l’interruzione del servizio dal 16 novembre 2026 al 5 dicembre 2026 e a informare il capoturno affinché possa riorganizzare i turni del reparto spedizioni.\n\nIl certificato telematico inviato all’INPS è stato correttamente ricevuto e archiviato. Prenderemo nota anche del suo ciclo di fisioterapia presso il poliambulatorio di [CITTA_2] e, qualora fosse necessario, la contatteremo al suo domicilio nei giorni e negli orari indicati.\n\nPer qualsiasi ulteriore necessità o aggiornamento, non esiti a contattarci al numero interno [NUMERO_REPARTO_RU] o via e‑mail all’indirizzo HR@[AZIENDA].it.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per ogni eventuale esigenza.\n\nCordiali saluti,\n\n[Nome_Risorsa_Um]  \nUfficio Risorse Umane  \n[AZIENDA] S.p.A.  \nTelefono: [NUMERO_UFFICI_RU]  \nE‑mail: hr@[AZIENDA].it",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Davide Davide Sorrentino,\n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.  \nAbbiamo provveduto a registrare l’interruzione del servizio dal 16 novembre 2026 al 5 dicembre 2026 e a informare il capoturno affinché possa riorganizzare i turni del reparto spedizioni.\n\nIl certificato telematico inviato all’INPS è stato correttamente ricevuto e archiviato. Prenderemo nota anche del suo ciclo di fisioterapia presso il poliambulatorio di Pomigliano e, qualora fosse necessario, la contatteremo al suo domicilio nei giorni e negli orari indicati.\n\nPer qualsiasi ulteriore necessità o aggiornamento, non esiti a contattarci al numero interno [NUMERO_REPARTO_RU] o via e‑mail all’indirizzo HR@[AZIENDA].it.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per ogni eventuale esigenza.\n\nCordiali saluti,\n\n[Nome_Risorsa_Um]  \nUfficio Risorse Umane  \n[AZIENDA] S.p.A.  \nTelefono: [NUMERO_UFFICI_RU]  \nE‑mail: hr@[AZIENDA].it",
     "events": [
      {
       "surrogate": "[PERSONA_1_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "bd5400e9b707"
    },
    "D2+R2": {
     "spans": [
      {
       "start": 85,
       "end": 102,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 158,
       "end": 162,
       "text": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 515,
       "end": 525,
       "text": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 818,
       "end": 824,
       "text": "davide",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 825,
       "end": 828,
       "text": "sor",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 883,
       "end": 893,
       "text": "Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per malattia\n\nGentile Ufficio Risorse Umane,\n\nsono Corrado Ubaldini, magazziniere del turno di notte nello stabilimento di Teramo, matricola NL-20417. Vi informo che da lunedì 16 novembre 2026 sarò assente per malattia: il medico di base mi ha diagnosticato un'ernia del disco lombare e mi ha prescritto riposo fino al 5 dicembre 2026. Il certificato telematico è già stato trasmesso all'INPS.\n\nDurante la convalescenza seguirò un ciclo di fisioterapia presso il poliambulatorio di Isernia, tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il capoturno, così da riorganizzare i turni del reparto spedizioni.\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al 081 512 3348 o scrivermi a oreste.orsolini@example.com.axyrentino@example.org.\n\nGrazie e cordiali saluti,\nDavide Ubaldini\n",
     "disclosure": [
      {
       "surrogate": "Corrado Ubaldini",
       "value": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Teramo",
       "value": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Isernia",
       "value": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "oreste.orsolini@example.com",
       "value": "davide",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "axy",
       "value": "sor",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Ubaldini,\n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza dal 16 novembre 2026 al 5 dicembre 2026 e di aver provveduto a informare il capoturno affinché vengano riorganizzati i turni del reparto spedizioni.  \n\nIl certificato telematico inviato all’INPS è stato ricevuto; qualora fosse necessario un ulteriore documento o una copia per i nostri archivi, le chiediamo di farcelo pervenire entro 5 giorni lavorativi.\n\nPer qualsiasi esigenza relativa alle visite fiscali o ad altre comunicazioni, prenderemo contatto con lei al numero 081 512 3348 o via e‑mail agli indirizzi indicati.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per ogni ulteriore necessità.\n\nCordiali saluti,\n\n[Nome Cognome]  \nUfficio Risorse Umane  \n[Nome Azienda]  \n[Telefono] – [E‑mail]  ",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia  \n\nGentile Sig. Sorrentino,\n\nla ringraziamo per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza dal 16 novembre 2026 al 5 dicembre 2026 e di aver provveduto a informare il capoturno affinché vengano riorganizzati i turni del reparto spedizioni.  \n\nIl certificato telematico inviato all’INPS è stato ricevuto; qualora fosse necessario un ulteriore documento o una copia per i nostri archivi, le chiediamo di farcelo pervenire entro 5 giorni lavorativi.\n\nPer qualsiasi esigenza relativa alle visite fiscali o ad altre comunicazioni, prenderemo contatto con lei al numero 081 512 3348 o via e‑mail agli indirizzi indicati.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per ogni ulteriore necessità.\n\nCordiali saluti,\n\n[Nome Cognome]  \nUfficio Risorse Umane  \n[Nome Azienda]  \n[Telefono] – [E‑mail]  ",
     "events": [
      {
       "surrogate": "Corrado Ubaldini",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Teramo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Isernia",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "oreste.orsolini@example.com",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "axy",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "ec47ad42dada"
    },
    "D3+R1": {
     "spans": [
      {
       "start": 38,
       "end": 46,
       "text": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 104,
       "end": 116,
       "text": "magazziniere",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 158,
       "end": 162,
       "text": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 164,
       "end": 182,
       "text": "matricola NL-20417",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3"
      },
      {
       "start": 209,
       "end": 225,
       "text": "16 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 243,
       "end": 251,
       "text": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 294,
       "end": 317,
       "text": "ernia del disco lombare",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 352,
       "end": 367,
       "text": "5 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 421,
       "end": 425,
       "text": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 473,
       "end": 485,
       "text": "fisioterapia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 515,
       "end": 525,
       "text": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 603,
       "end": 612,
       "text": "capoturno",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 648,
       "end": 666,
       "text": "reparto spedizioni",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per [SALUTE_1]\n\nGentile Ufficio Risorse Umane,\n\nsono Davide Sorrentino, [RUOLO_1] del turno di notte nello stabilimento di [CITTA_1], [UTENTE_1]. Vi informo che da lunedì [DATA_1] sarò assente per [SALUTE_1]: il medico di base mi ha diagnosticato un'[SALUTE_2] e mi ha prescritto riposo fino al [DATA_2]. Il certificato telematico è già stato trasmesso all'[AZIENDA_1].\n\nDurante la convalescenza seguirò un ciclo di [SALUTE_3] presso il poliambulatorio di [CITTA_2], tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il [RUOLO_2], così da riorganizzare i turni del [STRUTTURA_1].\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al 081 512 3348 o scrivermi a davide.sorrentino@example.org.\n\nGrazie e cordiali saluti,\nDavide Sorrentino\n",
     "disclosure": [
      {
       "surrogate": "[SALUTE_1]",
       "value": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "condizione di salute che causa l'assenza"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "magazziniere",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere di chi scrive"
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località dello stabilimento"
      },
      {
       "surrogate": "[UTENTE_1]",
       "value": "matricola NL-20417",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[DATA_1]",
       "value": "16 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di inizio assenza"
      },
      {
       "surrogate": "[SALUTE_2]",
       "value": "ernia del disco lombare",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "diagnosi specifica"
      },
      {
       "surrogate": "[DATA_2]",
       "value": "5 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di fine assenza"
      },
      {
       "surrogate": "[AZIENDA_1]",
       "value": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "ente di previdenza a cui è stato trasmesso il certificato"
      },
      {
       "surrogate": "[SALUTE_3]",
       "value": "fisioterapia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "terapia prescritta"
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "value": "capoturno",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "ruolo di riferimento per la riorganizzazione dei turni"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "reparto spedizioni",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per [SALUTE_1]\n\nGentile Davide Sorrentino,\n\nla ringrazio per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver ricevuto il certificato telematico relativo a [SALUTE_2] e di aver registrato l’assenza a partire da lunedì [DATA_1] fino al [DATA_2]. Abbiamo provveduto a informare il/la [RUOLO_2] affinché possa riorganizzare i turni del/la [STRUTTURA_1] in modo da garantire la continuità operativa del turno di notte nello stabilimento di [CITTA_1].\n\nPrendiamo atto del ciclo di [SALUTE_3] presso il poliambulatorio di [CITTA_2] e delle sue disponibilità per eventuali visite fiscali al domicilio negli orari previsti. Per qualsiasi ulteriore necessità o aggiornamento, la contatteremo al numero 081 512 3348 o all’indirizzo email davide.sorrentino@example.org.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per ogni eventuale esigenza.\n\nCordiali saluti,\n\n[Nome_Responsabile]  \n[RUOLO_RESPONSABILE] – Ufficio Risorse Umane  \n[AZIENDA_1]  \n[Telefono_Ufficio] – [Email_Ufficio]",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia\n\nGentile Davide Sorrentino,\n\nla ringrazio per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver ricevuto il certificato telematico relativo a ernia del disco lombare e di aver registrato l’assenza a partire da lunedì 16 novembre 2026 fino al 5 dicembre 2026. Abbiamo provveduto a informare il/la capoturno affinché possa riorganizzare i turni del/la reparto spedizioni in modo da garantire la continuità operativa del turno di notte nello stabilimento di Nola.\n\nPrendiamo atto del ciclo di fisioterapia presso il poliambulatorio di Pomigliano e delle sue disponibilità per eventuali visite fiscali al domicilio negli orari previsti. Per qualsiasi ulteriore necessità o aggiornamento, la contatteremo al numero 081 512 3348 o all’indirizzo email davide.sorrentino@example.org.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per ogni eventuale esigenza.\n\nCordiali saluti,\n\n[Nome_Responsabile]  \n[RUOLO_RESPONSABILE] – Ufficio Risorse Umane  \nINPS  \n[Telefono_Ufficio] – [Email_Ufficio]",
     "events": [
      {
       "surrogate": "[SALUTE_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[SALUTE_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[SALUTE_3]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "e22c1b81bcc5"
    },
    "D3+R2": {
     "spans": [
      {
       "start": 38,
       "end": 46,
       "text": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 104,
       "end": 116,
       "text": "magazziniere",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 158,
       "end": 162,
       "text": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 164,
       "end": 182,
       "text": "matricola NL-20417",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3"
      },
      {
       "start": 209,
       "end": 225,
       "text": "16 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 243,
       "end": 251,
       "text": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 294,
       "end": 317,
       "text": "ernia del disco lombare",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 352,
       "end": 367,
       "text": "5 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 421,
       "end": 425,
       "text": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 473,
       "end": 485,
       "text": "fisioterapia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 515,
       "end": 525,
       "text": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 603,
       "end": 612,
       "text": "capoturno",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 648,
       "end": 666,
       "text": "reparto spedizioni",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per [SALUTE_1]\n\nGentile Ufficio Risorse Umane,\n\nsono Davide Sorrentino, [RUOLO_1] del turno di notte nello stabilimento di Teramo, vnzhtrpvu AP-64069. Vi informo che da lunedì 28 novembre 2026 sarò assente per [SALUTE_1]: il medico di base mi ha diagnosticato un'[SALUTE_2] e mi ha prescritto riposo fino al 6 dicembre 2026. Il certificato telematico è già stato trasmesso all'Fabbrica Tessile Morandotti S.p.A..\n\nDurante la convalescenza seguirò un ciclo di [SALUTE_3] presso il poliambulatorio di Isernia, tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il [RUOLO_2], così da riorganizzare i turni del [STRUTTURA_1].\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al 081 512 3348 o scrivermi a davide.sorrentino@example.org.\n\nGrazie e cordiali saluti,\nDavide Sorrentino\n",
     "disclosure": [
      {
       "surrogate": "[SALUTE_1]",
       "value": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "condizione di salute che causa l'assenza"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "magazziniere",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere di chi scrive"
      },
      {
       "surrogate": "Teramo",
       "value": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località dello stabilimento"
      },
      {
       "surrogate": "vnzhtrpvu AP-64069",
       "value": "matricola NL-20417",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "28 novembre 2026",
       "value": "16 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di inizio assenza"
      },
      {
       "surrogate": "[SALUTE_2]",
       "value": "ernia del disco lombare",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "diagnosi specifica"
      },
      {
       "surrogate": "6 dicembre 2026",
       "value": "5 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di fine assenza"
      },
      {
       "surrogate": "Fabbrica Tessile Morandotti S.p.A.",
       "value": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "ente di previdenza a cui è stato trasmesso il certificato"
      },
      {
       "surrogate": "[SALUTE_3]",
       "value": "fisioterapia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "terapia prescritta"
      },
      {
       "surrogate": "Isernia",
       "value": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "value": "capoturno",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "ruolo di riferimento per la riorganizzazione dei turni"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "reparto spedizioni",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per [SALUTE_1]\n\nGentile Davide Sorrentino,\n\nla ringrazio per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza a partire da lunedì 28 novembre 2026 fino al 6 dicembre 2026 per [SALUTE_1]. Il certificato telematico è stato correttamente ricevuto e archiviato.\n\nAbbiamo provveduto a informare il/la [RUOLO_2] affinché possa riorganizzare i turni del/la [STRUTTURA_1] durante il periodo indicato. Inoltre, il suo ciclo di [SALUTE_3] presso il poliambulatorio di Isernia è stato annotato nel nostro calendario interno.\n\nPer eventuali necessità operative o richieste di informazioni, il nostro ufficio rimane a disposizione al numero 081 512 3348 o via e‑mail all’indirizzo risorseumane@azienda.it.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per qualsiasi ulteriore supporto.\n\nCordiali saluti,\n\n[Nome Cognome]  \n[RUOLO_3] – Ufficio Risorse Umane  \n[AZIENDA]  \nTelefono: 081 512 3348  \nE‑mail: risorseumane@azienda.it",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia\n\nGentile Davide Sorrentino,\n\nla ringrazio per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza a partire da lunedì 16 novembre 2026 fino al 5 dicembre 2026 per malattia. Il certificato telematico è stato correttamente ricevuto e archiviato.\n\nAbbiamo provveduto a informare il/la capoturno affinché possa riorganizzare i turni del/la reparto spedizioni durante il periodo indicato. Inoltre, il suo ciclo di fisioterapia presso il poliambulatorio di Pomigliano è stato annotato nel nostro calendario interno.\n\nPer eventuali necessità operative o richieste di informazioni, il nostro ufficio rimane a disposizione al numero 081 512 3348 o via e‑mail all’indirizzo risorseumane@azienda.it.\n\nLe auguriamo una pronta guarigione e restiamo a disposizione per qualsiasi ulteriore supporto.\n\nCordiali saluti,\n\n[Nome Cognome]  \n[RUOLO_3] – Ufficio Risorse Umane  \n[AZIENDA]  \nTelefono: 081 512 3348  \nE‑mail: risorseumane@azienda.it",
     "events": [
      {
       "surrogate": "[SALUTE_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Teramo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "vnzhtrpvu AP-64069",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "28 novembre 2026",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[SALUTE_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "6 dicembre 2026",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Fabbrica Tessile Morandotti S.p.A.",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[SALUTE_3]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Isernia",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_3]",
       "outcome": "hallucinated_token",
       "found_as": "[RUOLO_3]"
      }
     ],
     "fully_restored": false,
     "run_id": "78d5c21f1f74"
    },
    "D4+R1": {
     "spans": [
      {
       "start": 38,
       "end": 46,
       "text": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 85,
       "end": 102,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 104,
       "end": 116,
       "text": "magazziniere",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 158,
       "end": 162,
       "text": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 164,
       "end": 182,
       "text": "matricola NL-20417",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3"
      },
      {
       "start": 209,
       "end": 225,
       "text": "16 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 243,
       "end": 251,
       "text": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 294,
       "end": 317,
       "text": "ernia del disco lombare",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 352,
       "end": 367,
       "text": "5 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 421,
       "end": 425,
       "text": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 473,
       "end": 485,
       "text": "fisioterapia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 515,
       "end": 525,
       "text": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 603,
       "end": 612,
       "text": "capoturno",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 648,
       "end": 666,
       "text": "reparto spedizioni",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 791,
       "end": 803,
       "text": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 818,
       "end": 847,
       "text": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 876,
       "end": 893,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per [SALUTE_1]\n\nGentile Ufficio Risorse Umane,\n\nsono [PERSONA_1_M], [RUOLO_1] del turno di notte nello stabilimento di [CITTA_1], [UTENTE_1]. Vi informo che da lunedì [DATA_1] sarò assente per [SALUTE_1]: il medico di base mi ha diagnosticato un'[SALUTE_2] e mi ha prescritto riposo fino al [DATA_2]. Il certificato telematico è già stato trasmesso all'[AZIENDA_1].\n\nDurante la convalescenza seguirò un ciclo di [SALUTE_3] presso il poliambulatorio di [CITTA_2], tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il [RUOLO_2], così da riorganizzare i turni del [STRUTTURA_1].\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al [TELEFONO_1] o scrivermi a [EMAIL_1].\n\nGrazie e cordiali saluti,\n[PERSONA_1_M]\n",
     "disclosure": [
      {
       "surrogate": "[SALUTE_1]",
       "value": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "condizione di salute che causa l'assenza"
      },
      {
       "surrogate": "[PERSONA_1_M]",
       "value": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "magazziniere",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere di chi scrive"
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località dello stabilimento"
      },
      {
       "surrogate": "[UTENTE_1]",
       "value": "matricola NL-20417",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[DATA_1]",
       "value": "16 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di inizio assenza"
      },
      {
       "surrogate": "[SALUTE_2]",
       "value": "ernia del disco lombare",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "diagnosi specifica"
      },
      {
       "surrogate": "[DATA_2]",
       "value": "5 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di fine assenza"
      },
      {
       "surrogate": "[AZIENDA_1]",
       "value": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "ente di previdenza a cui è stato trasmesso il certificato"
      },
      {
       "surrogate": "[SALUTE_3]",
       "value": "fisioterapia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "terapia prescritta"
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "value": "capoturno",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "ruolo di riferimento per la riorganizzazione dei turni"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "reparto spedizioni",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per [SALUTE_1]\n\nGentile [PERSONA_1_M],\n\nla ringrazio per averci comunicato la sua situazione di salute.\n\nConfermiamo di aver ricevuto la sua segnalazione e il certificato telematico relativo a [SALUTE_2]. L’assenza è stata registrata a partire da lunedì [DATA_1] fino al [DATA_2] e il [RUOLO_2] è stato avvisato per la riorganizzazione dei turni del [STRUTTURA_1] durante il periodo indicato.\n\nNel frattempo, le auguriamo una pronta guarigione e un efficace percorso di cura presso il poliambulatorio di [CITTA_2]. Per qualsiasi necessità o aggiornamento, non esiti a contattarci al numero [TELEFONO_1] o via email all’indirizzo [EMAIL_1].\n\nRimaniamo a disposizione per eventuali ulteriori informazioni.\n\nCordiali saluti,\n\n[Nome del responsabile]  \n[RUOLO_2] – Ufficio Risorse Umane  \n[AZIENDA_1]  \n[TELEFONO_1]  \n[EMAIL_1]",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia\n\nGentile Davide Sorrentino,\n\nla ringrazio per averci comunicato la sua situazione di salute.\n\nConfermiamo di aver ricevuto la sua segnalazione e il certificato telematico relativo a ernia del disco lombare. L’assenza è stata registrata a partire da lunedì 16 novembre 2026 fino al 5 dicembre 2026 e il capoturno è stato avvisato per la riorganizzazione dei turni del reparto spedizioni durante il periodo indicato.\n\nNel frattempo, le auguriamo una pronta guarigione e un efficace percorso di cura presso il poliambulatorio di Pomigliano. Per qualsiasi necessità o aggiornamento, non esiti a contattarci al numero 081 512 3348 o via email all’indirizzo davide.sorrentino@example.org.\n\nRimaniamo a disposizione per eventuali ulteriori informazioni.\n\nCordiali saluti,\n\n[Nome del responsabile]  \ncapoturno – Ufficio Risorse Umane  \nINPS  \n081 512 3348  \ndavide.sorrentino@example.org",
     "events": [
      {
       "surrogate": "[SALUTE_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_1_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[SALUTE_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[SALUTE_3]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "933a73c866b3"
    },
    "D4+R2": {
     "spans": [
      {
       "start": 38,
       "end": 46,
       "text": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 85,
       "end": 102,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 104,
       "end": 116,
       "text": "magazziniere",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 158,
       "end": 162,
       "text": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 164,
       "end": 182,
       "text": "matricola NL-20417",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3"
      },
      {
       "start": 209,
       "end": 225,
       "text": "16 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 243,
       "end": 251,
       "text": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 294,
       "end": 317,
       "text": "ernia del disco lombare",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 352,
       "end": 367,
       "text": "5 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 421,
       "end": 425,
       "text": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 473,
       "end": 485,
       "text": "fisioterapia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3"
      },
      {
       "start": 515,
       "end": 525,
       "text": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 603,
       "end": 612,
       "text": "capoturno",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 648,
       "end": 666,
       "text": "reparto spedizioni",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 791,
       "end": 803,
       "text": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 818,
       "end": 847,
       "text": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 876,
       "end": 893,
       "text": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: comunicazione di assenza per [SALUTE_1]\n\nGentile Ufficio Risorse Umane,\n\nsono Corrado Ubaldini, [RUOLO_1] del turno di notte nello stabilimento di Teramo, vnzhtrpvu AP-64069. Vi informo che da lunedì 28 novembre 2026 sarò assente per [SALUTE_1]: il medico di base mi ha diagnosticato un'[SALUTE_2] e mi ha prescritto riposo fino al 6 dicembre 2026. Il certificato telematico è già stato trasmesso all'Fabbrica Tessile Morandotti S.p.A..\n\nDurante la convalescenza seguirò un ciclo di [SALUTE_3] presso il poliambulatorio di Isernia, tre mattine a settimana. Vi chiedo di registrare l'assenza e di avvisare il [RUOLO_2], così da riorganizzare i turni del [STRUTTURA_1].\n\nPer eventuali visite fiscali sono reperibile al mio domicilio negli orari previsti; per comunicazioni potete chiamarmi al 024 489 9877 o scrivermi a selene.brunelleschi@example.com.\n\nGrazie e cordiali saluti,\nCorrado Ubaldini\n",
     "disclosure": [
      {
       "surrogate": "[SALUTE_1]",
       "value": "malattia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "condizione di salute che causa l'assenza"
      },
      {
       "surrogate": "Corrado Ubaldini",
       "value": "Davide Sorrentino",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "magazziniere",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere di chi scrive"
      },
      {
       "surrogate": "Teramo",
       "value": "Nola",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "località dello stabilimento"
      },
      {
       "surrogate": "vnzhtrpvu AP-64069",
       "value": "matricola NL-20417",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "28 novembre 2026",
       "value": "16 novembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di inizio assenza"
      },
      {
       "surrogate": "[SALUTE_2]",
       "value": "ernia del disco lombare",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "diagnosi specifica"
      },
      {
       "surrogate": "6 dicembre 2026",
       "value": "5 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di fine assenza"
      },
      {
       "surrogate": "Fabbrica Tessile Morandotti S.p.A.",
       "value": "INPS",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "ente di previdenza a cui è stato trasmesso il certificato"
      },
      {
       "surrogate": "[SALUTE_3]",
       "value": "fisioterapia",
       "type": "SALUTE",
       "cls": "special",
       "source": "D3",
       "reason": "terapia prescritta"
      },
      {
       "surrogate": "Isernia",
       "value": "Pomigliano",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "value": "capoturno",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "ruolo di riferimento per la riorganizzazione dei turni"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "reparto spedizioni",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": ""
      },
      {
       "surrogate": "024 489 9877",
       "value": "081 512 3348",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "selene.brunelleschi@example.com",
       "value": "davide.sorrentino@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: comunicazione di assenza per [SALUTE_1]\n\nGentile Corrado Ubaldini,\n\nla ringrazio per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza a partire da lunedì 28 novembre 2026 fino al 6 dicembre 2026 per [SALUTE_1]. Il certificato telematico è stato correttamente ricevuto e archiviato.\n\nAbbiamo provveduto a informare il/la [RUOLO_2] affinché possa riorganizzare i turni del/la [STRUTTURA_1] durante il periodo indicato. Inoltre, il suo ciclo di [SALUTE_3] presso il poliambulatorio di Isernia è stato annotato nel nostro calendario interno.\n\nPer eventuali necessità operative o richieste di chiarimento, il nostro ufficio rimane a disposizione. La contatteremo, se necessario, al numero di telefono fornito (024 489 9877) o all’indirizzo email selene.brunelleschi@example.com.\n\nLe auguriamo una pronta guarigione e un completo recupero.\n\nCordiali saluti,\n\n[Nome Cognome]  \n[RUOLO_3] – Ufficio Risorse Umane  \nFabbrica Tessile Morandotti S.p.A.  \nTelefono: [NUMERO_TELEFONO_Ufficio]  \nEmail: [EMAIL_Ufficio]",
     "restored": "**Oggetto:** Re: comunicazione di assenza per malattia\n\nGentile Davide Sorrentino,\n\nla ringrazio per averci comunicato la sua assenza per motivi di salute.\n\nConfermiamo di aver registrato la sua assenza a partire da lunedì 16 novembre 2026 fino al 5 dicembre 2026 per malattia. Il certificato telematico è stato correttamente ricevuto e archiviato.\n\nAbbiamo provveduto a informare il/la capoturno affinché possa riorganizzare i turni del/la reparto spedizioni durante il periodo indicato. Inoltre, il suo ciclo di fisioterapia presso il poliambulatorio di Pomigliano è stato annotato nel nostro calendario interno.\n\nPer eventuali necessità operative o richieste di chiarimento, il nostro ufficio rimane a disposizione. La contatteremo, se necessario, al numero di telefono fornito (081 512 3348) o all’indirizzo email davide.sorrentino@example.org.\n\nLe auguriamo una pronta guarigione e un completo recupero.\n\nCordiali saluti,\n\n[Nome Cognome]  \n[RUOLO_3] – Ufficio Risorse Umane  \nINPS  \nTelefono: [NUMERO_TELEFONO_Ufficio]  \nEmail: [EMAIL_Ufficio]",
     "events": [
      {
       "surrogate": "[SALUTE_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Corrado Ubaldini",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Teramo",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "vnzhtrpvu AP-64069",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "28 novembre 2026",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[SALUTE_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "6 dicembre 2026",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Fabbrica Tessile Morandotti S.p.A.",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[SALUTE_3]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Isernia",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "024 489 9877",
       "outcome": "restored",
       "found_as": "024 489 9877"
      },
      {
       "surrogate": "selene.brunelleschi@example.com",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_3]",
       "outcome": "hallucinated_token",
       "found_as": "[RUOLO_3]"
      }
     ],
     "fully_restored": false,
     "run_id": "65b4d39c07a9"
    }
   },
   "calc_blocked": {
    "D0": {},
    "D1": {},
    "D2": {},
    "D3": {
     "DATA": 2
    },
    "D4": {
     "DATA": 2
    }
   }
  },
  {
   "id": "fx-hr-02",
   "domain": "hr",
   "scenario": "transfer_request",
   "text": "Oggetto: richiesta di trasferimento alla sede di Bologna\n\nGentile dott.ssa Paola Ricciardelli,\n\nsono Alessio Mondini, analista contabile dell'ufficio amministrazione di Meridiana Servizi S.p.A. nella sede di Rimini, dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di Bologna a partire dal 1 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'Ospedale Maggiore di Bologna e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 15 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al 333 908 1176 o all'indirizzo alessio.mondini@example.org.\n\nCordiali saluti,\nAlessio Mondini\n",
   "runs": {
    "D0+R1": {
     "spans": [
      {
       "start": 768,
       "end": 780,
       "text": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 797,
       "end": 824,
       "text": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di Bologna\n\nGentile dott.ssa Paola Ricciardelli,\n\nsono Alessio Mondini, analista contabile dell'ufficio amministrazione di Meridiana Servizi S.p.A. nella sede di Rimini, dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di Bologna a partire dal 1 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'Ospedale Maggiore di Bologna e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 15 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al [TELEFONO_1] o all'indirizzo [EMAIL_1].\n\nCordiali saluti,\nAlessio Mondini\n",
     "disclosure": [
      {
       "surrogate": "[TELEFONO_1]",
       "value": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile Sig. Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso con noi le motivazioni personali alla base della sua richiesta di trasferimento alla sede di Bologna.\n\nHo preso atto della sua disponibilità a mantenere le attuali mansioni di analista contabile, nonché della sua apertura a valutare un eventuale ruolo di addetto alla contabilità fornitori. La sua esperienza quinquennale presso la sede di Rimini è sicuramente un valore aggiunto per il nostro team bolognese.\n\nPer poter procedere con una valutazione completa, le chiedo gentilmente di inviarci, entro il 30 dicembre 2026, i seguenti documenti:\n\n1. Copia del contratto di lavoro attuale.  \n2. Eventuale documentazione relativa al nuovo incarico della sua consorte (es. lettera di conferma dell’Ospedale Maggiore di Bologna).  \n3. Una breve dichiarazione motivazionale (max 300 parole) in cui espone le sue aspettative professionali per il ruolo a Bologna.\n\nUna volta ricevuta la documentazione, provvederò a inoltrare la sua richiesta al dipartimento Risorse Umane e al responsabile della sede di Bologna. Prevediamo di poterle fornire una risposta definitiva entro il 15 gennaio 2027, in modo da consentirle di organizzare il trasferimento con il tempo necessario.\n\nResto a disposizione per eventuali chiarimenti e per concordare un colloquio telefonico al [TELEFONO_1] o via email all’indirizzo [EMAIL_1].\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p.A.  \nSede di Rimini  \n[TELEFONO_2] – [EMAIL_2]",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile Sig. Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso con noi le motivazioni personali alla base della sua richiesta di trasferimento alla sede di Bologna.\n\nHo preso atto della sua disponibilità a mantenere le attuali mansioni di analista contabile, nonché della sua apertura a valutare un eventuale ruolo di addetto alla contabilità fornitori. La sua esperienza quinquennale presso la sede di Rimini è sicuramente un valore aggiunto per il nostro team bolognese.\n\nPer poter procedere con una valutazione completa, le chiedo gentilmente di inviarci, entro il 30 dicembre 2026, i seguenti documenti:\n\n1. Copia del contratto di lavoro attuale.  \n2. Eventuale documentazione relativa al nuovo incarico della sua consorte (es. lettera di conferma dell’Ospedale Maggiore di Bologna).  \n3. Una breve dichiarazione motivazionale (max 300 parole) in cui espone le sue aspettative professionali per il ruolo a Bologna.\n\nUna volta ricevuta la documentazione, provvederò a inoltrare la sua richiesta al dipartimento Risorse Umane e al responsabile della sede di Bologna. Prevediamo di poterle fornire una risposta definitiva entro il 15 gennaio 2027, in modo da consentirle di organizzare il trasferimento con il tempo necessario.\n\nResto a disposizione per eventuali chiarimenti e per concordare un colloquio telefonico al 333 908 1176 o via email all’indirizzo alessio.mondini@example.org.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p.A.  \nSede di Rimini  \n[TELEFONO_2] – [EMAIL_2]",
     "events": [
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_2]",
       "outcome": "hallucinated_token",
       "found_as": "[TELEFONO_2]"
      },
      {
       "surrogate": "[EMAIL_2]",
       "outcome": "hallucinated_token",
       "found_as": "[EMAIL_2]"
      }
     ],
     "fully_restored": false,
     "run_id": "a3c06360ce07"
    },
    "D0+R2": {
     "spans": [
      {
       "start": 768,
       "end": 780,
       "text": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 797,
       "end": 824,
       "text": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di Bologna\n\nGentile dott.ssa Paola Ricciardelli,\n\nsono Alessio Mondini, analista contabile dell'ufficio amministrazione di Meridiana Servizi S.p.A. nella sede di Rimini, dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di Bologna a partire dal 1 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'Ospedale Maggiore di Bologna e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 15 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al 339 778 6313 o all'indirizzo clelia.querzoli@example.com.\n\nCordiali saluti,\nAlessio Mondini\n",
     "disclosure": [
      {
       "surrogate": "339 778 6313",
       "value": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "clelia.querzoli@example.com",
       "value": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile dott. Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso con noi le motivazioni personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua volontà di trasferirsi alla sede di Bologna a partire dal 1 marzo 2027, nonché della sua disponibilità a mantenere le attuali mansioni o, in alternativa, a ricoprire il ruolo di addetto alla contabilità fornitori.  \n\nPer poter valutare la sua richiesta nel rispetto delle procedure interne, le chiedo cortesemente di inviarci, entro il 10 gennaio 2027, i seguenti documenti:\n\n1. Copia del contratto di lavoro della sua consorte presso l’Ospedale Maggiore di Bologna (per confermare la necessità del trasferimento familiare).  \n2. Eventuale certificato di residenza o documentazione attestante il trasferimento di domicilio.  \n3. Aggiornamento del suo curriculum vitae, qualora desiderasse considerare il ruolo di addetto alla contabilità fornitori.\n\nUna volta ricevuta la documentazione, provvederò a inoltrare la sua pratica al dipartimento Risorse Umane e al responsabile della sede di Bologna per una valutazione congiunta. Mi impegno a fornirle un riscontro definitivo entro il 15 febbraio 2027, in modo da consentirle di organizzare il trasloco con il tempo necessario.\n\nNel frattempo, resto a disposizione per eventuali chiarimenti o per concordare un colloquio telefonico/virtuale, qualora lo ritenesse opportuno. Può contattarmi direttamente al [NUMERO_TELEFONO] o via email all’indirizzo [EMAIL_RISORSE_UMANE].\n\nLa ringrazio per la sua disponibilità e per l’impegno dimostrato negli ultimi cinque anni presso la sede di Rimini. Confido che, qualora la procedura lo consenta, potremo accogliere la sua richiesta e supportarla nel nuovo percorso professionale a Bologna.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p.A. – Sede di Rimini  \n[Telefono] – [Email]  ",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile dott. Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso con noi le motivazioni personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua volontà di trasferirsi alla sede di Bologna a partire dal 1 marzo 2027, nonché della sua disponibilità a mantenere le attuali mansioni o, in alternativa, a ricoprire il ruolo di addetto alla contabilità fornitori.  \n\nPer poter valutare la sua richiesta nel rispetto delle procedure interne, le chiedo cortesemente di inviarci, entro il 10 gennaio 2027, i seguenti documenti:\n\n1. Copia del contratto di lavoro della sua consorte presso l’Ospedale Maggiore di Bologna (per confermare la necessità del trasferimento familiare).  \n2. Eventuale certificato di residenza o documentazione attestante il trasferimento di domicilio.  \n3. Aggiornamento del suo curriculum vitae, qualora desiderasse considerare il ruolo di addetto alla contabilità fornitori.\n\nUna volta ricevuta la documentazione, provvederò a inoltrare la sua pratica al dipartimento Risorse Umane e al responsabile della sede di Bologna per una valutazione congiunta. Mi impegno a fornirle un riscontro definitivo entro il 15 febbraio 2027, in modo da consentirle di organizzare il trasloco con il tempo necessario.\n\nNel frattempo, resto a disposizione per eventuali chiarimenti o per concordare un colloquio telefonico/virtuale, qualora lo ritenesse opportuno. Può contattarmi direttamente al [NUMERO_TELEFONO] o via email all’indirizzo [EMAIL_RISORSE_UMANE].\n\nLa ringrazio per la sua disponibilità e per l’impegno dimostrato negli ultimi cinque anni presso la sede di Rimini. Confido che, qualora la procedura lo consenta, potremo accogliere la sua richiesta e supportarla nel nuovo percorso professionale a Bologna.\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p.A. – Sede di Rimini  \n[Telefono] – [Email]  ",
     "events": [
      {
       "surrogate": "339 778 6313",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "clelia.querzoli@example.com",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "1f4b787b41ab"
    },
    "D1+R1": {
     "spans": [
      {
       "start": 49,
       "end": 56,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 75,
       "end": 93,
       "text": "Paola Ricciardelli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 101,
       "end": 116,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 169,
       "end": 190,
       "text": "Meridiana Servizi S.p",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 208,
       "end": 214,
       "text": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 297,
       "end": 304,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 400,
       "end": 417,
       "text": "Ospedale Maggiore",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 421,
       "end": 428,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 768,
       "end": 780,
       "text": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 797,
       "end": 824,
       "text": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 844,
       "end": 859,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di [CITTA_1]\n\nGentile dott.ssa [PERSONA_1_F],\n\nsono [PERSONA_2_M], analista contabile dell'ufficio amministrazione di [AZIENDA_1].A. nella sede di [CITTA_2], dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di [CITTA_1] a partire dal 1 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'[CITTA_3] di [CITTA_1] e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 15 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al [TELEFONO_1] o all'indirizzo [EMAIL_1].\n\nCordiali saluti,\n[PERSONA_2_M]\n",
     "disclosure": [
      {
       "surrogate": "[CITTA_1]",
       "value": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_1_F]",
       "value": "Paola Ricciardelli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_2_M]",
       "value": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "value": "Meridiana Servizi S.p",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_3]",
       "value": "Ospedale Maggiore",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di [CITTA_1]\n\nGentile dott. [PERSONA_2_M],\n\nla ringrazio per la sua comunicazione e per averci illustrato le motivazioni del suo desiderio di trasferimento alla sede di [CITTA_1].\n\nConfermo di aver ricevuto la sua richiesta, che sarà valutata dal nostro ufficio Risorse Umane in collaborazione con la direzione della sede di [CITTA_1]. Per poter procedere con l’analisi, avremmo bisogno dei seguenti documenti:\n\n1. Copia del contratto di lavoro attuale;\n2. Copia del contratto o della lettera di conferma dell’incarico della sua moglie presso l’[CITTA_3] di [CITTA_1];\n3. Eventuale certificato di residenza o documento che attesti il trasferimento familiare;\n4. Eventuali preferenze o disponibilità per il ruolo di addetto alla contabilità fornitori, qualora fosse necessario un adeguamento delle mansioni.\n\nLe chiedo gentilmente di inviare il materiale richiesto entro il **10 dicembre 2026**, così da consentirci di fornirle una risposta definitiva entro il **15 dicembre 2026**, come da sua richiesta.\n\nNel frattempo, resto a disposizione per un colloquio telefonico o via videoconferenza, qualora volesse approfondire alcuni aspetti della sua proposta. Può contattarmi al [TELEFONO_1] o all’indirizzo [EMAIL_1] per concordare data e orario.\n\nRingraziandola per la disponibilità e per l’interesse a continuare a collaborare con [AZIENDA_1], le porgo cordiali saluti.\n\nDistinti saluti,\n\n[PERSONA_1_F]  \nResponsabile Risorse Umane  \n[AZIENDA_1]  \n[TELEFONO_1]  \n[EMAIL_1]",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna\n\nGentile dott. Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per averci illustrato le motivazioni del suo desiderio di trasferimento alla sede di Bologna.\n\nConfermo di aver ricevuto la sua richiesta, che sarà valutata dal nostro ufficio Risorse Umane in collaborazione con la direzione della sede di Bologna. Per poter procedere con l’analisi, avremmo bisogno dei seguenti documenti:\n\n1. Copia del contratto di lavoro attuale;\n2. Copia del contratto o della lettera di conferma dell’incarico della sua moglie presso l’Ospedale Maggiore di Bologna;\n3. Eventuale certificato di residenza o documento che attesti il trasferimento familiare;\n4. Eventuali preferenze o disponibilità per il ruolo di addetto alla contabilità fornitori, qualora fosse necessario un adeguamento delle mansioni.\n\nLe chiedo gentilmente di inviare il materiale richiesto entro il **10 dicembre 2026**, così da consentirci di fornirle una risposta definitiva entro il **15 dicembre 2026**, come da sua richiesta.\n\nNel frattempo, resto a disposizione per un colloquio telefonico o via videoconferenza, qualora volesse approfondire alcuni aspetti della sua proposta. Può contattarmi al 333 908 1176 o all’indirizzo alessio.mondini@example.org per concordare data e orario.\n\nRingraziandola per la disponibilità e per l’interesse a continuare a collaborare con Meridiana Servizi S.p, le porgo cordiali saluti.\n\nDistinti saluti,\n\nPaola Ricciardelli  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p  \n333 908 1176  \nalessio.mondini@example.org",
     "events": [
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_1_F]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_2_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_3]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "49f599e17121"
    },
    "D1+R2": {
     "spans": [
      {
       "start": 49,
       "end": 56,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 75,
       "end": 93,
       "text": "Paola Ricciardelli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 101,
       "end": 116,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 169,
       "end": 190,
       "text": "Meridiana Servizi S.p",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 208,
       "end": 214,
       "text": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 297,
       "end": 304,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 400,
       "end": 417,
       "text": "Ospedale Maggiore",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 421,
       "end": 428,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1"
      },
      {
       "start": 768,
       "end": 780,
       "text": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 797,
       "end": 824,
       "text": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 844,
       "end": 859,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di Vercelli\n\nGentile dott.ssa Olimpia Pagliarini,\n\nsono Gualtiero Salvadori, analista contabile dell'ufficio amministrazione di Gruppo Lucarelli Servizi S.r.l..A. nella sede di Rieti, dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di Vercelli a partire dal 1 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'Pordenone di Vercelli e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 15 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al 339 778 6313 o all'indirizzo clelia.querzoli@example.com.\n\nCordiali saluti,\nGualtiero Salvadori\n",
     "disclosure": [
      {
       "surrogate": "Vercelli",
       "value": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Olimpia Pagliarini",
       "value": "Paola Ricciardelli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Gualtiero Salvadori",
       "value": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Gruppo Lucarelli Servizi S.r.l.",
       "value": "Meridiana Servizi S.p",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Rieti",
       "value": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Pordenone",
       "value": "Ospedale Maggiore",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "339 778 6313",
       "value": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "clelia.querzoli@example.com",
       "value": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di Vercelli  \n\nGentile dott. Salvadori,\n\nla ringrazio per la sua comunicazione e per aver condiviso con noi le motivazioni del suo desiderio di trasferimento.\n\nHo preso atto della sua richiesta di passare alla sede di Vercelli a partire dal 1 marzo 2027, nonché della sua disponibilità a mantenere le attuali mansioni o, in alternativa, a ricoprire il ruolo di addetto alla contabilità fornitori. \n\nProcederò a inoltrare la sua domanda al responsabile delle risorse umane della sede di Vercelli e al Direttore Amministrativo, affinché possano valutare la fattibilità operativa e le eventuali esigenze di copertura del suo attuale ruolo a Rieti. \n\nLe confermo che riceverà una risposta definitiva entro il 15 dicembre 2026, come richiesto. Nel frattempo, qualora fossero necessari ulteriori chiarimenti o un colloquio, sarò lieta di contattarla al numero 339 778 6313 o via email all’indirizzo clelia.querzoli@example.com.\n\nResto a disposizione per qualsiasi ulteriore informazione e le porgo i miei più cordiali saluti.\n\nCordiali saluti,  \n\n[Nome Cognome]  \nResponsabile Risorse Umane  \nGruppo Lucarelli Servizi S.r.l.  \n[Telefono] – [Email]  ",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile dott. Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso con noi le motivazioni del suo desiderio di trasferimento.\n\nHo preso atto della sua richiesta di passare alla sede di Bologna a partire dal 1 marzo 2027, nonché della sua disponibilità a mantenere le attuali mansioni o, in alternativa, a ricoprire il ruolo di addetto alla contabilità fornitori. \n\nProcederò a inoltrare la sua domanda al responsabile delle risorse umane della sede di Bologna e al Direttore Amministrativo, affinché possano valutare la fattibilità operativa e le eventuali esigenze di copertura del suo attuale ruolo a Rimini. \n\nLe confermo che riceverà una risposta definitiva entro il 15 dicembre 2026, come richiesto. Nel frattempo, qualora fossero necessari ulteriori chiarimenti o un colloquio, sarò lieta di contattarla al numero 333 908 1176 o via email all’indirizzo alessio.mondini@example.org.\n\nResto a disposizione per qualsiasi ulteriore informazione e le porgo i miei più cordiali saluti.\n\nCordiali saluti,  \n\n[Nome Cognome]  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p  \n[Telefono] – [Email]  ",
     "events": [
      {
       "surrogate": "Vercelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Olimpia Pagliarini",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Gualtiero Salvadori",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Gruppo Lucarelli Servizi S.r.l.",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Rieti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Pordenone",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "339 778 6313",
       "outcome": "restored",
       "found_as": "339 778 6313"
      },
      {
       "surrogate": "clelia.querzoli@example.com",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "1b498f032ac2"
    },
    "D2+R1": {
     "spans": [
      {
       "start": 101,
       "end": 116,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 208,
       "end": 214,
       "text": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 421,
       "end": 428,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 805,
       "end": 812,
       "text": "mondini",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 844,
       "end": 859,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di Bologna\n\nGentile dott.ssa Paola Ricciardelli,\n\nsono [PERSONA_1_M], analista contabile dell'ufficio amministrazione di Meridiana Servizi S.p.A. nella sede di [CITTA_1], dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di Bologna a partire dal 1 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'Ospedale Maggiore di [CITTA_2] e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 15 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al 333 908 1176 o all'indirizzo alessio.[UTENTE_1]@example.org.\n\nCordiali saluti,\n[PERSONA_1_M]\n",
     "disclosure": [
      {
       "surrogate": "[PERSONA_1_M]",
       "value": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "value": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "value": "mondini",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile [PERSONA_1_M],\n\nla ringrazio per la sua comunicazione e per aver condiviso le motivazioni personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua volontà di trasferirsi alla sede di Bologna a partire dal 1 marzo 2027, nonché della sua disponibilità a mantenere le attuali mansioni o, in alternativa, a ricoprire il ruolo di addetto alla contabilità fornitori. \n\nProvvederò a inoltrare la sua richiesta al dipartimento Risorse Umane e al responsabile della sede di Bologna per valutare la fattibilità operativa e le eventuali opportunità disponibili. \n\nLe confermo che riceverà una risposta definitiva entro il 15 dicembre 2026, così da consentirle di organizzare il trasloco in modo adeguato.\n\nNel frattempo, qualora avesse ulteriori informazioni da fornire o volesse fissare un colloquio, può contattarmi direttamente al [NUMERO_TELEFONO] o via email all’indirizzo [UTENTE_1]@example.org.\n\nResto a disposizione per qualsiasi chiarimento.\n\nCordiali saluti,\n\n[Nome Cognome]  \n[Posizione]  \nMeridiana Servizi S.p.A.  \n[Indirizzo sede]  \n[Telefono aziendale]  \n[Email aziendale]",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso le motivazioni personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua volontà di trasferirsi alla sede di Bologna a partire dal 1 marzo 2027, nonché della sua disponibilità a mantenere le attuali mansioni o, in alternativa, a ricoprire il ruolo di addetto alla contabilità fornitori. \n\nProvvederò a inoltrare la sua richiesta al dipartimento Risorse Umane e al responsabile della sede di Bologna per valutare la fattibilità operativa e le eventuali opportunità disponibili. \n\nLe confermo che riceverà una risposta definitiva entro il 15 dicembre 2026, così da consentirle di organizzare il trasloco in modo adeguato.\n\nNel frattempo, qualora avesse ulteriori informazioni da fornire o volesse fissare un colloquio, può contattarmi direttamente al [NUMERO_TELEFONO] o via email all’indirizzo mondini@example.org.\n\nResto a disposizione per qualsiasi chiarimento.\n\nCordiali saluti,\n\n[Nome Cognome]  \n[Posizione]  \nMeridiana Servizi S.p.A.  \n[Indirizzo sede]  \n[Telefono aziendale]  \n[Email aziendale]",
     "events": [
      {
       "surrogate": "[PERSONA_1_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[UTENTE_1]",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "bd5400e9b707"
    },
    "D2+R2": {
     "spans": [
      {
       "start": 101,
       "end": 116,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 208,
       "end": 214,
       "text": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 421,
       "end": 428,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2"
      },
      {
       "start": 805,
       "end": 812,
       "text": "mondini",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 844,
       "end": 859,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di Bologna\n\nGentile dott.ssa Paola Ricciardelli,\n\nsono Gualtiero Salvadori, analista contabile dell'ufficio amministrazione di Meridiana Servizi S.p.A. nella sede di Rieti, dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di Bologna a partire dal 1 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'Ospedale Maggiore di Vercelli e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 15 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al 333 908 1176 o all'indirizzo alessio.cloilfi@example.org.\n\nCordiali saluti,\nGualtiero Salvadori\n",
     "disclosure": [
      {
       "surrogate": "Gualtiero Salvadori",
       "value": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Rieti",
       "value": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "Vercelli",
       "value": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "cloilfi",
       "value": "mondini",
       "type": "UTENTE",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile dott. Salvadori,\n\nla ringrazio per la sua comunicazione e per aver condiviso con noi le motivazioni personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua volontà di trasferirsi alla sede di Bologna a partire dal 1 marzo 2027, nonché della sua disponibilità a mantenere le attuali mansioni o, in alternativa, a ricoprire il ruolo di addetto alla contabilità fornitori.\n\nProcederò a inoltrare la sua richiesta al Responsabile delle Risorse Umane e al Direttore della sede di Bologna affinché possano valutare la fattibilità operativa e le eventuali opportunità disponibili. Le farò avere un riscontro entro il 15 dicembre 2026, come da sua indicazione, così da consentirle di organizzare il trasloco con il tempo necessario.\n\nNel frattempo, le chiedo gentilmente di inviare al nostro ufficio HR i seguenti documenti, utili per completare la pratica di trasferimento:\n\n1. Copia del contratto di lavoro attuale.  \n2. Eventuale certificato di trasferimento familiare (se disponibile).  \n3. Eventuali preferenze o disponibilità per il nuovo ruolo (se desidera specificare ulteriori dettagli).  \n\nPuò inviare il materiale all’indirizzo [HR_EMAIL] oppure consegnarlo direttamente presso la nostra sede di Rieti.\n\nResto a disposizione per qualsiasi chiarimento e per concordare, se necessario, un colloquio telefonico o in videoconferenza. Può contattarmi al [NUMERO_TELEFONO] o via e‑mail all’indirizzo [EMAIL_RISORSE_UMANE].\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p.A. – Sede di Rieti  \n[NUMERO_TELEFONO] – [EMAIL_RISORSE_UMANE]  ",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile dott. Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso con noi le motivazioni personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua volontà di trasferirsi alla sede di Bologna a partire dal 1 marzo 2027, nonché della sua disponibilità a mantenere le attuali mansioni o, in alternativa, a ricoprire il ruolo di addetto alla contabilità fornitori.\n\nProcederò a inoltrare la sua richiesta al Responsabile delle Risorse Umane e al Direttore della sede di Bologna affinché possano valutare la fattibilità operativa e le eventuali opportunità disponibili. Le farò avere un riscontro entro il 15 dicembre 2026, come da sua indicazione, così da consentirle di organizzare il trasloco con il tempo necessario.\n\nNel frattempo, le chiedo gentilmente di inviare al nostro ufficio HR i seguenti documenti, utili per completare la pratica di trasferimento:\n\n1. Copia del contratto di lavoro attuale.  \n2. Eventuale certificato di trasferimento familiare (se disponibile).  \n3. Eventuali preferenze o disponibilità per il nuovo ruolo (se desidera specificare ulteriori dettagli).  \n\nPuò inviare il materiale all’indirizzo [HR_EMAIL] oppure consegnarlo direttamente presso la nostra sede di Rimini.\n\nResto a disposizione per qualsiasi chiarimento e per concordare, se necessario, un colloquio telefonico o in videoconferenza. Può contattarmi al [NUMERO_TELEFONO] o via e‑mail all’indirizzo [EMAIL_RISORSE_UMANE].\n\nCordiali saluti,\n\n[Nome Cognome]  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p.A. – Sede di Rimini  \n[NUMERO_TELEFONO] – [EMAIL_RISORSE_UMANE]  ",
     "events": [
      {
       "surrogate": "Gualtiero Salvadori",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Rieti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Vercelli",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "cloilfi",
       "outcome": "dropped",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "ec47ad42dada"
    },
    "D3+R1": {
     "spans": [
      {
       "start": 49,
       "end": 56,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 118,
       "end": 136,
       "text": "analista contabile",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 169,
       "end": 193,
       "text": "Meridiana Servizi S.p.A.",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 208,
       "end": 214,
       "text": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 297,
       "end": 304,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 319,
       "end": 331,
       "text": "1 marzo 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 400,
       "end": 428,
       "text": "Ospedale Maggiore di Bologna",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 666,
       "end": 682,
       "text": "15 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di [CITTA_1]\n\nGentile dott.ssa Paola Ricciardelli,\n\nsono Alessio Mondini, [RUOLO_1] dell'ufficio amministrazione di [AZIENDA_1] nella sede di [CITTA_2], dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di [CITTA_1] a partire dal [DATA_1].\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'[STRUTTURA_1] e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il [DATA_2], così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al 333 908 1176 o all'indirizzo alessio.mondini@example.org.\n\nCordiali saluti,\nAlessio Mondini\n",
     "disclosure": [
      {
       "surrogate": "[CITTA_1]",
       "value": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città di destinazione del trasferimento"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "analista contabile",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere dell'autore"
      },
      {
       "surrogate": "[AZIENDA_1]",
       "value": "Meridiana Servizi S.p.A.",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda dove lavora l'autore"
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città della sede attuale"
      },
      {
       "surrogate": "[DATA_1]",
       "value": "1 marzo 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di inizio del trasferimento richiesta"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "Ospedale Maggiore di Bologna",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "struttura dove ha ottenuto l'incarico la moglie"
      },
      {
       "surrogate": "[DATA_2]",
       "value": "15 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "scadenza per la risposta richiesta"
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di [CITTA_1]\n\nGentile dott. Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso i motivi personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua disponibilità a mantenere le attuali mansioni e l’orario di lavoro, nonché della sua apertura verso il ruolo di addetto alla contabilità fornitori. Provvederò a inoltrare la sua richiesta al responsabile delle risorse umane della sede di [CITTA_1] e a valutare le opportunità disponibili in linea con le esigenze operative dei nostri uffici.\n\nLe confermo che riceveremo una risposta definitiva entro il [DATA_2], così da consentirle di organizzare il trasloco in modo adeguato. Nel frattempo, qualora fossero necessari ulteriori chiarimenti o documentazione, la contatterò direttamente al numero 333 908 1176 o via email all’indirizzo alessio.mondini@example.org.\n\nResto a disposizione per eventuali ulteriori informazioni e per concordare, se necessario, un colloquio conoscitivo.\n\nCordiali saluti,\n\n[PERSONA_1_M]  \n[RUOLO_2] – Risorse Umane  \n[AZIENDA_1] – Sede di [CITTA_1]  \n[EMAIL_1] – [TELEFONO_1]",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna\n\nGentile dott. Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso i motivi personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua disponibilità a mantenere le attuali mansioni e l’orario di lavoro, nonché della sua apertura verso il ruolo di addetto alla contabilità fornitori. Provvederò a inoltrare la sua richiesta al responsabile delle risorse umane della sede di Bologna e a valutare le opportunità disponibili in linea con le esigenze operative dei nostri uffici.\n\nLe confermo che riceveremo una risposta definitiva entro il 15 dicembre 2026, così da consentirle di organizzare il trasloco in modo adeguato. Nel frattempo, qualora fossero necessari ulteriori chiarimenti o documentazione, la contatterò direttamente al numero 333 908 1176 o via email all’indirizzo alessio.mondini@example.org.\n\nResto a disposizione per eventuali ulteriori informazioni e per concordare, se necessario, un colloquio conoscitivo.\n\nCordiali saluti,\n\n[PERSONA_1_M]  \n[RUOLO_2] – Risorse Umane  \nMeridiana Servizi S.p.A. – Sede di Bologna  \n[EMAIL_1] – [TELEFONO_1]",
     "events": [
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_1_M]",
       "outcome": "hallucinated_token",
       "found_as": "[PERSONA_1_M]"
      },
      {
       "surrogate": "[RUOLO_2]",
       "outcome": "hallucinated_token",
       "found_as": "[RUOLO_2]"
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "hallucinated_token",
       "found_as": "[EMAIL_1]"
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "hallucinated_token",
       "found_as": "[TELEFONO_1]"
      }
     ],
     "fully_restored": false,
     "run_id": "e22c1b81bcc5"
    },
    "D3+R2": {
     "spans": [
      {
       "start": 49,
       "end": 56,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 118,
       "end": 136,
       "text": "analista contabile",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 169,
       "end": 193,
       "text": "Meridiana Servizi S.p.A.",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 208,
       "end": 214,
       "text": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 297,
       "end": 304,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 319,
       "end": 331,
       "text": "1 marzo 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 400,
       "end": 428,
       "text": "Ospedale Maggiore di Bologna",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 666,
       "end": 682,
       "text": "15 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di Vercelli\n\nGentile dott.ssa Paola Ricciardelli,\n\nsono Alessio Mondini, [RUOLO_1] dell'ufficio amministrazione di Consorzio Agrario Terrenove nella sede di Rieti, dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di Vercelli a partire dal 27 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'[STRUTTURA_1] e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 27 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al 333 908 1176 o all'indirizzo alessio.mondini@example.org.\n\nCordiali saluti,\nAlessio Mondini\n",
     "disclosure": [
      {
       "surrogate": "Vercelli",
       "value": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città di destinazione del trasferimento"
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "analista contabile",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere dell'autore"
      },
      {
       "surrogate": "Consorzio Agrario Terrenove",
       "value": "Meridiana Servizi S.p.A.",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda dove lavora l'autore"
      },
      {
       "surrogate": "Rieti",
       "value": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città della sede attuale"
      },
      {
       "surrogate": "27 marzo 2027",
       "value": "1 marzo 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di inizio del trasferimento richiesta"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "Ospedale Maggiore di Bologna",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "struttura dove ha ottenuto l'incarico la moglie"
      },
      {
       "surrogate": "27 dicembre 2026",
       "value": "15 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "scadenza per la risposta richiesta"
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di Vercelli  \n\nGentile dott. Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso i motivi personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua disponibilità a mantenere le attuali mansioni di **[RUOLO_1]** oppure ad assumere il ruolo di addetto alla contabilità fornitori presso la sede di Vercelli. Dopo aver verificato le esigenze organizzative della nostra filiale, sono lieta di informarla che la sua candidatura è stata inserita nella lista di priorità per le prossime aperture di posizione.\n\nPer procedere con la valutazione definitiva, avremmo bisogno di un breve colloquio conoscitivo, preferibilmente entro la prossima settimana. La prego di indicarmi le sue disponibilità, così da concordare data e orario più comodi per entrambi. In alternativa, possiamo organizzare una video‑call, qualora le fosse più agevole.\n\nNel frattempo, le confermo che la sua richiesta sarà esaminata con la massima attenzione e che le forniremo una risposta definitiva entro il **27 dicembre 2026**, come da lei richiesto.\n\nResto a disposizione per qualsiasi ulteriore chiarimento e la invito a contattarmi al numero 06 1234 5678 o via email all’indirizzo paola.ricciardelli@consorzioagriario.it.\n\nCordiali saluti,\n\n**Dott.ssa Paola Ricciardelli**  \nResponsabile Risorse Umane  \nConsorzio Agrario Terrenove – Sede di Vercelli  \npaola.ricciardelli@consorzioagriario.it  \n06 1234 5678  ",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile dott. Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso i motivi personali alla base della sua richiesta di trasferimento.\n\nHo preso atto della sua disponibilità a mantenere le attuali mansioni di **analista contabile** oppure ad assumere il ruolo di addetto alla contabilità fornitori presso la sede di Bologna. Dopo aver verificato le esigenze organizzative della nostra filiale, sono lieta di informarla che la sua candidatura è stata inserita nella lista di priorità per le prossime aperture di posizione.\n\nPer procedere con la valutazione definitiva, avremmo bisogno di un breve colloquio conoscitivo, preferibilmente entro la prossima settimana. La prego di indicarmi le sue disponibilità, così da concordare data e orario più comodi per entrambi. In alternativa, possiamo organizzare una video‑call, qualora le fosse più agevole.\n\nNel frattempo, le confermo che la sua richiesta sarà esaminata con la massima attenzione e che le forniremo una risposta definitiva entro il **15 dicembre 2026**, come da lei richiesto.\n\nResto a disposizione per qualsiasi ulteriore chiarimento e la invito a contattarmi al numero 06 1234 5678 o via email all’indirizzo paola.ricciardelli@consorzioagriario.it.\n\nCordiali saluti,\n\n**Dott.ssa Paola Ricciardelli**  \nResponsabile Risorse Umane  \nMeridiana Servizi S.p.A. – Sede di Bologna  \npaola.ricciardelli@consorzioagriario.it  \n06 1234 5678  ",
     "events": [
      {
       "surrogate": "Vercelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Consorzio Agrario Terrenove",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Rieti",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "27 marzo 2027",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "27 dicembre 2026",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "78d5c21f1f74"
    },
    "D4+R1": {
     "spans": [
      {
       "start": 49,
       "end": 56,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 75,
       "end": 93,
       "text": "Paola Ricciardelli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 101,
       "end": 116,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 118,
       "end": 136,
       "text": "analista contabile",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 169,
       "end": 193,
       "text": "Meridiana Servizi S.p.A.",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 208,
       "end": 214,
       "text": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 297,
       "end": 304,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 319,
       "end": 331,
       "text": "1 marzo 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 400,
       "end": 428,
       "text": "Ospedale Maggiore di Bologna",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 666,
       "end": 682,
       "text": "15 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 768,
       "end": 780,
       "text": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 797,
       "end": 824,
       "text": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 844,
       "end": 859,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di [CITTA_1]\n\nGentile dott.ssa [PERSONA_1_F],\n\nsono [PERSONA_2_M], [RUOLO_1] dell'ufficio amministrazione di [AZIENDA_1] nella sede di [CITTA_2], dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di [CITTA_1] a partire dal [DATA_1].\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'[STRUTTURA_1] e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il [DATA_2], così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al [TELEFONO_1] o all'indirizzo [EMAIL_1].\n\nCordiali saluti,\n[PERSONA_2_M]\n",
     "disclosure": [
      {
       "surrogate": "[CITTA_1]",
       "value": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città di destinazione del trasferimento"
      },
      {
       "surrogate": "[PERSONA_1_F]",
       "value": "Paola Ricciardelli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "[PERSONA_2_M]",
       "value": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "analista contabile",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere dell'autore"
      },
      {
       "surrogate": "[AZIENDA_1]",
       "value": "Meridiana Servizi S.p.A.",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda dove lavora l'autore"
      },
      {
       "surrogate": "[CITTA_2]",
       "value": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città della sede attuale"
      },
      {
       "surrogate": "[DATA_1]",
       "value": "1 marzo 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di inizio del trasferimento richiesta"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "Ospedale Maggiore di Bologna",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "struttura dove ha ottenuto l'incarico la moglie"
      },
      {
       "surrogate": "[DATA_2]",
       "value": "15 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "scadenza per la risposta richiesta"
      },
      {
       "surrogate": "[TELEFONO_1]",
       "value": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "value": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di [CITTA_1]\n\nGentile dott. [PERSONA_2_M],\n\nla ringrazio per la sua comunicazione e per aver condiviso i motivi personali alla base della sua richiesta di trasferimento alla sede di [CITTA_1].\n\nHo preso visione della sua situazione e, dopo aver consultato il responsabile delle risorse umane e il direttore della sede di [CITTA_1], sono lieta di informarla che la sua richiesta è stata accolta.  \n\n- **Posizione:** potrà continuare a svolgere le stesse mansioni attuali con lo stesso orario, oppure, qualora lo ritenesse più opportuno, potrà essere assegnato al ruolo di addetto alla contabilità fornitori, come da sua disponibilità.  \n- **Data di inizio:** il trasferimento potrà avvenire a partire dal [DATA_1], compatibilmente con le esigenze operative di entrambe le sedi.  \n- **Procedura:** le chiediamo di confermare entro il [DATA_2] la sua accettazione della proposta, indicando la modalità di trasferimento che preferisce (mantenimento mansioni attuali o nuovo ruolo). Successivamente provvederemo a predisporre la documentazione necessaria (modulo di trasferimento interno, eventuali aggiornamenti contrattuali, ecc.) e a coordinare con il dipartimento logistico il supporto al trasloco.\n\nResto a disposizione per qualsiasi chiarimento e per fissare un colloquio telefonico o in videoconferenza, qualora volesse approfondire alcuni dettagli. Può contattarmi al [TELEFONO_1] o via email all’indirizzo [EMAIL_1].\n\nIn attesa di un suo cortese riscontro, le porgo i miei più cordiali saluti.\n\n[PERSONA_1_F]  \n[RUOLO_2] – Risorse Umane  \n[AZIENDA_1] – Sede di [CITTA_1]  \n[TELEFONO_1] – [EMAIL_1]",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna\n\nGentile dott. Alessio Mondini,\n\nla ringrazio per la sua comunicazione e per aver condiviso i motivi personali alla base della sua richiesta di trasferimento alla sede di Bologna.\n\nHo preso visione della sua situazione e, dopo aver consultato il responsabile delle risorse umane e il direttore della sede di Bologna, sono lieta di informarla che la sua richiesta è stata accolta.  \n\n- **Posizione:** potrà continuare a svolgere le stesse mansioni attuali con lo stesso orario, oppure, qualora lo ritenesse più opportuno, potrà essere assegnato al ruolo di addetto alla contabilità fornitori, come da sua disponibilità.  \n- **Data di inizio:** il trasferimento potrà avvenire a partire dal 1 marzo 2027, compatibilmente con le esigenze operative di entrambe le sedi.  \n- **Procedura:** le chiediamo di confermare entro il 15 dicembre 2026 la sua accettazione della proposta, indicando la modalità di trasferimento che preferisce (mantenimento mansioni attuali o nuovo ruolo). Successivamente provvederemo a predisporre la documentazione necessaria (modulo di trasferimento interno, eventuali aggiornamenti contrattuali, ecc.) e a coordinare con il dipartimento logistico il supporto al trasloco.\n\nResto a disposizione per qualsiasi chiarimento e per fissare un colloquio telefonico o in videoconferenza, qualora volesse approfondire alcuni dettagli. Può contattarmi al 333 908 1176 o via email all’indirizzo alessio.mondini@example.org.\n\nIn attesa di un suo cortese riscontro, le porgo i miei più cordiali saluti.\n\nPaola Ricciardelli  \n[RUOLO_2] – Risorse Umane  \nMeridiana Servizi S.p.A. – Sede di Bologna  \n333 908 1176 – alessio.mondini@example.org",
     "events": [
      {
       "surrogate": "[CITTA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_1_F]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[PERSONA_2_M]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[AZIENDA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[CITTA_2]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "[DATA_2]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[TELEFONO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[EMAIL_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_2]",
       "outcome": "hallucinated_token",
       "found_as": "[RUOLO_2]"
      }
     ],
     "fully_restored": false,
     "run_id": "933a73c866b3"
    },
    "D4+R2": {
     "spans": [
      {
       "start": 49,
       "end": 56,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 75,
       "end": 93,
       "text": "Paola Ricciardelli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1"
      },
      {
       "start": 101,
       "end": 116,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      },
      {
       "start": 118,
       "end": 136,
       "text": "analista contabile",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 169,
       "end": 193,
       "text": "Meridiana Servizi S.p.A.",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 208,
       "end": 214,
       "text": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 297,
       "end": 304,
       "text": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 319,
       "end": 331,
       "text": "1 marzo 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 400,
       "end": 428,
       "text": "Ospedale Maggiore di Bologna",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 666,
       "end": 682,
       "text": "15 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3"
      },
      {
       "start": 768,
       "end": 780,
       "text": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 797,
       "end": 824,
       "text": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0"
      },
      {
       "start": 844,
       "end": 859,
       "text": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2"
      }
     ],
     "masked": "Oggetto: richiesta di trasferimento alla sede di Vercelli\n\nGentile dott.ssa Olimpia Pagliarini,\n\nsono Gualtiero Salvadori, [RUOLO_1] dell'ufficio amministrazione di Consorzio Agrario Terrenove nella sede di Rieti, dove lavoro da cinque anni. Le scrivo per chiedere il trasferimento alla sede di Vercelli a partire dal 27 marzo 2027.\n\nMia moglie ha ottenuto un incarico a tempo indeterminato presso l'[STRUTTURA_1] e vorremmo trasferirci insieme a nostro figlio. Sono disponibile a mantenere le stesse mansioni e lo stesso orario; in alternativa accetterei anche un ruolo da addetto alla contabilità fornitori.\n\nLe sarei grato di una risposta entro il 27 dicembre 2026, così da organizzare per tempo il trasloco. Resto a disposizione per un colloquio al 339 778 6313 o all'indirizzo clelia.querzoli@example.com.\n\nCordiali saluti,\nGualtiero Salvadori\n",
     "disclosure": [
      {
       "surrogate": "Vercelli",
       "value": "Bologna",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città di destinazione del trasferimento"
      },
      {
       "surrogate": "Olimpia Pagliarini",
       "value": "Paola Ricciardelli",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D1",
       "reason": ""
      },
      {
       "surrogate": "Gualtiero Salvadori",
       "value": "Alessio Mondini",
       "type": "PERSONA",
       "cls": "direct",
       "source": "D2",
       "reason": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "value": "analista contabile",
       "type": "RUOLO",
       "cls": "quasi",
       "source": "D3",
       "reason": "mestiere dell'autore"
      },
      {
       "surrogate": "Consorzio Agrario Terrenove",
       "value": "Meridiana Servizi S.p.A.",
       "type": "AZIENDA",
       "cls": "quasi",
       "source": "D3",
       "reason": "nome dell'azienda dove lavora l'autore"
      },
      {
       "surrogate": "Rieti",
       "value": "Rimini",
       "type": "CITTA",
       "cls": "quasi",
       "source": "D3",
       "reason": "città della sede attuale"
      },
      {
       "surrogate": "27 marzo 2027",
       "value": "1 marzo 2027",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "data di inizio del trasferimento richiesta"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "value": "Ospedale Maggiore di Bologna",
       "type": "STRUTTURA",
       "cls": "quasi",
       "source": "D3",
       "reason": "struttura dove ha ottenuto l'incarico la moglie"
      },
      {
       "surrogate": "27 dicembre 2026",
       "value": "15 dicembre 2026",
       "type": "DATA",
       "cls": "quasi",
       "source": "D3",
       "reason": "scadenza per la risposta richiesta"
      },
      {
       "surrogate": "339 778 6313",
       "value": "333 908 1176",
       "type": "TELEFONO",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      },
      {
       "surrogate": "clelia.querzoli@example.com",
       "value": "alessio.mondini@example.org",
       "type": "EMAIL",
       "cls": "direct",
       "source": "D0",
       "reason": ""
      }
     ],
     "raw_reply": "**Oggetto:** Re: richiesta di trasferimento alla sede di Vercelli  \n\nGentile dott. Gualtiero Salvadori,\n\nla ringrazio per averci comunicato la sua richiesta di trasferimento alla sede di Vercelli, prevista per il 27 marzo 2027.\n\nHo preso atto della sua attuale posizione di [RUOLO_1] presso l’ufficio amministrazione del Consorzio Agrario Terrenove di Rieti e della motivazione legata al nuovo incarico della sua consorte presso l’[STRUTTURA_1].  \n\nIn merito alla sua disponibilità a mantenere le stesse mansioni e orario, oppure ad accettare un ruolo da addetto alla contabilità fornitori, provvederò a verificare le esigenze operative della sede di Vercelli e la disponibilità di eventuali posizioni compatibili.\n\nLe confermo che il suo caso sarà valutato con la massima attenzione e che le forniremo una risposta entro il 27 dicembre 2026, come richiesto, così da consentirle di organizzare il trasloco in tempi adeguati.\n\nNel frattempo, qualora avesse ulteriori informazioni da condividere o volesse fissare un colloquio, può contattarmi al numero 339 778 6313 o all’indirizzo clelia.querzoli@example.com.\n\nResto a disposizione per qualsiasi chiarimento.\n\nCordiali saluti,\n\n[Nome Cognome]  \n[Posizione] – Ufficio Risorse Umane  \nConsorzio Agrario Terrenove – Sede di Vercelli  \n[Telefono] – [Email]",
     "restored": "**Oggetto:** Re: richiesta di trasferimento alla sede di Bologna  \n\nGentile dott. Alessio Mondini,\n\nla ringrazio per averci comunicato la sua richiesta di trasferimento alla sede di Bologna, prevista per il 1 marzo 2027.\n\nHo preso atto della sua attuale posizione di analista contabile presso l’ufficio amministrazione del Meridiana Servizi S.p.A. di Rimini e della motivazione legata al nuovo incarico della sua consorte presso l’Ospedale Maggiore di Bologna.  \n\nIn merito alla sua disponibilità a mantenere le stesse mansioni e orario, oppure ad accettare un ruolo da addetto alla contabilità fornitori, provvederò a verificare le esigenze operative della sede di Bologna e la disponibilità di eventuali posizioni compatibili.\n\nLe confermo che il suo caso sarà valutato con la massima attenzione e che le forniremo una risposta entro il 15 dicembre 2026, come richiesto, così da consentirle di organizzare il trasloco in tempi adeguati.\n\nNel frattempo, qualora avesse ulteriori informazioni da condividere o volesse fissare un colloquio, può contattarmi al numero 333 908 1176 o all’indirizzo alessio.mondini@example.org.\n\nResto a disposizione per qualsiasi chiarimento.\n\nCordiali saluti,\n\n[Nome Cognome]  \n[Posizione] – Ufficio Risorse Umane  \nMeridiana Servizi S.p.A. – Sede di Bologna  \n[Telefono] – [Email]",
     "events": [
      {
       "surrogate": "Vercelli",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Olimpia Pagliarini",
       "outcome": "dropped",
       "found_as": ""
      },
      {
       "surrogate": "Gualtiero Salvadori",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "[RUOLO_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Consorzio Agrario Terrenove",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "Rieti",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "27 marzo 2027",
       "outcome": "restored",
       "found_as": "27 marzo 2027"
      },
      {
       "surrogate": "[STRUTTURA_1]",
       "outcome": "restored",
       "found_as": ""
      },
      {
       "surrogate": "27 dicembre 2026",
       "outcome": "restored",
       "found_as": "27 dicembre 2026"
      },
      {
       "surrogate": "339 778 6313",
       "outcome": "restored",
       "found_as": "339 778 6313"
      },
      {
       "surrogate": "clelia.querzoli@example.com",
       "outcome": "restored",
       "found_as": ""
      }
     ],
     "fully_restored": true,
     "run_id": "65b4d39c07a9"
    }
   },
   "calc_blocked": {
    "D0": {},
    "D1": {},
    "D2": {},
    "D3": {
     "DATA": 2
    },
    "D4": {
     "DATA": 2
    }
   }
  }
 ]
};
