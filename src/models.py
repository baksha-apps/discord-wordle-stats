from dataclasses import dataclass
from enum import Enum, unique

import discord


@dataclass(frozen=True)
class Command:
    name: str
    description: str


class Reaction(Enum):
    @classmethod
    def positives(cls):
        return [
            "nice one",
            "that's what we like to see",
            "alright mr dictionary",
            "well done",
            "round of applause for this guy",
            "congratulations",
            "AYOOOO",
            "YURRRRR",
            "LETS GOOOOO",
            "LOOK @YOU",
            "WATCH THIS",
        ]

    @classmethod
    def negatives(cls):
        return [
            "oh no",
            "sadly",
            "ain't no way",
            "sheesh...",
            "its not the best...",
            "english not ur best",
            "why did you post this here?",
            "i too do not have eyes",
            "with a score like that, just know that participation matters",
            "use `$today` to see the answer since you ain't catch it",
            "https://www.dictionary.com/",
            "you've done better",
            "are you new here",
            "mediocrity",
            "ok",
        ]


@unique
class Color(Enum):
    RED = discord.Color.from_rgb(204, 0, 0)
    BLUE = discord.Color.from_rgb(70, 130, 180)
    ORANGE = discord.Color.from_rgb(255, 111, 0)
    TURQ = discord.Color.from_rgb(95, 232, 182)


@unique
class Emote(Enum):
    # POSITIVE
    PEEPO_SIP = "<:peepoSip:711248715532468317>"
    AYAYA = "<:AYAYA:702579819610898513>"
    DHANDS = "<:dhands:702525589395079220>"
    UP = "🆙"
    CHART_UP = "📈"

    # NEGATIVE
    COOL_CRY = "<:coolcry:911489931233341460>"
    DOWN = "🔻"
    TOM_STARE = "<:tomStare:800220225794211860>"
    DAMN = "<:damn:800218841547931700>"
    YIKES = "<:yikes:800219237804539904>"
    GLASS_RNG = "<:glassRNG:704048329356607538>"
    THONKING = '<:thonking:726838160809787464>'
    CLOWN = ':clown:'

    @classmethod
    def positives(cls):
        return [
            Emote.PEEPO_SIP,
            Emote.AYAYA,
            Emote.DHANDS,
            Emote.DAMN,
            Emote.UP,
            Emote.CHART_UP,
        ]

    @classmethod
    def negatives(cls):
        return [
            Emote.COOL_CRY,
            Emote.DOWN,
            Emote.TOM_STARE,
            Emote.DAMN,
            Emote.YIKES,
            Emote.GLASS_RNG,
            Emote.CLOWN,
        ]

print(Emote.positives())
print(Emote.negatives())
