from typing import Optional, Mapping, AsyncIterator
from dateutil import parser
from datetime import datetime

import re
from aiohttp import ClientResponse, ClientSession
from .types import (Word, Meaning,
                    BriefMeaning,
                    Translation,
                    PartOfSpeechCode,
                    Definition,
                    Properties, Example,
                    MeaningWithSimilarTranslation,
                    AlternativeTranslation, Pronunciation, Language)
from .exc.exceptions import WordsNotFound, MeaningsNotFound, SkyConnectorError

DEFAULT_PAGE_SIZE = 15
MAX_PAGE_SIZE = 128
MEANING_CHUNK_SIZE = 500


class Dictionary:
    def __init__(self, logging=False, rising=True) -> None:
        self.url_search = f"https://dictionary.skyeng.ru/api/public/v1/words/search"
        self.url_meaning = f"https://dictionary.skyeng.ru/api/public/v1/meanings"
        self.logging = logging
        self.rising = rising

    async def __aenter__(self):
        self._session = ClientSession(raise_for_status=True)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._close()

    def _page_size(self, pagesize: int, default: int = DEFAULT_PAGE_SIZE) -> int:
        if pagesize == 0:
            return default
        if not 0 < pagesize <= MAX_PAGE_SIZE:
            raise ValueError(f'pagesize must be between 0 and {MAX_PAGE_SIZE}')
        return pagesize

    async def _fetch(
            self,
            url: str,
            *,
            params: Optional[Mapping[str, str]],
            headers: Mapping[str, str],
            session: ClientSession,
    ) -> ClientResponse:
        try:
            async with session.get(url, params=params, headers=headers, raise_for_status=True) as response:
                await response.read()
        except Exception:
            raise SkyConnectorError
        return response

    def _what_part_of_speech(self, part: Optional[str]) -> Optional[PartOfSpeechCode]:
        if not part:
            return None
        return PartOfSpeechCode.__members__.get(part)

    @staticmethod
    def _as_int(value) -> Optional[int]:
        return int(value) if value is not None else None

    @staticmethod
    def _translation_parts(value) -> tuple[Optional[str], Optional[str]]:
        if not isinstance(value, dict):
            return None, None
        return value.get('text'), value.get('note')

    @staticmethod
    def _parse_url(value) -> Optional[str]:
        if not value:
            return None
        match = re.search(pattern=r"https.+", string=str(value))
        return None if match is None else match.group(0)

    def _pronunciation(self, url, language: Language = Language.en) -> Optional[Pronunciation]:
        if not url:
            return None
        try:
            return Pronunciation(url, language)
        except Exception as error:
            if self.logging:
                print(f'Cannot parse pronunciation url {url!r}: {error}')
            return None

    def _get_words(self, data) -> list[Word]:
        words = []
        if data:
            for word in data:
                brief_meanings = []
                for brief_meaning in word.get('meanings') or []:
                    translation, translation_note = self._translation_parts(brief_meaning.get('translation'))
                    m = BriefMeaning(
                        id=self._as_int(brief_meaning.get('id')),
                        part_of_speech_code=self._what_part_of_speech(brief_meaning.get('partOfSpeechCode')),
                        translation=translation,
                        translation_note=translation_note,
                        image_url=self._parse_url(brief_meaning.get('imageUrl')),
                        transcription=brief_meaning.get('transcription'),
                        sound_url=self._pronunciation(brief_meaning.get('soundUrl'), Language.en),  # sound of transcription
                        text=word.get('text'),
                    )
                    brief_meanings.append(m)
                word = Word(
                    id=self._as_int(word.get('id')),
                    text=word.get('text'),
                    meanings=brief_meanings
                )
                words.append(word)
        else:
            if self.rising:
                raise WordsNotFound
        return words

    def _get_meanings(self, data) -> list[Meaning]:
        meanings = []
        if data:
            for meaning in data:
                images_url = []
                for image in meaning.get('images') or []:
                    images_url.append(self._parse_url(image.get('url')))
                examples = []
                for example in meaning.get('examples') or []:
                    examples.append(Example(text=example.get('text'),
                                            sound_url=self._pronunciation(example.get('soundUrl'), Language.en)))
                meanings_with_similar_translation = []
                for meaning_with_similar_translation in meaning.get('meaningsWithSimilarTranslation') or []:
                    translation, translation_note = self._translation_parts(
                        meaning_with_similar_translation.get('translation'))
                    form = MeaningWithSimilarTranslation(
                        meaning_id=meaning_with_similar_translation.get('meaningId'),
                        frequency_percent=meaning_with_similar_translation.get('frequencyPercent'),
                        part_of_speech_abbreviation=meaning_with_similar_translation.get('partOfSpeechAbbreviation'),
                        translation=translation,
                        translation_note=translation_note
                    )
                    meanings_with_similar_translation.append(form)
                alternative_translations = []
                for alternative_translation in meaning.get('alternativeTranslations') or []:
                    translation, translation_note = self._translation_parts(
                        alternative_translation.get('translation'))
                    form = AlternativeTranslation(
                        text=alternative_translation.get('text'),
                        translation=translation,
                        translation_note=translation_note
                    )
                    alternative_translations.append(form)
                _prop = meaning.get('properties') or {}
                prop_sound_url = _prop.get('soundUrl')
                if isinstance(prop_sound_url, str) and prop_sound_url.startswith('//'):
                    prop_sound_url = f'https:{prop_sound_url}'
                properties = Properties(collocation=_prop.get('collocation'),
                                        not_gradable=_prop.get('notGradable'),
                                        irregular=_prop.get('irregular'),
                                        past_tense=_prop.get('pastTense'),
                                        past_participle=_prop.get('pastParticiple'),
                                        countability=_prop.get('countability'),
                                        plurality=_prop.get('plurality'),
                                        plural=_prop.get('plural'),
                                        irregular_plural=_prop.get('irregularPlural'),
                                        transitivity=_prop.get('transitivity'),
                                        linking_verb=_prop.get('linkingVerb'),
                                        linking_type=_prop.get('linkingType'),
                                        phrasal_verb=_prop.get('phrasalVerb'),
                                        sound_url=prop_sound_url,
                                        false_friends=_prop.get('falseFriends'), )
                part_of_speech_code = self._what_part_of_speech(meaning.get('partOfSpeechCode'))
                _definition = meaning.get('definition') or {}
                _definition_sound_url = _definition.get('soundUrl')
                translation, translation_note = self._translation_parts(meaning.get('translation'))
                meaning = Meaning(
                    id=meaning.get('id'),
                    word_id=self._as_int(meaning.get('wordId')),
                    difficulty_level=meaning.get('difficultyLevel'),
                    part_of_speech_code=part_of_speech_code,
                    prefix=meaning.get('prefix'),
                    text=meaning.get('text'),
                    sound_url=self._pronunciation(meaning.get('soundUrl'), Language.en),
                    transcription=meaning.get('transcription'),
                    properties=properties,
                    updated_at=meaning.get('updatedAt'),
                    mnemonics=meaning.get('mnemonics'),
                    translation=translation,
                    translation_note=translation_note,
                    images_url=[None] if images_url == [] else images_url,
                    definition=_definition.get('text'),
                    definition_sound_url=self._pronunciation(_definition_sound_url, Language.en),
                    examples=examples,
                    meanings_with_similar_translation=meanings_with_similar_translation,
                    alternative_translations=alternative_translations
                )
                meanings.append(meaning)
        else:
            if self.rising:
                raise MeaningsNotFound
        return meanings

    async def words(self, word: str, page: int = 1, pagesize: int = 0) -> list[Word]:
        '''
        :param word:
        :param page: page number, starting from 1
        :param pagesize: 0 means default page size (15), maximum is 128
        :return: One page with meanings. It will return relevant meanings grouped by words.
                 You can search in English or translation
        '''
        if page < 1:
            raise ValueError('page must be >= 1')
        pagesize = self._page_size(pagesize)
        params = {
            'search': word,
            'page': page,
            'pageSize': pagesize}
        headers = {}
        response = await self._fetch(self.url_search, params=params, headers=headers, session=self._session)
        if self.logging:
            print("response status ", response.status)
        data = await response.json()
        return self._get_words(data)

    async def iter_words(self, word: str, pagesize: int = MAX_PAGE_SIZE) -> AsyncIterator[Word]:
        '''
        :param word:
        :param pagesize: page size, from 1 to 128 (0 means 128)
        :return: Async iterator over all found words, fetching pages automatically
        '''
        pagesize = self._page_size(pagesize, default=MAX_PAGE_SIZE)
        page = 1
        while True:
            try:
                batch = await self.words(word, page=page, pagesize=pagesize)
            except WordsNotFound:
                if page == 1 and self.rising:
                    raise
                break
            for item in batch:
                yield item
            if len(batch) < pagesize:
                break
            page += 1

    def _out_value(self, ids: int | list[int]) -> str:
        '''
        :param ids: id or array ids
        :return: A string of meaning ids. Separated by a comma
        '''
        if type(ids) is int:
            return str(ids)
        elif type(ids) is list:
            return ','.join(str(el) for el in ids)
        else:
            raise ValueError

    def _convert_time(self, complex_date_string: str) -> str:
        default = datetime(2000, 1, 1, 0, 0, 0)
        date_obj_flex = parser.parse(complex_date_string, default=default)
        return date_obj_flex.strftime("%Y-%m-%d %H:%M:%S")

    async def meaning(self, ids: int | list[int], data: str = None) -> list[Meaning]:
        '''
        :param ids: An array of meaning ids or integer value
        :param data: Retrieve results from this date. * * Must be in UTC timezone. *
        :return: Return full information about meaning.
                 Large id lists are split into chunks of MEANING_CHUNK_SIZE
                 and merged, preserving the order of the passed ids.
        '''
        if type(ids) is int:
            ids_list = [ids]
        elif isinstance(ids, list):
            ids_list = ids
        else:
            raise ValueError('ids must be an int or a list of ints')

        # Request each id only once, keeping the original order.
        unique_ids = list(dict.fromkeys(ids_list))
        if not unique_ids:
            return self._get_meanings([])

        updated_at = '' if data is None else self._convert_time(data)
        headers = {}
        response_data = []
        for start in range(0, len(unique_ids), MEANING_CHUNK_SIZE):
            chunk = unique_ids[start:start + MEANING_CHUNK_SIZE]
            params = {
                'ids': self._out_value(chunk),
                'updatedAt': updated_at
            }
            if self.logging:
                print(params)
            response = await self._fetch(self.url_meaning, params=params, headers=headers, session=self._session)
            response_data.extend(await response.json())

        # The API may return ids as strings, while callers pass ints, so compare by text.
        positions = {str(meaning_id): index for index, meaning_id in enumerate(unique_ids)}
        response_data.sort(key=lambda item: positions.get(str(item.get('id')), len(positions)))
        return self._get_meanings(response_data)

    async def _close(self) -> None:
        if not self._session.closed:
            # print("Session is closed")
            await self._session.close()
