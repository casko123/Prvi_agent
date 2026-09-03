"""
Korak 1 dnevnega agenta: pripravi sporočilo in pošlji v potrditev
====================================================================

Zažene se enkrat dnevno (glej 1-dnevna-generacija.yml).

1. Sestavi celotno besedilo sporočila za ženo (fiksen uvod + fiksen
   motivacijski stavek - brez LLM, besedilo je vedno enako).
2. To besedilo shrani v pending/pending.json (čaka na potrditev).
3. Pošlje potrditveno e-pošto nazaj na isti (tvoj) naslov.

Sporočilo ženi NE bo poslano, dokler ga ročno ne potrdiš z odgovorom
"POTRJUJEM" - to preveri ločena skripta (preveri_in_poslji_koncno.py).
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path

PENDING_POT = Path("pending/pending.json")

# Statični motivacijski stavek - uredi po želji. Besedilo se ne
# spreminja iz dneva v dan.
MOTIVACIJSKI_STAVEK = (
    "Vsak dan znova dokazuješ, kako močna in sposobna si - "
    "verjamem vate."
)


def sestavi_sporocilo() -> str:
    return (
        "Pozdravljena,\n\n"
        "sem agent, ki ga je pripravil tvoj mož. Z njegovim dovoljenjem "
        "ti pošiljam enostavno motivacijsko sporočilo.\n\n"
        f"{MOTIVACIJSKI_STAVEK}\n\n"
        "Lep pozdrav,\n"
        "Tvoj agent"
    )


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
    posiljatelj = os.environ["GMAIL_NASLOV"]
    geslo = os.environ["GMAIL_APP_GESLO"]

    koncno_sporocilo = sestavi_sporocilo()
    danes = datetime.now(timezone.utc).strftime("%d.%m.%Y")

    # Shrani osnutek, da ga druga skripta lahko kasneje pošlje
    PENDING_POT.parent.mkdir(parents=True, exist_ok=True)
    PENDING_POT.write_text(
        json.dumps(
            {
                "ustvarjeno_utc": datetime.now(timezone.utc).isoformat(),
                "sporocilo": koncno_sporocilo,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # Pošlji potrditveno e-pošto nazaj nase
    zadeva = f"Potrditev: dnevno motivacijsko sporočilo - {danes}"
    vsebina_potrditve = (
        "Agent je pripravil naslednje sporočilo za Heleno:\n\n"
        "----------------------------------------\n"
        f"{koncno_sporocilo}\n"
        "----------------------------------------\n\n"
        'Če se strinjaš, ODGOVORI na to sporočilo z eno samo besedo: '
        "POTRJUJEM\n\n"
        "Če ne odgovoriš, sporočilo Heleni ne bo poslano.\n"
        "(Preverjanje odgovora poteka približno vsakih 15 minut.)"
    )
    poslji_email(posiljatelj, geslo, posiljatelj, zadeva, vsebina_potrditve)

    print(f"Osnutek pripravljen in potrditev poslana na {posiljatelj}.")


if __name__ == "__main__":
    main()
