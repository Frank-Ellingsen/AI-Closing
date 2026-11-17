# AI Closer — Enterprise Financial Close Control Room

Nordic Engineering Projects AS · Org.nr 984 512 330 MVA  
Komplett Record-to-Report (R2R) kontrollrom for automatisert transaksjonsavstemming, 4-veis balansekontroll, revisjonsdossier og deterministisk månedsavslutning.

---

## Produksjonsmiljo og Arkitektur

- Web Control Room: GitHub Pages produksjonsmiljo
- Analytics Backend: Streamlit lokal port 8501 eller Streamlit Community Cloud
- Lokal Database: Embedded DuckDB (reconciliation.duckdb, reconciled_transactions.duckdb, unreconciled_transactions.duckdb)
- API Server: FastAPI (api_server.py) for toveis synkronisering mellom frontend og databasesjiktet

---

## Visuell Fargekoding

Applikasjonen har en gjennomfort visuell differensiering som gjor det enkelt for regnskapsforere og controllere a skille kilder fra hverandre:

- Hovedbok og Reskontro (ERP): Subtilt grablatt (#f0f4f8, border #cbd5e1, tekst #1e3a8a). Gjelder bokforte transaksjoner, saldorapporter, bilag og debet/kredit i ERP.
- Bankforbindelse: Subtilt lysgult (#fefce8, border #fef08a, tekst #854d0e). Gjelder elektroniske kontoutdrag, valuteringsdatoer, CAMT.053 og banktransaksjoner.
- Soft RAG / Tilgjengelighet: WCAG 2.1 AA kompatibel palett for fargeblinde brukere.

---

## Nokkelfunksjoner og Modulstruktur

### 1. 4-Delt Balansekontroll og Avstemmingsmatrise
- Balansebroen: Verifiserer formelen IB + Periodens bevegelser = UB i sanntid.
- 4-Veis Revisjonsmatrise:
  1. Kreditert Bank / Ikke debetert ERP
  2. Debetert Bank / Ikke kreditert ERP (inkl. uavstemte bankgebyrer og renter)
  3. Debetert ERP / Ikke kreditert Bank
  4. Kreditert ERP / Ikke debetert Bank
- Matematisk bevis: Etablerer formelt revisjonsbevis der uavklart avvik dokumenteres til noyaktig Delta = 0,00 NOK.
- Balance Break Alert: Overvaker sertifiserte saldoer; dersom etterposteringer eller nye importfiler endrer en godkjent periode, utloses en umiddelbar revisjonsalarm.

### 2. To-delt Importstudio (Bank og ERP)
- Del A: Bank Import Studio (Lysgul profil)
  - Stotter Nordea Corporate, DNB Telepay, ISO 20022 CAMT.053 XML og MT940.
  - Valg av enkeltfil eller hel lokal katalog via webkitdirectory.
  - Sanntids saldokontroll: Viser Bankens IB, manedens inn- og utbetalinger, og beregnet ny UB.
- Del B: ERP Import Studio (Grabla profil)
  - Stotter Visma, Microsoft Dynamics 365 Business Central, Xledger og SAF-T Financial v1.30/v1.40 XML.
  - Valg av enkeltfil eller lokal katalog for batch-import.
  - Sanntids saldokontroll som verifiserer at importerte transaksjoner stemmer eksakt overens med den offisielle ERP-saldorapporten.

### 3. AI Closer Matcher Workbench
- Regelstigen:
  - R-01: Eksakt 1:1 KID/OCR-match (samme belop og dato).
  - R-02: 1:1 Faktura/arkivreferanse med dato-float.
  - R-03: 1:M Samleoppgjor og batch-utbetalinger.
  - R-04: Multi-Way Gateway for betalingsformidlere (Nets, Vipps, Stripe, Adyen).
- Suggestive Matching (AI Copilot): Probabilistisk maskinlaering som foreslar kandidater ved skrivefeil eller datoavvik med tillitsscore og forklaring (Human-in-the-Loop).
- Ett-klikks Unmatch: Full historikk med umiddelbar angremulighet som tilbakeforer transaksjoner til apne poster.
- DFO-Metoden: Dedikert funksjon for a overfore gjenstaende apne poster direkte til AI Closer Balancer etter fullfort transaksjonsmatching.

### 4. Reskontro-, Intercompany- og Avviks-Hub
- Subledger-to-GL Avstemming: Automatisk kontroll av Kundereskontro (Konto 1500) og Leverandorreskontro (Konto 2400) mot Hovedbok, med varsling om manuelle bilag fort utenom reskontro.
- Intercompany-avstemming: 2-veis konsernmatrise som avstemmer mellomvaerende (Konto 1310) mot datterselskapers tilsvarende gjeldskonto.
- Statistisk Avvikskontroll:
  - Benford's Law analyse av forste siffer for a identifisere uvanlige eller manipulerte bilagsmonstre.
  - Duplikatvarsler for identiske belop til samme mottaker innenfor et kort tidsrom.
  - Terskelkontroll for fakturaer lagt rett under attestasjonsgrensen.
- Norges Bank Valutakurs-Feed: Automatisk manedssluttoppslag for EUR/NOK pa konto 1940 med beregning av agio/disagio.

### 5. AI Closer Balancer og 3-Trinns Sertifisering
- Kontospesifikasjon (Open Items): Aldersfordeling i standardbotter (0-30d, 31-60d, 61-90d, 90+d).
- Rollebasert Sertifiseringsmatrise:
  - Preparer: Klargjor underlag og foretar primaersignering.
  - Approver: Controller godkjenner avstemmingen.
  - Reviewer / Revisor: Ekstern revisor eller CFO laser perioden.
- Auto-Sertifisering: Lavrisikokontoer med avvik Delta = 0,00 kr og ingen apne poster over terskelverdien sertifiseres automatisk.

### 6. Manedlig Avslutningssjekkliste (Task Manager)
- 16 Standardoppgaver (T-01 til T-16) fordelt pa Fase 1 (Forberedelse), Fase 2 (Matching), Fase 3 (Balansekontroll) og Fase 4 (Sertifisering).
- Formell PDF/Print Revisjonseksport: Genererer et komplett revisjonsdossier med signaturblokker, balansebevis og kryptografisk SHA-256 forsegling.

### 7. Bilagsforslag og SAF-T v1.30/v1.40 Validator
- Autonome Spin-Off Forslag: Genererer forslag for ubokforte bankposter for oktober 2026:
  - Bankgebyr: 2 450,00 NOK (Debet 7770 / Kredit 1925)
  - Lanerenter: 18 750,00 NOK (Debet 8150 / Kredit 1925)
- Pre-flight Sjekk: Validerer standardkontokoder, MVA-koder og balansert debet/kredit for eksport til ERP.

### 8. Superbruker og Kontoadministrasjon
- 100% Dynamisk: Opprett og rediger konti i sanntid uten kodeendringer.
- Regelbygger: Konfigurer nye regler med tilpasset feltmatching, toleranser og dato-float.
- Oreavrunding: Konfigurerbar terskel (f.eks. 0,50 NOK) med automatisk kontering mot Konto 7740.
- DuckDB Monitor: Sanntidsstatus pa lokale tabeller og transaksjonsvolum.

---

## Brukerveiledning (User Guide)

### For Klargjorer (Preparer)
1. Velg Konto og Periode i topplinjen.
2. Ga til Import Studio. Last opp bankutskriften i Del A og ERP-hovedboken i Del B. Kontroller at gronn statusindikator bekrefter at IB pluss/minus bevegelser er lik UB.
3. Ga til AI Closer Matcher. Klikk Kjor Auto-Match. Gjennomga apne poster og godkjenn eventuelle AI-forslag i Suggestive Drawer.
4. Ga til Bilagsforslag, godkjenn foreslatte spin-off poster (gebyrer og renter), og last ned eksportfilen for innlesing i ERP.
5. Under Matcher velger du de tre prikkene og klikker Send til Balancer (DFO-metoden) for a overfore uavstemte poster.
6. Apne AI Closer Balancer, verifiser at uavklart avvik er 0,00 NOK, og klikk Signer som Preparer.

### For Controller og Godkjenner (Approver)
1. Apne 4-Delt Balansekontroll. Bekreft at differansen Delta er 0,00 NOK, og gjennomga de fire revisjonskategoriene.
2. Verifiser at det ikke foreligger brudd pa reskontroavstemmingen (konto 1500/2400) eller avviksvarsler fra statistiske kontroller.
3. Apne Task Manager, bekreft at oppgavene T-01 til T-13 er fullfort, og signer ut T-15.
4. I AI Closer Balancer signerer du som Approver.

### For Superbruker
1. Ga til Superbruker, klikk Ny Konto, fyll ut kontonummer, navn, IBAN og inngaende balanser.
2. Apne Regelbygger, velg kildekolonner for Bank og ERP, definer kardinalitet (1:1, 1:M) og tillatt dato-float.
3. Juster maksimal tillatt oredifferanse for automatisk postering mot oreavrundingskonto 7740.

---

## Lokal Kkjoring

1. Installer avhengigheter:
   pip install -r requirements.txt
2. Klargjor DuckDB og generer testdata:
   python setup_duckdb.py
   python generate_erp_data.py
3. Start API-server og Streamlit:
   python api_server.py
   streamlit run app.py
4. Apne index.html i nettleseren.
