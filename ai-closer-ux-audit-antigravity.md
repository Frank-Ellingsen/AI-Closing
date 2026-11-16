# AI Closer — Antigravity UX/UI Brukertest og Heuristisk Systemevaluering

Dette dokumentet etablerer en helhetlig brukertest, heuristisk evaluering og friksjonsanalyse for **AI Closer — Enterprise Financial Close & Superuser Control Room**. Formålet med et "Antigravity"-rammeverk innen finansiell programvarearkitektur er å identifisere og fjerne kognitiv tyngdekraft, administrative omveier og visuell støy, slik at økonomiavdelingen oppnår en tilnærmet vektløs og deterministisk månedsavslutning. Evalueringen dekker både linjeorganisasjonens operative roller (Preparer, Approver, Revisor) og avanserte oppgaver forbeholdt Superbrukeren.

---

## 1. Antigravity-Rammeverket for Finansielle Kontrollrom

I tradisjonelle regnskapssystemer skaper manuelle avstemminger, uklare filformater og manglende sporbarhet en betydelig friksjon som forlenger avslutningsprosessen. Antigravity-metodikken vurderer brukergrensesnittets evne til å redusere denne friksjonen gjennom fire kjerneakser:

*   **Kognitiv belastning (Mental Drag):** Hvor mye mental kapasitet kreves for å tolke systemstatus, verifisere avvik og bekrefte dataintegritet?
*   **Interaksjonsfriksjon (Click Friction):** Antall unødige klikk, kontekstskifter og navigasjonsomveier mellom datafangst, transaksjonsmatching og balansekontroll.
*   **Reversibilitet og feiltoleranse (Zero-Gravity Safety):** Hvor enkelt og trygt kan en bruker oppheve feilaktige handlinger uten å kompromittere revisjonssporet?
*   **Deterministisk forklarbarhet (Explainable Autonomy):** Hvor klart skiller grensesnittet mellom absolutte matematiske regler og veiledende maskinlæringsforslag?

Evalueringen bygger på anerkjente standarder for finansteknologi i Norden, herunder DFØs retningslinjer for transaksjonsavstemming, ISO 20022 CAMT.053, SAF-T Financial v1.30/v1.40, samt internasjonale krav til internkontroll og tilgjengelighet (WCAG 2.1 AA og Nielsens ti heuristikker).

---

## 2. Nielsens Heuristiske Evaluering av Kontrollrommet

Gjennomgangen av systemets arkitektur og brukergrensesnitt avdekker følgende funn vurdert mot etablerte prinsipper for menneske-maskin-interaksjon:

### 2.1. Synlighet av systemstatus
Kontrollrommet gir kontinuerlig tilbakemelding om finansiell tilstand via den øverste KPI-stripen. Banksaldo (UB), Hovedbokssaldo (UB) og det uavklarte avviket (Delta) kalkuleres og oppdateres fortløpende.

Tidligere versjoner av importgrensesnittet manglet en eksplisitt fremstilling av hvordan importerte transaksjoner påvirket periodens saldo før dataene ble overført til avstemmingsmotoren. Denne friksjonen er nå eliminert ved at Import Studio beregner og viser balansebroen direkte:

$$\text{Inngående Balanse (IB)} \pm \text{Periodens Bevegelser} = \text{Beregnet Utgående Balanse (UB)}$$

Dette sikrer at brukeren umiddelbart ser om innleste transaksjoner harmonerer med offisiell saldorapport før matching igangsettes.

### 2.2. Samsvar mellom system og virkeligheten
Systemet benytter konsistent norsk autorisert regnskapsterminologi. Begreper som *Debet/Kredit*, *KID/OCR*, *Valuteringsdato*, *WBS-prosjektelementer*, *Spin-off-bilag* og *4-delt avstemmingsmatrise* følger etablert regnskapsstandard. Dette fjerner behovet for mental oversettelse mellom skjermbilde og revisjonspraksis.

### 2.3. Brukerkontroll og frihet
Et vesentlig krav til feiltoleranse i avstemmingssystemer er muligheten til å angre lukkede poster. AI Closer tilbyr en dedikert ett-klikks `[ Opphev ]`-knapp på samtlige rader i listen over avstemte poster. Dette tilbakefører transaksjonene til åpen status og gjenoppretter det opprinnelige avviket uten forsinkelse eller behov for administrativ overstyring.

### 2.4. Konsistens og standarder
Typografi og farger følger et stramt industrielt designsystem basert på IBM Plex Sans for tekst og IBM Plex Mono for tallstørrelser. Modusen for "Soft RAG" erstatter harde rød-grønne kontraster med ergonomiske, fargeblindsikre fargetoner, noe som reduserer øyetretthet og sikrer etterlevelse av universell utforming.

### 2.5. Feilforebygging og logiske sperrer
For å hindre premature eller feilaktige godkjenninger inneholder sertifiseringsmodulen en absolutt matematisk sperre:

$$\Delta \ne 0{,}00 \text{ NOK} \implies \text{Sertifiseringshandling deaktivert}$$

Kontoen kan ikke sertifiseres før enhver differanse er fullt ut forklart gjennom godkjente spin-off-bilag eller dokumenterte åpne poster i den 4-delte matrisen.

---

## 3. Brukertestprotokoller for Operative Roller

Testprotokollene simulerer en fullstendig månedsavslutning for **Nordic Engineering Projects AS** (Konto 1925 Nordea Driftskonto NOK, Periode Oktober 2026). Nedenfor evalueres oppgavene fordelt på tre sentrale personaer.

### 3.1. Persona 1: Regnskapsfører / Preparer (Ingrid, 34 år)
Ingrid har ansvaret for den daglige og månedlige avstemmingen, innlesing av rådata, opprettelse av korreksjonsbilag og forberedelse av dokumentasjon til kontroller.

#### Testscenario 1: To-delt filimport med saldokontroll
*   **Oppgave:** Navigere til Import Studio, hente inn bankutskrift (`bank_nordea_2026_10.csv`) i Del A og hovedboksuttrekk (`erp_hovedbok_2026_10.csv`) i Del B, og validere summene mot forhåndsdefinert IB.
*   **Observasjon:** Brukeren valgte filene via de tradisjonelle filvelgerne. Systemet leste 7 transaksjonslinjer fra ERP med sum debet på 8 120 400,00 NOK og sum kredit på 7 619 950,00 NOK.
*   **Resultat:** Kassetten viste en beregnet UB på 6 342 550,00 NOK, som stemte på øret med ERP-saldorapporten. Brukeren uttrykte høy trygghet ved at overføringsknappen tydelig indikerte antall linjer som ville tilflyte Matcher.

#### Testscenario 2: Transaksjonsavstemming og godkjenning av Spin-off bilag
*   **Oppgave:** Kjøre automatisk matching og behandle gjenstående bankgebyrer og renteposter per 31.10.2026.
*   **Observasjon:** De ordinære driftslinjene ble matchet av regel `R-01` (KID) og `R-02` (Faktura m/ float). To uavstemte poster gjensto i banken: depotgebyr på 2 450,00 NOK og lånerente på 18 750,00 NOK.
*   **Resultat:** I modulen for bilagsforslag lå begge postene ferdig kontert (Debet 7770 / Kredit 1925 for gebyr, og Debet 8150 / Kredit 1925 for renter). Ved godkjenning falt uforklart differanse fra 21 200,00 NOK til nøyaktig 0,00 NOK.

#### Testscenario 3: Overføring av åpne poster til Balancer
*   **Oppgave:** Overføre uavstemte poster fra Matcher til Balancer etter fullført avstemming.
*   **Observasjon:** Brukeren benyttet handlingen "Send åpne poster til Balancer" for periode `2026-10`.
*   **Resultat:** Postene ble umiddelbart tilgjengelige under kontospesifikasjonen i Balancer, og perioden ble merket med stjernesymbol for å forhindre utilsiktede duplikatoverføringer.

### 3.2. Persona 2: Controller / Approver (Henrik, 48 år)
Henrik kontrollerer at avstemmingen tilfredsstiller dokumentasjonskravene og signerer på ledelsens vegne.

#### Testscenario: Gjennomgang av 4-delt matrise og signering
*   **Oppgave:** Verifisere at den 4-delte matrisen dokumenterer alle avvik, kontrollere aldersfordeling på åpne poster og utføre Approver Sign-off.
*   **Observasjon:** Henrik verifiserte at Boks 2 (Debetert Bank / Ikke kreditert ERP) forklarte de periodiserte postene, og at aldersfordelingen i Analytics ikke inneholdt poster over 60 dager.
*   **Resultat:** Approver Sign-off ble utført med ett klikk. Systemet genererte en digital tidsstempelkvittering og låste kontoen mot videre manuelle endringer.

### 3.3. Persona 3: Ekstern Revisor / Auditor (Camilla, 41 år)
Camilla reviderer selskapets internkontroll over finansiell rapportering og krever uforanderlige bevis.

#### Testscenario: Generering av revisjonsdossier (PBC-pakke)
*   **Oppgave:** Validere sjekklisten i Task Manager og eksportere fullstendig dokumentasjonspakke.
*   **Observasjon:** Camilla inspiserte gjennomføringen av oppgavene T-01 til T-16 og aktiverte eksportfunksjonen for signert revisjonsrapport.
*   **Resultat:** Grensesnittet genererte et ferdig formatert utskriftsdokument med formell selskapsinformasjon, fullstendig oppgavelogg, matematiske balansebevis og kryptografisk SHA-256 forsegling.

---

## 4. Dedikert Brukertest og Friksjonsanalyse for Superbrukeren

Superbrukeren krever full administrativ fleksibilitet for å konfigurere konti, skreddersy avstemmingsregler og overvåke databasene uten bistand fra eksterne utviklere. Nedenfor følger evalueringen av Superbruker-oppsettet.

### 4.1. Dynamisk Kontokonfigurasjon og IB-Håndtering
Superbrukeren har tilgang til et helhetlig administrasjonspanel for å opprette og vedlikeholde kontostrukturen:

| Parameter | Validering og Funksjon | Brukerrespons | Vurdering |
| :--- | :--- | :--- | :--- |
| **Kontoidentifikator** | Alfanumerisk kode (f.eks. `1925`, `1920`, `1940`). | Oppdaterer kontekstvelgere globalt i hele applikasjonen. | Optimal |
| **Bankdetaljer & IBAN** | Validerer gyldig bankkontonummer og ISO-standard IBAN. | Knytter kildeprofiler i Import Studio direkte til riktig konto. | Optimal |
| **Valutastyring** | Støtte for basisvaluta (NOK) og fremmedvaluta (EUR, USD). | Aktiverer agio/disagio-modul ved avstemming av valutakonti. | Høy verdi |
| **Dynamisk IB-rulling** | Automatisk innhenting av forrige måneds UB som ny IB. | Fjerner behovet for manuell overføring av åpningsbalanser. | Vektløs |

### 4.2. Visuell Regelbygger (Rule Builder)
Superbrukeren konfigurerer matchinglogikken gjennom en strukturert regelbygger. Evalueringen testet oppsett av en sammensatt samleoppgjørsregel (1:M):

*   **Testkrav:** Etablere en regel som matcher én samlet bankutbetaling mot flere åpne leverandørposter i ERP basert på felles batch-referanse, med tillatt datoavvik på inntil tre virkedager.
*   **Gjennomføring:** Superbrukeren definerte regelkode `R-03`, valgte kardinalitet `1:M`, anga referansefelt og satte dato-float til 3 dager.
*   **Identifisert forbedringspunkt:** Selv om regelen ble lagret korrekt, opplevde testpersonen en kognitiv usikkerhet knyttet til treffsikkerheten før regelen ble satt i produksjon. Det anbefales å innføre en "Simuler regel"-knapp som utfører en tørrkjøring (Dry-Run) mot eksisterende åpne poster og rapporterer antall potensielle treff.

### 4.3. Toleranse for Øreavrunding og Automatisk Motpostering
For å håndtere uunngåelige bankdifferanser (f.eks. renter eller gebyrbrøkdeler) inneholder systemet en konfigurerbar øretoleranse:

*   **Testoppsett:** Superbrukeren satte tillatt avvik til $\pm 0{,}50 \text{ NOK}$ og definerte motkonto for avrunding til `Konto 7740 Øreavrunding`.
*   **Observasjon:** En bankpost på 15 200,35 NOK ble avstemt mot en ERP-post på 15 200,00 NOK.
*   **Resultat:** Systemet godkjente matchen, flagget den med badge `R-ROUND (0,35 kr)` og opprettet automatisk et balansert korreksjonsbilag på 0,35 NOK mot konto 7740. Dette fjerner hundrevis av manuelle mikroposteringer i løpet av et regnskapsår.

### 4.4. Databaseintegritet og Toveis DuckDB-Synkronisering
Superbrukeren overvåker helsetilstanden til de tre lokale DuckDB-databasene (`reconciliation.duckdb`, `reconciled_transactions.duckdb` og `unreconciled_transactions.duckdb`):

*   **Testscenario:** Kjøre lokal synkronisering via FastAPI-backend (`api_server.py`) og verifisere fallback ved serverbortfall.
*   **Resultat:** Applikasjonen synkroniserer transaksjoner i sanntid over REST API. Dersom API-serveren kobles fra, varsler grensesnittet med en diskret indikator og skifter sømløst over til lokal nettlesertilstand uten tap av data eller systemkrasj.

---

## 5. Antigravity Friksjonsmatrise (Friction vs. Lift)

Nedenfor sammenstilles de identifiserte friksjonspunktene med de implementerte arkitektoniske løsningene som sikrer en uanstrengt arbeidsflyt:

| Område i Appen | Opprinnelig Friksjonspunkt (Mental Drag) | Operativ Konsekvens | Antigravity Løsning (Vektløs Flyt) |
| :--- | :--- | :--- | :--- |
| **Import Studio** | Usikkerhet om filens fortegnskonvensjon harmonerer med debet/kredit i ERP. | Behov for manuell forhåndskontroll i regneark. | Automatisk gjenkjenning av fortegn, live tabellvisning og sanntids balansekassett for IB $\rightarrow$ UB. |
| **Matcher** | Manuell gjennomgang av hundrevis av transaksjoner med avvikende referanser. | Økt tidsbruk og risiko for oversette matcher. | Deterministisk regelstige supplert med AI Suggestive Copilot som gir forklarende forslag. |
| **Balancer** | Risiko for å overføre åpne poster før transaksjonsmatching er fullført. | Fare for duplikate oppføringer i balansespesifikasjonen. | Visuell varsling og stjernemerking (`*`) av perioder som allerede er overført, i tråd med DFØ-standard. |
| **Bilagsbehandling** | Manuell opprettelse og tildeling av kontoer for bankgebyr og renter i ERP. | Fragmentert arbeidsflyt og forsinket periodeavslutning. | Autonome forslag generert direkte fra banktransaksjoner med balanserte debet/kredit-linjer ($\Delta = 0{,}00$). |
| **Superbruker** | Usikkerhet ved konfigurering av komplekse avstemmingsregler og dato-float. | Redsel for at feilkonfigurerte regler skal auto-lukke feil poster. | Tydelig kardinalitetsvelger (1:1, 1:M, M:1) og forhåndsdefinerte maler for nordiske standardformater. |

---

## 6. Prioritert Forbedringsbacklog for Videre Utvikling

For å videreføre systemets posisjon som et helhetlig, revisjonssikkert finanskontrollrom, anbefales følgende tiltak inndelt i prioriterte faser:

### Prioritet 0: Kritiske forbedringer (P0 — Umiddelbar implementering)
1.  **Simuleringsverktøy i Regelbyggeren (Dry-Run):** Gi superbrukeren mulighet til å teste en nyopprettet regel mot gjeldende periodes uavstemte poster med umiddelbar forhåndsvisning av treffrate før regelen låses.
2.  **Tastaturnavigasjon for volumavstemming (Power-User Shortcuts):** Innføre tastatursnarveier i Matcher Workbench (`Mellomrom` for å markere rader, `Enter` for å bekrefte match, `Ctrl+Z` for å oppheve siste match).
3.  **Permanent lagring av importprofiler:** Lagre tilpassede feltkonfigurasjoner i DuckDB slik at nye filopplastinger fra samme bank automatisk gjenkjenner kolonnerekkefølgen.

### Prioritet 1: Viktige funksjonalitetsløft (P1 — Neste sprint)
1.  **Automatisk Agio/Disagio-motor:** Automatisk utregning og kontering av valutadifferanser mot konto 8060 og 8160 når valutaposter i EUR/USD gjøres opp mot NOK.
2.  **Massegodkjenning av periodiseringsbilag:** Mulighet til å huke av og godkjenne samtlige spin-off-bilag i én samlet operasjon etter at beløpene er kontrollert.
3.  **Varsling ved balansebrudd (Balance Break Alert):** Umiddelbar varsling i grensesnittet dersom en etterpostering i ERP forrykker saldoen på en konto som allerede er ferdig sertifisert for perioden.

### Prioritet 2: Videreutvikling og finesse (P2 — Strategisk veikart)
1.  **Direkte Altinn-eksport for SAF-T:** Integrasjon mot Altinns grensesnitt for sikker digital oversendelse av avstemmingsdossier og XML-pakker ved bokettersyn.
2.  **Prediktiv avslutningsprognose i Analytics:** Maskinlæringsalgoritme som estimerer nøyaktig fullføringstidspunkt for månedsavslutningen basert på historisk avvikshåndtering og gjenværende oppgaver i Task Manager.

---

Gjennom disse tiltakene sikrer AI Closer at komplekse finansielle krav ivaretas med minimal kognitiv friksjon, maksimal revisjonssikkerhet og full autonomi for både operative brukere og superbrukere.
