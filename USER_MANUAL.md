# CLOSE-AI Financial Close Room — Brukermanual (v2026.10)
**Systemansvarlig & Prosjektcontroller:** Frank Ellingsen  
**Selskap:** Nordic Engineering Projects AS (Org.nr 984 210 552)  
**Standarder:** NGAAP / IFRS 9, ISA 240 / 315 / 500, SAF-T Financial v1.3  
**Databasemotor:** DuckDB 1.5.3 (ACID Real-time Analytical Store)

---

## Innholdsfortegnelse
1. [Innledning & Systemarkitektur](#1-innledning--systemarkitektur)
2. [Oversikt over Brukergrensesnittet (Cockpit)](#2-oversikt-over-brukergrensesnittet-cockpit)
3. [Den 5-Trinns Sekvensielle Avslutningsprosessen (Close Gates)](#3-den-5-trinns-sekvensielle-avslutningsprosessen-close-gates)
4. [Modulveiledning (De 8 Fanene)](#4-modulveiledning-de-8-fanene)
   * [Fane 1: Datakilder & Automatisk Regelmotor](#fane-1-datakilder--automatisk-regelmotor)
   * [Fane 2: Balansekontroll & Avstemmingsbro](#fane-2-balansekontroll--avstemmingsbro)
   * [Fane 3: Åpne Poster (Bank & ERP) med Betinget RAG](#fane-3-åpne-poster-bank--erp-med-betinget-rag)
   * [Fane 4: Bilagsstudio & SAF-T Korreksjoner](#fane-4-bilagsstudio--saf-t-korreksjoner)
   * [Fane 5: Aldersfordeling & IFRS 9 Tapsavsetning](#fane-5-aldersfordeling--ifrs-9-tapsavsetning)
   * [Fane 6: Avstemte Poster & Revisjonskjede](#fane-6-avstemte-poster--revisjonskjede)
   * [Fane 7: CFO-Rapport & Ledelsessammendrag](#fane-7-cfo-rapport--ledelsessammendrag)
   * [Fane 8: Revisjon & Revisorpakke (ISA 500)](#fane-8-revisjon--revisorpakke-isa-500)
5. [DuckDB Analytisk Database & Live Spørringer](#5-duckdb-analytisk-database--live-spørringer)
6. [Pop-Up Chatbot & Copilot Assistent](#6-pop-up-chatbot--copilot-assistent)
7. [Superbruker & Systemansvarlig Guide](#7-superbruker--systemansvarlig-guide)
8. [Prosjektcontrolling & WBS-Oppfølging (EAC/ETC)](#8-prosjektcontrolling--wbs-oppfølging-eacetc)
9. [Feilsøking & Hurtighandlinger](#9-feilsøking--hurtighandlinger)

---

## 1. Innledning & Systemarkitektur

**CLOSE-AI Financial Close Room** er en integrert, autonom finansiell avstemmings- og månedsavslutningsplattform utviklet for prosjektintensive virksomheter innen engineering, maritim industri og forsvar. 

Plattformen automatiserer avstemmingen mellom eksterne bankkilder (f.eks. DNB) og interne ERP-systemer (Visma, Business Central, Xledger, Tripletex, SAP), isolerer avvik (tidsforskjeller, bankgebyrer, agio), genererer balanserte korreksjonsbilag, og forsegler regnskapsperioden med en uforanderlig SHA-256 kryptografisk revisjonskjede.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLOSE-AI ARKITEKTUR                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  KILDER: CAMT.053 XML / MT940 / BAI2 / SAF-T / OData API / SFTP Host-to-Host │
│                                    │                                        │
│                                    ▼                                        │
│  LAKEHOUSE BRONSE -> SØLV -> GULL (Medallion Pipeline & DuckDB)             │
│                                    │                                        │
│                                    ▼                                        │
│  AUTONOM MATCHINGMOTOR (R-01 til R-04, Regex Agent, Combinatorial Solver)   │
│                                    │                                        │
│            ┌───────────────────────┴───────────────────────┐                │
│            ▼                                               ▼                │
│   reconciled_transactions                        unreconciled_transactions  │
│   (Låst, Hashet, Gebyrsplittet)                  (RAG, IFRS 9, WBS-Tags)    │
│            │                                               │                │
│            └───────────────────────┬───────────────────────┘                │
│                                    ▼                                        │
│  CLOSE COCKPIT (Web UI, Tufte Data-Ink, 8 Faner, Dual-Role Chatbot Copilot) │
│                                    │                                        │
│                                    ▼                                        │
│  4-ØYNE GODKJENNING (Controller Sign-off -> CFO Lock -> ISA 500 Revisorpakke)│
└─────────────────────────────────────────────────────────────────────────────┘
```

### Sentrale Kontonumre i Løsningen
* **1920 Driftskonto NOK**: Hovedoppgjørskonto i DNB.
* **1921 Driftskonto USD / EUR**: Valutakonti for internasjonale innkjøp og prosjektoppgjør.
* **1950 Skattetrekk**: Sperret skattetrekkskonto (avstemmes 1:1 mot terminoppgave).
* **7770 Bank- og kortgebyrer**: Kostnadskonto for automatisk isolerte transaksjonskostnader.
* **7799 Øreavrunding**: Automatisk driftskostnadspostering for øresavvik under toleransegrensen ($\le 5\text{ NOK}$).
* **8160 Valutadifferanse (Agio / Disagio)**: Urealiserte og realiserte kursdifferanser.

---

## 2. Oversikt over Brukergrensesnittet (Cockpit)

Brukergrensesnittet følger Edward Tuftes prinsipper for **Data-Ink Ratio**:
* Ingen unødige 3D-skygger eller forstyrrende fargeelementer.
* Tallkolonner er strengt høyrejusterte med tabulære tallfonter (`SFMono-Regular / Consolas`).
* Farger er reservert for informasjonsbærende statusindikatorer (**RAG: Rød, Gul, Grønn**).

### Cockpitens Hovedelementer
1. **Topplinje (Header)**:
   * **WBS-Filter**: Filtrer hele cockpiten på prosjekter (f.eks. `WBS-401 Subsea Manifold`, `WBS-408 Kystvakt`, `WBS-412 Landanlegg`).
   * **Periodeselektor**: Bytt mellom aktive og historiske perioder (`Oktober 2026`, `September 2026`, `August 2026`).
   * **Tilbakestill periode**: Gjenoppretter periodens rådata for demonstrasjons- eller testformål.
2. **Executive KPI Strip**:
   * 6 nøkkelkort med dynamiske RAG-toppkanter: *Avstemt periode*, *Saldo Bank*, *Saldo ERP*, *Differanse ($\Delta$)*, *Åpne poster Bank*, og *Åpne poster ERP*.
3. **Beredskapsmåler & Nedtelling (Close Clock)**:
   * Viser *Close Readiness Index* (0–100 %) og dager/timer gjenstående til månedlig cut-off frist.
4. **Sekvensiell Prosesslinje (Close Stepper)**:
   * 5 interaktive kontrollporter som låses opp etter hvert som kriteriene innfris.
5. **Navigasjonsfaner**: 8 dedikerte arbeidsmoduler.
6. **Flytende Chatbot (Nede til høyre)**: AI-assistent for både saksbehandlende controllere og superbrukere.

---

## 3. Den 5-Trinns Sekvensielle Avslutningsprosessen (Close Gates)

Månedsavslutningen er designet som en sekvensiell prosess der hvert trinn bygger på det forrige:

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  PORT 1  │ ──> │  PORT 2  │ ──> │  PORT 3  │ ──> │  PORT 4  │ ──> │  PORT 5  │
│  Import  │     │ Autoløp  │     │ Manuell  │     │  Bilag   │     │ Sign-off │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
```

1. **Port 1: Datainnhenting & Kildevalidering**
   * *Mål:* Bekrefte at CAMT.053 bankfil og ERP SAF-T uttrekk er innlest uten brudd på hash eller manglende linjer.
   * *Status:* Grønn når kilder er bekreftet.
2. **Port 2: Autonom Regelkjøring**
   * *Mål:* Kjøre regelkjedene (R-01 til R-04). Systemet matcher automatisk $\ge 80\,\%$ av volumet.
   * *Status:* Grønn når autokandidater er prosessert.
3. **Port 3: Behandling av Åpne Poster & Tidsavvik**
   * *Mål:* Gjennomgå uavstemte poster, bekrefte transittposter (f.eks. Bergen Marine underveis 45 000 kr) og godkjenne Copilot-forslag.
   * *Status:* Grønn når alle gjenstående poster har en gyldig avviksklassifisering.
4. **Port 4: Korreksjonsbilag & Hovedboksoppdatering**
   * *Mål:* Bokføre genererte spinn-off bilag for bankgebyr (Konto 7770), agio (Konto 8160) og pensjon mot Hovedbok 1920.
   * *Status:* Grønn når alle spinn-off bilag har status `BOKFØRT`.
5. **Port 5: 4-Øyne Signering, CFO Låsing & Revisorpakke**
   * *Mål:* Frank Ellingsen (Controller) bekrefter avstemmingsbroen ($\Delta = 0,00\text{ kr}$). Deretter godkjenner og låser CFO perioden, og revisjonsdossieret forsegles.

---

## 4. Modulveiledning (De 8 Fanene)

### Fane 1: Datakilder & Automatisk Regelmotor
* **Formål:** Innlasting av rådata og utførelse av AI Close-regelmotoren.
* **Regelhierarki:**
  * **R-01 Eksakt Match (1:1):** Samme beløp, samme referanse/KID innen $\pm 1$ dag.
  * **R-02 Dato-toleranse (1:1):** Samme beløp med referanselikhet og dato innen $\pm 3$ dager.
  * **R-03 1:M Samleoppgjør:** Regex-gjenkjenning av batch-strenger (f.eks. Nets/Adyen) og subset-sum matching mot åpne kundefakturaer.
  * **R-04 Gebyrsplitt (1:1 m/avvik):** Isolerer bankgebyr (f.eks. 175 kr eller 2 % merchant fee) og klargjør spinn-off bilag.
* **Operasjon:** Klikk på **«Kjør Automatisk Avstemming»**. Klyngene flyttes umiddelbart til *Avstemte Poster*.

---

### Fane 2: Balansekontroll & Avstemmingsbro
* **Formål:** Dokumentere lovpålagt avstemming mellom bankens kontoutskrift og selskapets regnskap i henhold til god regnskapsskikk.
* **Balansebroens Matematikk:**
  $$\text{UB Bank} - \text{UB Hovedbok (ujustert)} = \text{Rådifferanse } (\Delta_{\text{rå}} = +137\,962{,}50\text{ kr})$$
  
  *Brojusteringer:*
  1. *Transittposter / Tidsavvik:* $+45\,000{,}00\text{ kr}$ (Bergen Marine innbetalt i bank 31.10, godskrevet reskontro 02.11).
  2. *Urealisert Valutakursendring (Agio):* $+48\,900{,}00\text{ kr}$ (Konsernavregning UK Ltd, kursavvik GBP/NOK).
  3. *Uførte bankgebyrer:* $-175{,}00\text{ kr}$ (DNB transaksjonskostnader).
  4. *Spinn-off pensjonspostering:* $-1\,000{,}00\text{ kr}$ (KLP premiejustering).
  
  $$\text{Netto Uforklart Avvik} = \Delta_{\text{netto}} = 0{,}00\text{ kr}$$
* **Operasjon:** Klikk **«Bekreft Tidsavvik underveis»** for å verifisere Bergen Marine-posten.

---

### Fane 3: Åpne Poster (Bank & ERP) med Betinget RAG
* **Formål:** Detaljert oppfølging av enkelttransaksjoner som ennå ikke er avstemt.
* **Funksjoner:**
  * **Delt Visning:** Bankposter til venstre, ERP-reskontroposter til høyre.
  * **Betinget RAG-formatering:**
    * <span style="color:#22c55e;">● Grønn (Lav risiko):</span> Normale transittposter med alder under 7 dager.
    * <span style="color:#eab308;">● Gul (Middels risiko):</span> Ubehandlede spinn-off poster eller alder 31–60 dager.
    * <span style="color:#ef4444;">● Rød (Høy/Kritisk risiko):</span> Poster med alder $>60$ dager, omtvistede krav, eller poster over 100 000 kr.
  * **RAG Filterknapper:** Filtrer på *Alle*, *Rød*, *Gul* eller *Grønn*.
  * **Manuell Matching:** Velg én eller flere bankposter og én eller flere ERP-poster med avkryssingsboksene. Når $\sum \text{Bank} = \sum \text{ERP}$, aktiveres **«Avstem valgte manuelt»**.
  * **AI Copilot Forslag:** Interaktive kort som presenterer komplekse matchingsforslag med tillitsscore og begrunnelse.

---

### Fane 4: Bilagsstudio & SAF-T Korreksjoner
* **Formål:** Kontrollere og bokføre genererte korreksjonsbilag før periodelåsing.
* **Bilagsoversikt:**
  * `JV-2026-10-01`: DNB gebyr (Debet 7770 / Kredit 1920: 175,00 kr).
  * `JV-2026-10-02`: KLP pensjonsjustering (Debet 5400 / Kredit 1920: 1 000,00 kr).
  * `JV-2026-10-03`: Agio UK Ltd (Debet 8160 / Kredit 1920: 48 900,00 kr).
* **Operasjon:** Klikk **«Bokfør alle spinn-off bilag»**. Bilagene merkes med SAF-T transaksjons-ID og oppdaterer hovedbokssaldoen direkte.

---

### Fane 5: Aldersfordeling & IFRS 9 Tapsavsetning
* **Formål:** Kredittrisikovurdering og tapsavsetning på åpne poster etter IFRS 9 ECL (Expected Credit Loss).
* **Matrise for Tapsavsetning:**
  | Tidsbøtte | Sats | Formål | Revisjonsrisiko |
  | :--- | :---: | :--- | :--- |
  | **0–30 dager** | 0 % | Løpende drift og ferske fakturaer | Lav (Grønn) |
  | **31–60 dager** | 2 % | Normale purreløp | Moderat (Gul) |
  | **61–90 dager** | 10 % | Forsinket betaling / eskalering | Høy (Rød) |
  | **90+ dager** | 40 % | Misligholdte fordringer / tvistesaker | Kritisk (Rød) |
* **WBS-Knytning:** Viser hvilke prosjekter (f.eks. `WBS-408 Kystvakt`) som belastes med tapsavsetningen.

---

### Fane 6: Avstemte Poster & Revisjonskjede
* **Formål:** Innsyn i alle lukkede transaksjonsklynger for perioden.
* **Funksjoner:**
  * Filtrering på regelkode (`R-01`, `R-02`, `R-03`, `R-04`, `R-AI-AGENT`, `R-MAN`).
  * **Ekspanderbar Klyngevisning:** Klikk på en klynge for å se de underliggende bank- og ERP-linjene.
  * **Opphev Avstemming (Rollback):** Frigjør transaksjonene tilbake til åpne poster. Handlingen logges i den kryptografiske revisjonskjeden med tidsstempel og bruker-ID.
  * **DuckDB Integrasjon:** Direkte kobling mot `v_reconciliation_summary`.

---

### Fane 7: CFO-Rapport & Ledelsessammendrag
* **Formål:** Styringsrapport for økonomiledelsen med full balansekontroll.
* **Nøkkelkomponenter:**
  * **Sammendragstabell:** Fullstendig bro fra Bank UB til Bokført UB med revisorkommentarer.
  * **Top 5 Vesentlige Åpne Poster:** Tabell med beløp, motpart, WBS-prosjekt, alder og forklaring.
  * **4-Øyne Godkjenning:**
    1. *Controller Kvalitetssikring:* Frank Ellingsen signerer på at avstemmingsbroen er dokumentert.
    2. *CFO Låsing:* Kari Nordmann låser perioden for etterposteringer.

---

### Fane 8: Revisjon & Revisorpakke (ISA 500)
* **Formål:** Tilrettelegge dokumentasjon for ekstern revisor (PwC/KPMG/EY/Deloitte) i henhold til revisjonsstandardene.
* **Innhold:**
  * **ISA 500 Cut-off Test:** Etterfølgende innbetalinger og kontroll av at inntekter/kostnader tilhører riktig regnskapsperiode.
  * **Kryptografisk Revisjonskjede:** Sanntidslogg der hver hendelse (`PRE_MATCH`, `SPIN_OFF`, `MANUAL_OVERRIDE`, `SIGN_OFF`) forsegles med SHA-256 hash koblet til forrige blokk.
  * **Ett-klikks Eksport:** Generer komplett revisjonspakke (ZIP med SAF-T XML, bankutskrifter, avstemmingsprotokoll og SHA-256 verifikasjonsbevis).

---

## 5. DuckDB Analytisk Database & Live Spørringer

CLOSE-AI benytter **DuckDB 1.5.3** som en embedded, høyytelses analytisk motor. Databasen lagres lokalt i prosjektets `data/`-mappe:

```
c:\Users\frank\Desktop\AI Financial Close Room\data\
 ├── reconciliation.duckdb               # Primærdatabase med begge tabeller og views
 ├── reconciled_transactions.duckdb      # Satellitt for avstemte transaksjoner
 └── unreconciled_transactions.duckdb    # Satellitt for uavstemte / åpne poster
```

### Tabeller & Datastruktur
1. **`reconciled_transactions`**:
   * Inneholder `reconciliation_id`, `match_group_id`, `match_type`, `gross_amount_nok`, `fee_deduction_nok`, `audit_hash`, `matched_by` og `matched_at`.
2. **`unreconciled_transactions`**:
   * Inneholder `item_id`, `source_system`, `amount_nok`, `transaction_date`, `project_id`, `wbs_code`, `rag_status`, `age_days`, `aging_bucket` og `provision_nok`.

### Fortløpende ACID-oppdatering
Når en transaksjon avstemmes i applikasjonen eller i Python-pipelinen, utføres en atomisk transaksjon:
```sql
BEGIN TRANSACTION;
INSERT INTO reconciled_transactions (...) VALUES (...);
UPDATE unreconciled_transactions SET status = 'RECONCILED', updated_at = CURRENT_TIMESTAMP WHERE item_id = ?;
COMMIT;
```

### Nyttige SQL-spørringer for Controllere
Du kan åpne `data/reconciliation.duckdb` direkte via Python, DBeaver, Power BI eller Excel Power Query:

```python
import duckdb

con = duckdb.connect("data/reconciliation.duckdb")

# 1. Hent WBS-eksponering for prosjektmøtet
df_wbs = con.execute("SELECT * FROM v_wbs_open_exposure").df()
print(df_wbs)

# 2. Hent IFRS 9 tapsavsetning
df_aging = con.execute("SELECT * FROM v_unreconciled_aging").df()
print(df_aging)

con.close()
```

---

## 6. Pop-Up Chatbot & Copilot Assistent

Nede i høyre hjørne finner du den flytende **Close-AI Assistenten**. Klikk på ikonet for å åpne samtaleskuffen.

```
       ┌───────────────────────────────────────────────────────┐
       │ 🤖 Close-AI Assistent                               ✕ │
       ├───────────────────────────────────────────────────────┤
       │ Modus: [ Bruker / Controller ] [ Superbruker / Admin ]│
       ├───────────────────────────────────────────────────────┤
       │ [ Hvorfor diff på 1920? ] [ Hjelp med Bergen Marine ] │
       │ [ Vis DuckDB status ]     [ Bokfør alle spinn-off ]   │
       ├───────────────────────────────────────────────────────┤
       │ 💬 Frank: Hvorfor er konto 1920 ubalansert?           │
       │ 🤖 Bot: Rådifferansen er 137 962,50 kr. Balansebroen  │
       │    lukkes med: Bergen Marine (+45k), UK agio (+48,9k),│
       │    DNB gebyr (-175 kr) og KLP (-1 000 kr).            │
       │    Netto differanse etter justering er 0,00 kr!       │
       │                                                       │
       │    [ Åpne Balansekontroll ] [ Bekreft Tidsavvik ]     │
       └───────────────────────────────────────────────────────┘
```

### Assistentens To Moduser:
1. **Bruker / Controller Modus**:
   * Hjelp med ubalanse på 1920 og forklaring av broelementene.
   * Veiledning for å bekrefte tidsavvik (Bergen Marine).
   * Ett-klikks kjøring av autoløp og bokføring av bilag.
   * Status for 4-øyne signering og revisorpakke.
2. **Superbruker / Admin Modus**:
   * Importmaler for Topp 5 ERP (Visma, Business Central, Xledger, Tripletex, SAP).
   * Internasjonale bankformater (CAMT.053, MT940, BAI2 sent-format).
   * Oppsett av nye konti med IB-validering.
   * Konfigurasjon av øresavrundingsregler ($\le 5\text{ NOK}$).
   * DuckDB SQL-spørringer og databasestatus.

---

## 7. Superbruker & Systemansvarlig Guide

### Sette opp ny balansekonto med IB
Ved opprettelse av nye drifts- eller valutakonti (f.eks. `1921 Driftskonto USD`):
1. **Opprett i Kontoplanen:** Registrer kontonummer, kontonavn, valuta og tilknyttet IBAN.
2. **Registrer Inngående Balanse (IB):** Tast inn IB per periodestart for både Bank og Hovedbok.
3. **Validering av Historiske Åpne Poster:**
   Systemet håndhever en streng valideringsregel:
   $$\text{IB Hovedbok} + \sum (\text{Importerte Åpne Poster}) = \text{IB Bank}$$
   Kontoen kan ikke settes i aktiv driftsstatus før denne likningen er i balanse.

### Konfigurasjon av Øresavrunding ($\le 5\text{ NOK}$)
Små avrundingsdifferanser under $\le 5\text{ NOK}$ (eller opptil $10\text{ NOK}$) kan automatiseres:
* **Regelkode:** `R-TOLERANCE-AUTO`
* **Kontering:**
  * **Debet/Kredit:** `Konto 7799 Fradragsberettigede andre driftskostnader (Øreavrunding)`
  * **Motkonto:** `Konto 1920 Driftskonto NOK`
* Revisorattest genereres automatisk i revisjonskjeden.

### Integrasjon mot Topp 5 Norske ERP-Systemer
* **Microsoft Dynamics 365 Business Central:** OData v4 mot Page 21 (`Customer Ledger Entries`) og Page 20 (`General Ledger Entries`).
* **Visma.net / Visma Business NXT:** REST API mot `/controller/api/v1/customerledgerdocument` koblet til Visma AutoPay.
* **Xledger:** GraphQL API mot `glTransactions` med 5-dimensjonal kontering (Konto, Reskontro, Prosjekt/WBS, Avdeling, Aktivitet).
* **Tripletex:** Swagger REST JSON API mot `/ledger/voucher` og `/ledger/openPostings`.
* **SAP S/4HANA:** BAPI-grensesnitt (`BAPI_ACC_DOCUMENT_POST`) eller periodisk SAP SAF-T XML dump.

---

## 8. Prosjektcontrolling & WBS-Oppfølging (EAC/ETC)

For prosjektcontrollere i engineering- og forsvarssektoren (Umoe Mandal-kontekst) gir CLOSE-AI direkte støtte for prosjektoppfølging:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROSJEKTCONTROLLING SAMMENHENG                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  WBS Element (f.eks. WBS-408 Kystvakt Hull Structure)                       │
│    ├── Pådratte faktiske kostnader (ACWP) via Hovedbok 1920                 │
│    ├── Åpne uavstemte leverandørfakturaer (Potensiell EAC-risiko)           │
│    ├── IFRS 9 Tapsavsetning på omtvistede poster                            │
│    └── Oppdatert Estimate at Completion (EAC = ACWP + ETC + Uavstemt Avvik) │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **WBS-Filter i Headeren:** Isolerer alle 8 faner til ett spesifikt prosjekt.
* **Tapsavsetning mot Prosjektmargin:** Uavstemte krav over 90 dager avsettes med 40 %, noe som automatisk synliggjøres i prosjektets EAC-prognose.
* **Ingen "Svarte Hull":** Hver eneste uavstemt banktransaksjon må tagges mot et WBS-element før CFO kan låse perioden.

---

## 9. Feilsøking & Hurtighandlinger

| Symptom / Feilmelding | Årsak | Løsning |
| :--- | :--- | :--- |
| **Balansebro har avvik ($\Delta \ne 0$)** | Ubekreftet transittpost eller ubokført spinn-off bilag. | 1. Gå til Fane 2 og bekreft Bergen Marine.<br>2. Gå til Fane 4 og klikk «Bokfør alle spinn-off bilag». |
| **CFO-godkjenning er deaktivert** | Controller har ikke signert, eller avviket er ikke 0,00 kr. | Signer først som Controller Frank Ellingsen i Fane 7. |
| **Manuell match-knapp er grået ut** | Summen av valgte banklinjer er ikke lik summen av valgte ERP-linjer. | Kontroller at differansen mellom markerte linjer er akkurat 0,00 kr. Ved gebyravvik, bruk AI Copilot. |
| **DuckDB database låst (Lock error)** | Databasen er åpen i skrivemodus i et annet program (f.eks. Python-sesjon). | Lukk eksterne DuckDB-koblinger eller koble til med `read_only=True`. |
| **Ønsker å teste på nytt** | Behov for å tilbakestille data til periodestart. | Klikk på **«Tilbakestill periode»** i topplinjen. |

---

*Manualen er generert for CLOSE-AI v2026.10 — Nordic Engineering Projects AS.*
