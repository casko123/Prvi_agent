# Motivacijski agent s potrditvijo — navodila za nastavitev

## Kako deluje (povzetek)

1. **Vsak dan ob nastavljeni uri** (delovni tok "1 - Pripravi sporočilo in
   pošlji potrditev"): agent sestavi celotno sporočilo iz fiksnega uvoda
   in fiksnega, nespremenljivega motivacijskega stavka (besedilo je
   vedno enako, brez LLM), in ga **shrani kot osnutek** v repozitoriju.
   Nato ti pošlje potrditveno e-pošto s celotnim besedilom na
   casser@gmail.com.

2. **Ti prebereš osnutek** in se odločiš:
   - Če se strinjaš: odgovori na e-pošto z eno samo besedo **POTRJUJEM**.
   - Če se ne strinjaš: ne naredi nič - sporočilo ne bo poslano.

3. **Vsakih ~15 minut** (delovni tok "2 - Preveri potrditev..."): agent
   preveri tvoj predal. Če najde odgovor s POTRJUJEM, pošlje pripravljeno
   sporočilo Heleni in izbriše osnutek (da se ne pošlje dvakrat).

Ker gre za pošiljanje sporočila drugi osebi, ta korak **namenoma ni
samodejen** - agent počaka na tvojo izrecno potrditev, preden karkoli
pošlje naprej. To je razlika med akcijo, ki je "prosta" (priprava
osnutka, pošiljanje tebi), in akcijo, ki "zahteva potrditev" (pošiljanje
drugi osebi v tvojem imenu).

## Korak 1: Po želji uredi besedilo sporočila

Motivacijski stavek je v datoteki `pripravi_in_poslji_potrditev.py`,
spremenljivka `MOTIVACIJSKI_STAVEK` na vrhu datoteke. Uredi ga po
želji - ostane enak vsak dan, dokler ga ročno ne spremeniš.

## Korak 2: Nastavi GitHub Secrets

V repozitoriju pojdi na **Settings → Secrets and variables → Actions**
in nastavi:

| Ime skrivnosti | Vrednost |
|---|---|
| `GMAIL_NASLOV` | casser@gmail.com |
| `GMAIL_APP_GESLO` | app geslo za casser@gmail.com |
| `ZENA_NASLOV` | helena.caserman@gmail.com |

`ANTHROPIC_API_KEY` ni več potreben - agent ne kliče nobenega zunanjega
LLM API-ja, zato ga lahko izbrišeš, če si ga prej dodal.

## Korak 3: Preveri, da Gmail dovoljuje IMAP

1. V Gmail nastavitvah (na računu casser@gmail.com) pojdi na
   **Settings → Forwarding and POP/IMAP**.
2. Preveri, da je **IMAP omogočen** (Enable IMAP). Brez tega skripta za
   preverjanje potrditve ne bo mogla prebrati predala.

## Korak 4: Naloži datoteke in preveri urnike

Naloži vse datoteke iz tega projekta v repozitorij, z ohranjeno strukturo
map (`.github/workflows/`, `pending/`). Prilagodi uro v
`1-dnevna-generacija.yml` (glej opombo o UTC iz prejšnjih navodil).

## Korak 5: Testiraj celoten cikel ročno

Oba delovna toka imata `workflow_dispatch`, torej ju lahko sprožiš ročno
v zavihku **Actions**:

1. Ročno zaženi **"1 - Pripravi sporočilo in pošlji potrditev"**.
2. Preveri, da si prejel potrditveno e-pošto z osnutkom.
3. Odgovori nanjo z besedo **POTRJUJEM**.
4. Ročno zaženi **"2 - Preveri potrditev in pošlji ženi"** (ali počakaj
   do 15 minut, da se zažene sam).
5. Preveri, da je Helena prejela sporočilo, in da je datoteka
   `pending/pending.json` iz repozitorija izginila.

## Pomembne opombe

- **Zakasnitev**: med tvojo potrditvijo in dejansko oddajo sporočila lahko
  mine do ~15-30 minut (odvisno od obremenjenosti GitHub Actions).
- **En osnutek naenkrat**: sistem trenutno podpira samo en čakajoč osnutek.
  Če pozabiš potrditi enega dne, ga naslednji dan povozi nov osnutek
  (staro sporočilo se izgubi, ne pošlje se dvojno).
- **Neaktivnost repozitorija**: GitHub samodejno onemogoči urnike (cron)
  v repozitorijih, ki so 60 dni neaktivni. Če agent nenadoma neha delovati,
  preveri zavihek Actions in urnik ponovno omogoči.
- **Varnost**: nihče razen tebe nima dostopa do skrivnosti (Secrets), in
  agent ne pošlje ničesar Heleni brez tvoje izrecne potrditve po e-pošti.
