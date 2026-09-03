"""
Korak 2 dnevnega agenta: preveri potrditev in po potrebi pošlji ženi
======================================================================

Zažene se pogosto (npr. vsakih 15 minut, glej preveri-potrditev.yml).

1. Če ni čakajočega osnutka (pending/pending.json ne obstaja), konča brez akcije.
2. Prebere predal (IMAP) in išče NEPREBRANA sporočila, ki vsebujejo besedo
   POTRJUJEM in so prispela po tem, ko je bil osnutek ustvarjen.
3. Če najde potrditev: pošlje shranjeno sporočilo ženi in izbriše osnutek,
   da se sporočilo ne pošlje dvakrat.
4. Če potrditve še ni: ne naredi nič in počaka na naslednji zagon.
"""

import os
import json
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime
from pathlib import Path

PENDING_POT = Path("pending/pending.json")
KLJUCNA_BESEDA = "POTRJUJEM"


def preberi_besedilo_sporocila(msg) -> str:
    if msg.is_multipart():
        deli = []
        for del_ in msg.walk():
            if del_.get_content_type() == "text/plain":
                deli.append(
                    del_.get_payload(decode=True).decode(errors="ignore")
                )
        return "\n".join(deli)
    return msg.get_payload(decode=True).decode(errors="ignore")


def obstaja_potrditev(naslov, geslo, ustvarjeno_od) -> bool:
    """Preveri predal in vrne True, če je prispel odgovor s ključno besedo."""
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(naslov, geslo)
    imap.select("INBOX")

    # Poišči nepreb rana sporočila
    status, podatki = imap.search(None, "UNSEEN")
    if status != "OK":
        imap.logout()
        return False

    id_sporocil = podatki[0].split()
    najdena_potrditev = False

    for msg_id in id_sporocil:
        status, podatki_msg = imap.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        msg = email.message_from_bytes(podatki_msg[0][1])
        besedilo = preberi_besedilo_sporocila(msg)

        # Preveri, ali je prispelo po tem, ko je bil osnutek ustvarjen,
        # in ali vsebuje ključno besedo
        datum_prejema = email.utils.parsedate_to_datetime(msg["Date"])
        if (
            KLJUCNA_BESEDA.lower() in besedilo.lower()
            and datum_prejema.timestamp() >= ustvarjeno_od.timestamp()
        ):
            najdena_potrditev = True
            # Označi kot prebrano, da se ne obravnava znova
            imap.store(msg_id, "+FLAGS", "\\Seen")

    imap.logout()
    return najdena_potrditev


def poslji_email(posiljatelj, geslo, prejemnik, zadeva, vsebina):
    sporocilo = MIMEMultipart()
    sporocilo["From"] = posiljatelj
    sporocilo["To"] = prejemnik
    sporocilo["Subject"] = zadeva
    sporocilo.attach(MIMEText(vsebina, "plain", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(posiljatelj, geslo)
        server.send_message(sporocilo)


def main():
    if not PENDING_POT.exists():
        print("Ni čakajočega osnutka - nič za narediti.")
        return

    podatki_osnutka = json.loads(PENDING_POT.read_text(encoding="utf-8"))
    ustvarjeno_od = datetime.fromisoformat(podatki_osnutka["ustvarjeno_utc"])

    posiljatelj = os.environ["GMAIL_NASLOV"]
    geslo = os.environ["GMAIL_APP_GESLO"]
    zena_naslov = os.environ["ZENA_NASLOV"]

    if obstaja_potrditev(posiljatelj, geslo, ustvarjeno_od):
        poslji_email(
            posiljatelj,
            geslo,
            zena_naslov,
            "Zate",
            podatki_osnutka["sporocilo"],
        )
        PENDING_POT.unlink()  # izbriši osnutek, da se ne pošlje dvakrat
        print(f"Potrditev najdena - sporočilo poslano na {zena_naslov}.")
    else:
        print("Potrditev še ni prispela - čakam na naslednje preverjanje.")


if __name__ == "__main__":
    main()
