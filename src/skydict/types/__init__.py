from dataclasses import dataclass
from typing import TypeAlias
from enum import Enum
from urllib.parse import urlparse, parse_qs, urlencode

MeaningId: TypeAlias = int

class PartOfSpeechCode(Enum):  # Available code
    def __init__(self, en, ru):
        self.en = en
        self.ru = ru

    n = ("noun", "существительное")
    v = ("verb", "глагол")
    j = ("adjective", "прилагательное")
    r = ("adverb", "наречие")
    prp = ("preposition", "предлог")
    prn = ("pronoun", "местоимение")
    crd = ("cardinal number", "количественное числительное")
    cjc = ("conjunction", "союз")
    exc = ("interjection", "междометие")
    det = ("article", "артикль")
    abb = ("abbreviation", "сокращение")
    x = ("particle", "частица")
    ord = ("ordinal number", "порядковое числительное")
    md = ("modal verb", "модальный глагол")
    ph = ("phrase", "фраза")
    phi = ("idiom", "идиома")


@dataclass
class Translation:
    text: str  # A text of a translation.
    note: str  # A note about translation.


class Language(Enum):
    en = 'english'
    ru = 'russian'

class Pronunciation:
    '''
    handler link with own params
    example: https://vimbox-tts.skyeng.ru/api/v1/tts?text=Lacking+ease+or+grace.&lang=en&voice=male_2'
    '''
    def __init__(self, url: str, language: Language):
        __parse_result = urlparse(url)
        self.__scheme = __parse_result.scheme
        self.__netloc = __parse_result.netloc
        self.__path = __parse_result.path
        __params = parse_qs(__parse_result.query)
        __text = __params.get('text')[0]
        __lang = language.name
        self.__assembly_params_dict = {'text': __text,
                                       'lang': __lang,
                                       'voice': 'male_1'}
        if __params.get('isSsml') is not None:
            __is_ssml = __params.get('isSsml')[0]
            self.__assembly_params_dict['isSsml'] = __is_ssml

    @property
    def male_1(self):
        self.__assembly_params_dict['voice'] = 'male_1'
        params = urlencode(self.__assembly_params_dict)
        return f'{self.__scheme}://{self.__netloc}{self.__path}?{params}'

    @property
    def male_2(self):
        self.__assembly_params_dict['voice'] = 'male_2'
        params = urlencode(self.__assembly_params_dict)
        return f'{self.__scheme}://{self.__netloc}{self.__path}?{params}'

    @property
    def female_1(self):
        self.__assembly_params_dict['voice'] = 'female_1'
        params = urlencode(self.__assembly_params_dict)
        return f'{self.__scheme}://{self.__netloc}{self.__path}?{params}'

    @property
    def female_2(self):
        self.__assembly_params_dict['voice'] = 'female_2'
        params = urlencode(self.__assembly_params_dict)
        return f'{self.__scheme}://{self.__netloc}{self.__path}?{params}'

    def __repr__(self):
        return self.male_1

    def __str__(self):
        return self.male_1


@dataclass
class BriefMeaning:  # Meaning2
    id: MeaningId  # MeaningId.
    part_of_speech_code: PartOfSpeechCode
    translation: str
    translation_note: str
    image_url: str  #
    transcription: str  #
    sound_url: Pronunciation
    text: str


@dataclass
class Properties:
    collocation: bool | None #
    not_gradable: bool | None
    irregular: bool | None #
    past_tense: str | None  # "found",
    past_participle: str | None  # "found",
    transitivity: str | None  # "t", "i" "ti"
    countability: str | None # "c", cu
    plurality: str | None # s , sp
    plural: str | None
    irregular_plural: str | None
    phrasal_verb: bool | None # false,
    linking_verb: bool | None #
    linking_type: str | None # 'L + noun, L + adjective'
    sound_url: Pronunciation | None  #
    false_friends: list | None   #


@dataclass  #
class Definition:  #
    text: str  #
    sound_url: Pronunciation  #


@dataclass
class Example:
    text: str  #
    sound_url: Pronunciation  #


@dataclass
class MeaningWithSimilarTranslation:
    meaning_id: int  #
    frequency_percent: float  #
    part_of_speech_abbreviation: str  # часть речи на русском напрм: "гл."
    translation: str  #
    translation_note: str


@dataclass
class AlternativeTranslation:  #
    text: str  #
    translation: str  #
    translation_note: str


@dataclass
class Meaning:
    id: MeaningId  # Meaning id.
    word_id: int  # Word is a group of meanings. We combine meanings by word entity.
    difficulty_level: int  # There are 6 difficultyLevels: 1, 2, 3, 4, 5, 6.
    part_of_speech_code: PartOfSpeechCode  # String representation of a part of speech.
    prefix: str  # Infinitive particle (to) or articles (a, the).
    text: str  # Meaning text.
    sound_url: Pronunciation  # URL to meaning sound.
    transcription: str  # IPA phonetic transcription.
    properties: Properties  #
    updated_at: str  #
    mnemonics: str  #
    translation: str  #
    translation_note: str | None
    images: list[str]  # A collection of an images.
    definition: str  #
    definition_sound_url: Pronunciation
    examples: list[Example]  # Usage examples
    meanings_with_similar_translation: (
        list[MeaningWithSimilarTranslation])  # Collection of meanings with similar translations.
    alternative_translations: (
        list[AlternativeTranslation])  # Collection of alternative translations.


@dataclass
class Word:
    id: int  #
    text: str  #
    meanings: list[BriefMeaning]  #
