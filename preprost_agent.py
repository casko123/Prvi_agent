"""
PREPROST AGENT — primer s stopnjami avtonomije
================================================

Namen: pokazati, kako agent razvrsti akcije v tri razrede in kdaj
vpraša uporabnika za potrditev, namesto da vse "poganja" naravnost.

Scenarij: agent dobi seznam opravil in za vsako presodi, ali jo lahko
izvede sam, ali mora vprašati uporabnika, ali je sploh ne sme izvesti.

To NI prava LLM-integracija (ni klica na API) — je čisti "okostje"
odločitvene logike, ki jo lahko kasneje priklopiš na pravi LLM
(npr. Claude API), da namesto pravil odloča model sam.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Callable


class Avtonomija(Enum):
    PROSTO = "prosto"                  # agent izvede sam, brez vprašanja
    POTRDITEV = "potrebna_potrditev"   # agent vpraša uporabnika, čaka odgovor
    PREPOVEDANO = "prepovedano"        # agent tega nikoli ne naredi


@dataclass
class Akcija:
    ime: str
    opis: str
    stopnja: Avtonomija
    izvedi: Callable[[], str]  # funkcija, ki dejansko izvede akcijo


class Agent:
    def __init__(self, ime: str):
        self.ime = ime
        self.dnevnik = []  # zapisuje, kaj se je zgodilo (za sledljivost)

    def _zapisi(self, sporocilo: str):
        self.dnevnik.append(sporocilo)
        print(sporocilo)

    def obravnavaj(self, akcija: Akcija):
        """
        Osrednja odločitvena točka agenta.
        Tu se zgodi presoja: ali izvedem sam, vprašam, ali zavrnem.
        """
        if akcija.stopnja == Avtonomija.PROSTO:
            self._zapisi(f"[IZVAJAM SAMODEJNO] {akcija.opis}")
            rezultat = akcija.izvedi()
            self._zapisi(f"  -> rezultat: {rezultat}")

        elif akcija.stopnja == Avtonomija.POTRDITEV:
            self._zapisi(f"[ČAKAM POTRDITEV] {akcija.opis}")
            odgovor = input(f"  Ali naj izvedem to akcijo? (da/ne): ").strip().lower()
            if odgovor == "da":
                rezultat = akcija.izvedi()
                self._zapisi(f"  -> potrjeno, rezultat: {rezultat}")
            else:
                self._zapisi("  -> uporabnik je zavrnil, akcija preskočena")

        elif akcija.stopnja == Avtonomija.PREPOVEDANO:
            self._zapisi(
                f"[ZAVRNJENO] '{akcija.opis}' spada med prepovedane akcije. "
                f"To mora uporabnik izvesti sam."
            )

        else:
            raise ValueError("Neznana stopnja avtonomije")


# --------------------------------------------------------------------
# PRAKTIČEN PRIMER: agent za organizacijo opravil
# --------------------------------------------------------------------

def preberi_datoteko():
    return "Prebral seznam 12 opravil iz todo.txt"

def poslji_email_povzetka():
    return "E-pošta s povzetkom tedna poslana na sasa@example.com"

def izbrisi_stare_zapiske():
    return "Trajno izbrisanih 40 starih zapiskov iz arhiva"

def izracunaj_statistiko():
    return "Statistika: 8 opravljenih, 4 v teku"


if __name__ == "__main__":
    agent = Agent("Organizator opravil")

    seznam_akcij = [
        Akcija(
            ime="branje",
            opis="Preberi seznam opravil iz datoteke",
            stopnja=Avtonomija.PROSTO,       # branje je nepovratno neškodljivo
            izvedi=preberi_datoteko,
        ),
        Akcija(
            ime="statistika",
            opis="Izračunaj statistiko opravljenih nalog",
            stopnja=Avtonomija.PROSTO,       # samo izračun, brez stranskih učinkov
            izvedi=izracunaj_statistiko,
        ),
        Akcija(
            ime="email",
            opis="Pošlji tedenski povzetek po e-pošti",
            stopnja=Avtonomija.POTRDITEV,    # pošiljanje = akcija navzven, vpliva na druge
            izvedi=poslji_email_povzetka,
        ),
        Akcija(
            ime="brisanje",
            opis="Trajno izbriši stare zapiske iz arhiva",
            stopnja=Avtonomija.PREPOVEDANO,  # nepovratno brisanje = prepovedano
            izvedi=izbrisi_stare_zapiske,
        ),
    ]

    for akcija in seznam_akcij:
        agent.obravnavaj(akcija)
        print()
