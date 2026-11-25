"""Entity resolution: group span mentions into entities, rules only.

People. A mention is read as name words, after removing a title written inside the
span ("Sig.", "Dott.ssa", "Avv."); the last word is taken as the surname, together
with the particles before it ("De Luca", "Di Stefano"), and what comes before is the
first names. Two mentions are the same person when the last word of one is among the
words of the other ("Marco Ferri", "Ferri", "Marco"), unless both carry first names
and these differ ("Marco Ferri", "Anna Ferri"), or their genders differ ("Sig.
Ferri", "Sig.ra Ferri"). The same full name is always one person, whatever a title
says ("Prof. Maria Rossi"), and so is a name written surname first ("Ferri Marco",
"De Luca Rosa"); the same words in another order are not ("Rosa De Luca", "Luca De
Rosa"). Mentions with a
first name are grouped first, in order of appearance; a surname or a first name
alone then joins the first person it is compatible with.

Gender comes from a title, written inside the span or just before it on the same
line, then from the first name looked up in the lists below, otherwise it is UNKNOWN.

Every other type: one entity per value, compared without case and extra spaces.

The canonical value of a person is the mention with the most name words (the first
one on a tie), of any other entity its first mention. Entity ids are
`<TYPE>_<n>`, numbered per type in order of appearance.

The name lists are common Italian first names, written for this project; names
used for both genders (Andrea, Celeste, Fiore) are left out on purpose.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field

from omissis.contracts import Entity, Gender, Span, SpanType

_TITLES = {
    Gender.F: "sig.ra sig.na signora signorina dott.ssa dottoressa prof.ssa professoressa",
    Gender.M: "sig. sig signor signore dott. dott dottor dottore prof. prof professor professore",
}
_TITLE_GENDER = {title: gender for gender, titles in _TITLES.items() for title in titles.split()}
# Titles that say nothing about gender, and the articles that may open a mention.
_NO_GENDER = frozenset("avv. avv ing. ing dr. dr geom. geom rag. rag arch. arch il la".split())
# Words that open a surname of several words.
_PARTICLES = frozenset("de di del della dello dei degli da dal dalla dalle lo la li le".split())
_TITLE_BEFORE = re.compile(r"(\S+)[^\S\n]*$")  # the word before the span, on the same line
_OPENING = "([{«“‘\"'/"

_FEMALE = frozenset(
    """alessandra alessia alice angela anna annalisa antonella arianna aurora barbara beatrice
    bianca camilla carla carlotta carmela caterina cecilia chiara cinzia claudia cristina
    daniela debora elena eleonora elisa elisabetta emma erica federica francesca gabriella
    giada gianna giorgia giovanna giulia giuseppina grazia ilaria irene laura letizia lidia
    liliana lorenza loredana luana lucia luisa maddalena manuela mara margherita maria
    mariangela marina marta martina matilde michela monica nadia nicoletta noemi paola
    patrizia raffaella rita roberta rosa rosanna sabrina sara serena silvia simona sofia
    sonia stefania susanna teresa valentina valeria vanessa veronica viola vittoria""".split()
)
_MALE = frozenset(
    """alberto aldo alessandro alessio angelo antonio armando bruno carlo cesare claudio
    cristian daniele dario davide diego domenico edoardo elia emanuele enrico enzo ettore
    fabio fabrizio federico filippo francesco franco gabriele giacomo gianluca gianni
    giorgio giovanni giulio giuseppe guido ivan jacopo leonardo lorenzo luca luciano luigi
    manuel marcello marco mario massimo matteo mattia maurizio mauro michele mirko nicola
    paolo pasquale piero pietro raffaele renato riccardo roberto rocco salvatore samuele
    sergio silvio simone stefano tommaso umberto valerio vincenzo vittorio""".split()
)


def _normalise(value: str) -> str:
    return " ".join(value.split()).casefold()


def _name_gender(name: str) -> Gender:
    if name in _FEMALE:
        return Gender.F
    return Gender.M if name in _MALE else Gender.UNKNOWN


@dataclass
class _Person:
    words: set[str]
    names: tuple[str, ...]  # the name words in the order they are written
    surname: str
    first_names: tuple[str, ...]
    title: Gender
    # Each mention with its number of name words (the title does not count).
    mentions: list[tuple[Span, int]] = field(default_factory=list)

    @property
    def known_gender(self) -> Gender:
        """Gender from a title, else from the first name; a lone word is not evidence."""
        if self.title is not Gender.UNKNOWN or not self.first_names:
            return self.title
        return _name_gender(self.first_names[0])

    def accepts(self, other: _Person) -> bool:
        if not (other.surname in self.words or self.surname in other.words):
            return False
        if self.first_names and other.first_names:
            if self.names == other.names:
                return True  # one full name, whatever a title says
            swapped = other.names == self._surname_first() or self.names == other._surname_first()
            if not swapped and self.first_names != other.first_names:
                return False
        mine, theirs = self.known_gender, other.known_gender
        return Gender.UNKNOWN in (mine, theirs) or mine is theirs

    def _surname_first(self) -> tuple[str, ...]:
        """The same name written with the surname before the first names."""
        return self.names[len(self.first_names) :] + self.first_names

    def absorb(self, other: _Person) -> None:
        self.words |= other.words
        self.first_names = self.first_names or other.first_names
        if self.title is Gender.UNKNOWN:
            self.title = other.title
        self.mentions += other.mentions

    @property
    def gender(self) -> Gender:
        if self.known_gender is not Gender.UNKNOWN or self.first_names:
            return self.known_gender
        return _name_gender(self.surname)  # a lone word may be a first name ("Lidia")


def _name_words(value: str) -> tuple[list[str], Gender]:
    """The name words of a mention as they are written, and the gender of its title."""
    words = value.split() or [value]  # a blank mention is its own only word
    title = Gender.UNKNOWN
    while len(words) > 1 and (
        words[0].casefold() in _TITLE_GENDER or words[0].casefold() in _NO_GENDER
    ):
        title = _TITLE_GENDER.get(words.pop(0).casefold(), title)
    return words, title


def _first_names(words: list[str]) -> list[str]:
    """The words before the surname: the last word and its particles are the surname."""
    first = words[:-1]
    while first and first[-1].casefold() in _PARTICLES:
        first.pop()
    return first


def name_parts(value: str) -> tuple[str, str]:
    """The first names and the surname of a person's name, as written, without a title.

    A name of one word, or a surname alone, has no first names: `("", "De Luca")`.
    """
    words, _ = _name_words(value)
    first = _first_names(words)
    return " ".join(first), " ".join(words[len(first) :])


def _first_name_in_front(mention: str) -> bool:
    words, _ = _name_words(mention)
    return _name_gender(words[0].casefold()) is not Gender.UNKNOWN


def _read_person(span: Span, text: str) -> _Person:
    written, title = _name_words(span.text)
    if title is Gender.UNKNOWN:
        before = _TITLE_BEFORE.search(text[: span.start])
        if before:
            word = before.group(1).casefold().lstrip(_OPENING)
            title = _TITLE_GENDER.get(word, Gender.UNKNOWN)
    words = [word.casefold() for word in written]
    first = tuple(_first_names(words))
    return _Person(set(words), tuple(words), words[-1], first, title, [(span, len(words))])


def _people(spans: list[Span], text: str) -> list[tuple[str, list[Span], Gender]]:
    read = [_read_person(span, text) for span in spans]
    people: list[_Person] = []
    for wanted in (True, False):  # mentions with a first name first
        for person in read:
            if bool(person.first_names) is not wanted:
                continue
            match = next((p for p in people if p.accepts(person)), None)
            if match is None:
                people.append(person)
            else:
                match.absorb(person)
    out = []
    for person in people:
        mentions = sorted(person.mentions, key=lambda m: (m[0].start, m[0].end))
        # The longest mention; of one name in two orders ("De Luca Rosa", "Rosa De
        # Luca"), the one with a known first name in front, whose last word is the surname.
        canonical = max(mentions, key=lambda m: (m[1], _first_name_in_front(m[0].text)))[0].text
        out.append((canonical, [span for span, _ in mentions], person.gender))
    return out


def resolve(spans: Sequence[Span], text: str) -> list[Entity]:
    """Group `spans` into entities.

    Every input span ends up in exactly one entity. Person mentions merge when one
    contains the other's surname; two people with one surname and different first
    names stay separate. Other types merge on normalised equality (case and
    whitespace). Gender from titles first (Sig./Sig.ra, Dott./Dott.ssa), then from
    a first-name list, otherwise UNKNOWN. Rules only; the same function serves
    every detector.
    """
    ordered = sorted(spans, key=lambda s: (s.start, s.end))
    groups = _people([s for s in ordered if s.type is SpanType.PERSONA], text)
    others: dict[tuple[SpanType, str], list[Span]] = {}
    for span in ordered:
        if span.type is not SpanType.PERSONA:
            others.setdefault((span.type, _normalise(span.text)), []).append(span)
    groups += [(mentions[0].text, mentions, Gender.UNKNOWN) for mentions in others.values()]

    counters: dict[SpanType, int] = {}
    entities = []
    for canonical, mentions, gender in sorted(groups, key=lambda g: g[1][0].start):
        type = mentions[0].type
        counters[type] = counters.get(type, 0) + 1
        entities.append(
            Entity(f"{type.value}_{counters[type]}", type, canonical, tuple(mentions), gender)
        )
    return entities
