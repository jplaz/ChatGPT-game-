#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()

# Only change user-facing quoted strings. This deliberately leaves C identifiers,
# map IDs, script labels, mechanics, graphics paths, and the Crossroads engine intact.
DISPLAY_REPLACEMENTS = [
    ("POKéMON CENTER", "HEALER'S HALL"),
    ("Pokémon Center", "Healer's Hall"),
    ("POKéMON MART", "MARKET HALL"),
    ("Pokémon Mart", "Market Hall"),
    ("POKéMON LAB", "MAESTER HALL"),
    ("Pokémon Lab", "Maester Hall"),
    ("POKéMON LEAGUE", "GREAT COUNCIL"),
    ("Pokémon League", "Great Council"),
    ("POKéDEX", "BESTIARY"),
    ("Pokédex", "Bestiary"),
    ("POKé BALLS", "BIND ORBS"),
    ("Poké Balls", "Bind Orbs"),
    ("POKé BALL", "BIND ORB"),
    ("Poké Ball", "Bind Orb"),
    ("TEAM AQUA", "IRONBORN"),
    ("Team Aqua", "Ironborn"),
    ("TEAM MAGMA", "BOLTONS"),
    ("Team Magma", "Boltons"),
    ("TEAM ROCKET", "GOLD CLOAKS"),
    ("Team Rocket", "Gold Cloaks"),
    ("GYM LEADER", "HOUSE LORD"),
    ("Gym Leader", "House Lord"),
    ("ELITE FOUR", "WAR COUNCIL"),
    ("Elite Four", "War Council"),
    ("CHAMPION", "RULER"),
    ("Champion", "Ruler"),
    ("TRAINER", "HANDLER"),
    ("Trainer", "Handler"),
    ("PROFESSOR", "MAESTER"),
    ("Professor", "Maester"),
    ("BADGES", "SIGILS"),
    ("Badges", "Sigils"),
    ("BADGE", "SIGIL"),
    ("Badge", "Sigil"),
    ("GYMS", "KEEPS"),
    ("Gyms", "Keeps"),
    ("GYM", "KEEP"),
    ("Gym", "Keep"),
    ("POKéMON", "BEAST"),
    ("Pokémon", "Beast"),
    ("pokemon", "beast"),
    ("HOENN", "THE NORTH"),
    ("Hoenn", "the North"),
    ("KANTO", "THE SOUTH"),
    ("Kanto", "the South"),
    ("SEVII", "NARROW SEA"),
    ("Sevii", "Narrow Sea"),
    ("LITTLEROOT", "WINTERFELL"),
    ("Littleroot", "Winterfell"),
    ("OLDALE", "WINTER TOWN"),
    ("Oldale", "Winter Town"),
    ("PETALBURG", "WHITE HARBOR"),
    ("Petalburg", "White Harbor"),
    ("RUSTBORO", "DREADFORT"),
    ("Rustboro", "Dreadfort"),
    ("DEWFORD", "BEAR ISLAND"),
    ("Dewford", "Bear Island"),
    ("SLATEPORT", "SEAGARD"),
    ("Slateport", "Seagard"),
    ("MAUVILLE", "RIVERRUN"),
    ("Mauville", "Riverrun"),
    ("VERDANTURF", "THE TWINS"),
    ("Verdanturf", "the Twins"),
    ("FALLARBOR", "MOAT CAILIN"),
    ("Fallarbor", "Moat Cailin"),
    ("LAVARIDGE", "HARRENHAL"),
    ("Lavaridge", "Harrenhal"),
    ("FORTREE", "THE EYRIE"),
    ("Fortree", "the Eyrie"),
    ("LILYCOVE", "KING'S LANDING"),
    ("Lilycove", "King's Landing"),
    ("MOSSDEEP", "DRAGONSTONE"),
    ("Mossdeep", "Dragonstone"),
    ("SOOTOPOLIS", "HIGHGARDEN"),
    ("Sootopolis", "Highgarden"),
    ("PACIFIDLOG", "PYKE"),
    ("Pacifidlog", "Pyke"),
    ("EVER GRANDE", "THE RED KEEP"),
    ("Ever Grande", "the Red Keep"),
    ("PALLET", "STARFALL"),
    ("Pallet", "Starfall"),
    ("VIRIDIAN", "SUNSPEAR"),
    ("Viridian", "Sunspear"),
    ("PEWTER", "CASTERLY ROCK"),
    ("Pewter", "Casterly Rock"),
    ("CERULEAN", "GULLTOWN"),
    ("Cerulean", "Gulltown"),
    ("VERMILION", "OLDTOWN"),
    ("Vermilion", "Oldtown"),
    ("LAVENDER", "CASTLE BLACK"),
    ("Lavender", "Castle Black"),
    ("CELADON", "HIGHGARDEN"),
    ("Celadon", "Highgarden"),
    ("FUCHSIA", "STORM'S END"),
    ("Fuchsia", "Storm's End"),
    ("SAFFRON", "KING'S LANDING"),
    ("Saffron", "King's Landing"),
    ("CINNABAR", "DRAGONSTONE"),
    ("Cinnabar", "Dragonstone"),
    ("INDIGO PLATEAU", "IRON THRONE"),
    ("Indigo Plateau", "Iron Throne"),
]

# More atmospheric exact phrases, applied before the broad terminology pass.
SPECIAL_REPLACEMENTS = {
    "data/text/birch_speech.inc": [
        ("Hi! Sorry to keep you waiting!", "Welcome, traveler."),
        ("Welcome to the world of POKéMON!", "Welcome to the Seven Kingdoms!"),
        ("My name is BIRCH.", "I am MAESTER LUWIN."),
        ("This is what we call a “POKéMON.”", "This is one of the realm's beasts."),
        ("Your very own adventure is about", "Your own song of ice and fire is"),
        ("to unfold.", "about to unfold."),
        ("Take courage, and leap into the", "Take courage. The realm remembers"),
        ("world of POKéMON where dreams,", "every oath, victory, and betrayal."),
        ("adventure, and friendships await!", "Choose what kind of ruler you become!"),
    ],
    "data/text/new_game_intro_frlg.inc": [
        ("Welcome to the world of POKéMON!", "Welcome to the Seven Kingdoms!"),
        ("My name is OAK.", "I am MAESTER AEMON."),
        ("In the world which you are about to", "In the realm you are about to enter,"),
        ("enter, you will embark on a grand", "you will embark on a long and dangerous"),
        ("adventure with you as the hero.", "adventure with your name at its center."),
        ("New paths will open to you by helping", "New roads open through favors, oaths,"),
        ("people in need, overcoming challenges,", "victories, alliances, and hard choices,"),
        ("and solving mysteries.", "and every choice can shape the realm."),
        ("Be brave and keep pushing on.", "Be brave. Winter is never far away."),
    ],
}


def replace_in_quoted_literals(text: str) -> str:
    # C/asm string literal matcher. It intentionally ignores identifiers and comments
    # except for quoted text inside them, where these tokens almost never appear.
    pattern = re.compile(r'"(?:\\.|[^"\\])*"')

    def repl(match: re.Match[str]) -> str:
        s = match.group(0)
        for old, new in DISPLAY_REPLACEMENTS:
            s = s.replace(old, new)
        return s

    return pattern.sub(repl, text)


def patch_text_file(path: Path) -> None:
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    text = original
    rel = path.relative_to(ROOT).as_posix()
    for old, new in SPECIAL_REPLACEMENTS.get(rel, []):
        text = text.replace(old, new)
    text = replace_in_quoted_literals(text)
    if text != original:
        path.write_text(text, encoding="utf-8")


# Patch player-facing source/script text without touching graphics or binary assets.
for base in (ROOT / "data", ROOT / "src", ROOT / "include"):
    if not base.exists():
        continue
    for path in base.rglob("*"):
        if path.is_file() and path.suffix in {".inc", ".c", ".h", ".s"}:
            patch_text_file(path)

# The region-map display names are JSON values, so change only the "name" field
# while preserving IDs and all map wiring.
region_file = ROOT / "src/data/region_map/region_map_sections.json"
if region_file.exists():
    data = json.loads(region_file.read_text(encoding="utf-8"))
    names = {
        "MAPSEC_LITTLEROOT_TOWN": "WINTERFELL",
        "MAPSEC_OLDALE_TOWN": "WINTER TOWN",
        "MAPSEC_DEWFORD_TOWN": "BEAR ISLAND",
        "MAPSEC_LAVARIDGE_TOWN": "HARRENHAL",
        "MAPSEC_FALLARBOR_TOWN": "MOAT CAILIN",
        "MAPSEC_VERDANTURF_TOWN": "THE TWINS",
        "MAPSEC_PACIFIDLOG_TOWN": "PYKE",
        "MAPSEC_PETALBURG_CITY": "WHITE HARBOR",
        "MAPSEC_SLATEPORT_CITY": "SEAGARD",
        "MAPSEC_MAUVILLE_CITY": "RIVERRUN",
        "MAPSEC_RUSTBORO_CITY": "DREADFORT",
        "MAPSEC_FORTREE_CITY": "THE EYRIE",
        "MAPSEC_LILYCOVE_CITY": "KING'S LANDING",
        "MAPSEC_MOSSDEEP_CITY": "DRAGONSTONE",
        "MAPSEC_SOOTOPOLIS_CITY": "HIGHGARDEN",
        "MAPSEC_EVER_GRANDE_CITY": "THE RED KEEP",
        "MAPSEC_PALLET_TOWN": "STARFALL",
        "MAPSEC_VIRIDIAN_CITY": "SUNSPEAR",
        "MAPSEC_PEWTER_CITY": "CASTERLY ROCK",
        "MAPSEC_CERULEAN_CITY": "GULLTOWN",
        "MAPSEC_VERMILION_CITY": "OLDTOWN",
        "MAPSEC_LAVENDER_TOWN": "CASTLE BLACK",
        "MAPSEC_CELADON_CITY": "HIGHGARDEN",
        "MAPSEC_FUCHSIA_CITY": "STORM'S END",
        "MAPSEC_SAFFRON_CITY": "KING'S LANDING",
        "MAPSEC_CINNABAR_ISLAND": "DRAGONSTONE",
        "MAPSEC_INDIGO_PLATEAU": "IRON THRONE",
        "MAPSEC_ROUTE_101": "THE KINGSROAD",
        "MAPSEC_ROUTE_102": "WOLFSWOOD",
        "MAPSEC_ROUTE_103": "BARROWLANDS",
        "MAPSEC_ROUTE_104": "STONY SHORE",
        "MAPSEC_ROUTE_105": "SUNSET SEA",
        "MAPSEC_ROUTE_106": "CAPE KRAKEN",
        "MAPSEC_ROUTE_107": "IRONMANS BAY",
        "MAPSEC_ROUTE_108": "THE BITE",
        "MAPSEC_ROUTE_109": "WHITE KNIFE",
        "MAPSEC_ROUTE_110": "RIVER ROAD",
        "MAPSEC_ROUTE_111": "GOLDROAD",
        "MAPSEC_ROUTE_112": "HIGH ROAD",
        "MAPSEC_ROUTE_113": "KINGSWOOD",
        "MAPSEC_ROUTE_114": "TRIDENT ROAD",
        "MAPSEC_ROUTE_115": "RED FORK",
        "MAPSEC_ROUTE_116": "BLUE FORK",
        "MAPSEC_ROUTE_117": "GREEN FORK",
        "MAPSEC_ROUTE_118": "BLACKWATER",
        "MAPSEC_ROUTE_119": "VALE ROAD",
        "MAPSEC_ROUTE_120": "MOUNTAIN PASS",
        "MAPSEC_ROUTE_121": "ROSE ROAD",
        "MAPSEC_ROUTE_122": "GODS EYE",
        "MAPSEC_ROUTE_123": "STORM ROAD",
        "MAPSEC_ROUTE_124": "NARROW SEA",
        "MAPSEC_ROUTE_125": "SHIPBREAKER",
        "MAPSEC_ROUTE_126": "DRAGON BAY",
        "MAPSEC_ROUTE_127": "STEPSTONES",
        "MAPSEC_ROUTE_128": "DORNISH SEA",
        "MAPSEC_ROUTE_129": "SUMMER SEA",
        "MAPSEC_ROUTE_130": "IRON COAST",
        "MAPSEC_ROUTE_131": "ARBOR SEA",
        "MAPSEC_ROUTE_132": "SALT ROAD",
        "MAPSEC_ROUTE_133": "BONEWAY",
        "MAPSEC_ROUTE_134": "PRINCES PASS",
    }
    for section in data.get("map_sections", []):
        new_name = names.get(section.get("id"))
        if new_name:
            section["name"] = new_name
    region_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

print("Applied Westeros display-text and map-name overlay to Crossroads source.")
