"""
Data definitions and domain knowledge for the Murder Mystery Logic Solver.
Defines suspects, locations, weapons, and narrative flavor text.
"""
from typing import Dict, List, Any

# Suspects with rich noir backstories
SUSPECTS: Dict[str, Dict[str, str]] = {
    "Ravi": {
        "title": "The Disgraced Antiquities Dealer",
        "description": "An obsessed collector haunted by counterfeit scandals, gambling debts, and whispered black-market deals.",
        "motive": "Facing imminent bankruptcy after the victim threatened to expose his forged relics to Scotland Yard.",
        "color": "#E63946"  # Crimson
    },
    "Meera": {
        "title": "The Calculating Chemist",
        "description": "A brilliant toxicologist whose experimental synthesized compounds mysteriously vanished from the research laboratory.",
        "motive": "The victim had stolen her breakthrough research patent and planned to sell it to an overseas syndicate.",
        "color": "#457B9D"  # Slate Blue
    },
    "Kabir": {
        "title": "The Ruthless Tycoon",
        "description": "A predatory corporate magnate who views human lives as balance sheet line items to be liquidated.",
        "motive": "The victim held voting majority shares that blocked his multi-million pound hostile estate acquisition.",
        "color": "#D4AF37"  # Vintage Gold
    },
    "Zara": {
        "title": "The Secretive Novelist",
        "description": "A reclusive crime author whose unpublished manuscript details the exact sequence of tonight's demise.",
        "motive": "The victim possessed personal correspondence that would destroy her identity and career forever.",
        "color": "#8338EC"  # Royal Purple
    },
    "Dev": {
        "title": "The Disgruntled Butler",
        "description": "The silent shadow of the manor who served for thirty bitter years, knowing every hidden passage and locked safe.",
        "motive": "Discovered that the revised will cast him out into the London winter without a single farthing.",
        "color": "#2A9D8F"  # Dark Teal
    }
}

# Crime scenes / Locations
LOCATIONS: Dict[str, Dict[str, str]] = {
    "Library": {
        "description": "Lined with towering mahogany shelves, heavy velvet drapes, and the scent of aged parchment.",
        "icon": "📚"
    },
    "Kitchen": {
        "description": "Gleaming cast-iron pans, chilled marble slabs, and an eerie silence beneath the pantry lanterns.",
        "icon": "🍳"
    },
    "Garden": {
        "description": "Thick mist winding through thorny rose trellises, weeping willows, and rain-slicked cobblestone.",
        "icon": "🥀"
    },
    "Study": {
        "description": "A secluded chamber behind stained glass, dominated by a locked bureau and smoldering fireplace.",
        "icon": "🖋️"
    },
    "Ballroom": {
        "description": "Dusty parquet floors, vaulted mirrors reflecting the moonlight, and a silent grand piano.",
        "icon": "🎭"
    }
}

# Murder Weapons
WEAPONS: Dict[str, Dict[str, str]] = {
    "Knife": {
        "description": "A surgical Sheffield steel blade with an ivory handle, wiped meticulously clean with silk.",
        "icon": "🗡️"
    },
    "Candlestick": {
        "description": "A solid brass Victorian candelabrum, battered at its pedestal and streaked with candle soot.",
        "icon": "🕯️"
    },
    "Poison": {
        "description": "A vintage amber apothecary dropper containing lethal aconite extract from the conservatory.",
        "icon": "🧪"
    },
    "Rope": {
        "description": "A length of twisted hemp sash-cord severed with chilling precision from the salon curtains.",
        "icon": "🪢"
    },
    "Revolver": {
        "description": "A snub-nosed .38 service revolver with ornate barrel engravings and a missing cylinder round.",
        "icon": "🔫"
    }
}

CATEGORIES: Dict[str, List[str]] = {
    "WHO": list(SUSPECTS.keys()),
    "WHERE": list(LOCATIONS.keys()),
    "WHAT": list(WEAPONS.keys())
}

VARIABLE_PREFIXES = {
    "WHO": "Who",
    "WHERE": "Where",
    "WHAT": "Weapon"
}

def get_var_name(category: str, item: str) -> str:
    """Format category and entity into standard variable name: Who_Ravi, Where_Library, Weapon_Knife."""
    return f"{VARIABLE_PREFIXES[category]}_{item}"

def parse_var_name(var_name: str) -> tuple[str, str]:
    """Parse variable name back into (category, item)."""
    prefix, item = var_name.split("_", 1)
    prefix_to_cat = {v: k for k, v in VARIABLE_PREFIXES.items()}
    prefix_to_cat.update({"WHO": "WHO", "WHERE": "WHERE", "WHAT": "WHAT", "Who": "WHO", "Where": "WHERE", "Weapon": "WHAT"})
    return prefix_to_cat[prefix], item

# Atmosphere and method notes used by the closing story.
SCENE_NOTES: Dict[str, str] = {
    "Library": (
        "The library was still and close, the way only rooms full of paper can be. "
        "A ladder stood at a crooked angle, one volume lay face-down with its spine broken, "
        "and the fire had been allowed to die in the grate."
    ),
    "Kitchen": (
        "The kitchen had gone cold. A copper pot sat on the range, a half-peeled apple had "
        "browned on the block, and the pantry lantern still swayed although there was no draught."
    ),
    "Garden": (
        "Mist hung in the rose trellises and the cobbles shone black with rain. The fountain had "
        "been shut off, but its basin was full, and a single line of footprints ended at the wall."
    ),
    "Study": (
        "The study smelled of coal smoke and spilled ink. The bureau was locked, the fire was down "
        "to its last red breath, and a sheet of paper had been fed to the flames a moment too late."
    ),
    "Ballroom": (
        "The ballroom was dark but for the moon in the tall mirrors. The grand piano stood open, "
        "its last note long gone, and a trail of candle wax crossed the parquet and stopped at nothing."
    ),
}

METHOD_NOTES: Dict[str, str] = {
    "Knife": (
        "The knife was a Sheffield blade with an ivory handle, and it was used once, with a "
        "surgeon's economy, just under the fifth rib. The handle had been wiped with silk. "
        "The hand that held it had not."
    ),
    "Candlestick": (
        "The candelabrum came down once, hard, at the base of the skull. Brass leaves a particular "
        "mark. The dent in the pedestal matched the wound, and a crescent of candle soot was found "
        "where no candle had ever burned."
    ),
    "Poison": (
        "The aconite went into the brandy ten minutes before the toast. Lord Ravenscroft never tasted "
        "it — aconite numbs the tongue first — and the amber dropper was found later, rolled beneath "
        "the conservatory bench."
    ),
    "Rope": (
        "The sash-cord had been cut from the salon drapes and knotted with a left-handed hitch. "
        "Six feet of cord were missing from the window, and six feet of cord were missing from the story."
    ),
    "Revolver": (
        "There was one round, fired at close range. The cylinder had been spun afterwards to hide the "
        "empty chamber, but a thin line of powder residue remained along the barrel engraving, where "
        "no handkerchief could reach."
    ),
}


def generate_crime_story(
    suspect: str,
    location: str,
    weapon: str,
    evidence: str | None = None,
) -> str:
    """Generate a noir closing chapter explaining exactly how the murder happened.

    ``evidence`` is an optional clue line from the case file. When given, it becomes
    the small detail that broke the culprit's alibi.
    """
    s_info = SUSPECTS.get(suspect, {"title": "The Culprit", "motive": "Driven by dark ambitions."})
    scene = SCENE_NOTES.get(location, "The room was silent, and the lamp had been turned low.")
    method = METHOD_NOTES.get(weapon, "The deed was done quickly, and the instrument was taken away.")

    if evidence:
        break_line = (
            f"The detail that broke the alibi was already written in the case file: "
            f"\u201c{evidence}\u201d It was small, easy to overlook \u2014 and impossible to explain away."
        )
    else:
        break_line = (
            "It was a small thing that undid the story: a door that should have been locked, "
            "a lamp that should have been cold, a name mentioned one time too few."
        )

    return (
        f"### \U0001f56f\ufe0f Case Closed: The Murder of Lord Ravenscroft\n\n"
        f"**The killer was {suspect}, {s_info['title']} — in the {location}, with the {weapon}.**\n\n"
        f"The clock in the east wing had just struck two when the scream moved through the house "
        f"like a draught. By the time the household gathered, Lord Ravenscroft was past saving \u2014 "
        f"and every guest had a reason to be glad of it. {suspect} arrived last, and was the only "
        f"one who did not look surprised.\n\n"
        f"{scene}\n\n"
        f"The motive had been growing in the dark for years. {s_info['motive']} "
        f"That is the thing about old grudges: they never announce themselves. They wait for a "
        f"locked door and a quiet hour.\n\n"
        f"{method}\n\n"
        f"{break_line}\n\n"
        f"When the constable finally laid the sequence out, the denials came quickly and then not "
        f"at all. {suspect} looked at the evidence spread across the table, and something behind the "
        f"eyes went quiet. The house exhaled. Somewhere upstairs a clock resumed its ticking, as if "
        f"the night had only paused.\n\n"
        f"In the end it had not been a guess. Every other version of that evening had been "
        f"eliminated, one contradiction at a time, until only one truth was left standing."
    )
