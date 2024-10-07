from typing import Optional, Mapping

import re
from aiohttp import ClientResponse, ClientSession
from .types import (Word, Meaning,
                    BriefMeaning, Translation,
                    PartOfSpeechCode, Definition,
                    Properties, Example,
                    MeaningWithSimilarTranslation,
                    AlternativeTranslation, Pronunciation, Language)


class Dictionary:
    def __init__(self) -> None:
        self.url_search = f"https://dictionary.skyeng.ru/api/public/v1/words/search"
        self.url_meaning = f"https://dictionary.skyeng.ru/api/public/v1/meanings"

    async def __aenter__(self):
        self._session = ClientSession(raise_for_status=True)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._close()

    async def _fetch(
            self,
            url: str,
            *,
            params: Optional[Mapping[str, str]],
            headers: Mapping[str, str],
            session: ClientSession,
    ) -> ClientResponse:
        async with session.get(url, params=params, headers=headers, raise_for_status=True) as response:
            await response.read()
        return response

    def _what_part_of_speech(self, part: str) -> PartOfSpeechCode:
        return PartOfSpeechCode.__dict__['_member_map_'][part]

    def _get_words(self, data) -> list[Word]:
        words = []
        if data is not None:
            for word in data:
                brief_meanings = []
                for brief_meaning in word['meanings']:
                    part_of_speech_code = self._what_part_of_speech(brief_meaning['partOfSpeechCode'])
                    match = re.search(pattern=r"https.+", string=brief_meaning['imageUrl'])
                    m = BriefMeaning(
                        id=int(brief_meaning['id']),
                        part_of_speech_code=part_of_speech_code,
                        translation=brief_meaning['translation']['text'],
                        translation_note=brief_meaning['translation']['note'],
                        image_url=None if match is None else match.group(0),
                        transcription=brief_meaning['transcription'],
                        sound_url=Pronunciation(brief_meaning['soundUrl'], Language.en)  # sound of transcription
                    )
                    brief_meanings.append(m)
                word = Word(
                    id=int(word['id']),
                    text=word['text'],
                    meanings=brief_meanings
                )
                words.append(word)
        return words

    def _get_meanings(self, data) -> list[Meaning]:
        meanings = []
        if data is not None:
            for meaning in data:
                images = []
                for image in meaning['images']:
                    match = re.search(pattern=r"https.+", string=image['url'])
                    images.append(None if match is None else match.group(0))
                examples = []
                for example in meaning['examples']:
                    examples.append(Example(text=example['text'],
                                            sound_url=Pronunciation(example['soundUrl'], Language.en)))
                meanings_with_similar_translation = []
                for meaning_with_similar_translation in meaning['meaningsWithSimilarTranslation']:
                    form = MeaningWithSimilarTranslation(
                        meaning_id=meaning_with_similar_translation['meaningId'],
                        frequency_percent=meaning_with_similar_translation['frequencyPercent'],
                        part_of_speech_abbreviation=meaning_with_similar_translation['partOfSpeechAbbreviation'],
                        translation=meaning_with_similar_translation['translation']['text'],
                        translation_note=meaning_with_similar_translation['translation']['note']
                    )
                    meanings_with_similar_translation.append(form)
                alternative_translations = []
                for alternative_translation in meaning['alternativeTranslations']:
                    form = AlternativeTranslation(
                        text=alternative_translation['text'],
                        translation=alternative_translation['translation']['text'],
                        translation_note=alternative_translation['translation']['note']
                    )
                    alternative_translations.append(form)
                properties = Properties(collocation=False,
                                        irregular=False,
                                        past_tense=None,
                                        past_participle=None,
                                        transitivity=None,
                                        phrasal_verb=False,
                                        sound_url=None,  # TODO : пока не знаю что там должно быть
                                        false_friends=None)
                # TODO : изменить
                part_of_speech_code = self._what_part_of_speech(meaning['partOfSpeechCode'])
                meaning = Meaning(
                    id=meaning['id'],
                    word_id=int(meaning['wordId']),
                    difficulty_level=meaning['difficultyLevel'],
                    part_of_speech_code=part_of_speech_code,
                    prefix=meaning['prefix'],
                    text=meaning['text'],
                    sound_url=Pronunciation(meaning['soundUrl'], Language.en),
                    transcription=meaning['transcription'],
                    properties=properties,
                    updated_at=meaning['updatedAt'],
                    # TODO изменить дату на дату питон
                    mnemonics=meaning['mnemonics'],
                    translation=meaning['translation']['text'],
                    translation_note=meaning['translation']['note'],
                    images=images,
                    definition=meaning['definition']['text'],
                    definition_sound_url=meaning['definition']['soundUrl'],
                    examples=examples,
                    meanings_with_similar_translation=meanings_with_similar_translation,
                    alternative_translations=alternative_translations
                )
                meanings.append(meaning)
        return meanings

    async def words(self, word: str, page: int = 1, pagesize: int = 0) -> list[Word]:
        '''
        :param word:
        :param page:
        :param pagesize: if value 0 then show full page, if value 1 then show only one word
        :return: Find words with meanings. It will return relevant meanings grouped by words.
                 You can search in English or translation
        '''
        params = {
            'search': word,
            'page': page,
            'pageSize': pagesize}
        headers = {}
        response = await self._fetch(self.url_search, params=params, headers=headers, session=self._session)
        print(response.status)
        data = await response.json()
        return self._get_words(data)

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

    async def meaning(self, ids: int | list[int], data: str = '') -> list[Meaning]:
        '''
        :param ids: An array of meaning ids or integer value
        :param data: Retrieve results from this date. * * Must be in UTC timezone. *
        :return: Return full information about meaning
        '''
        params = {
            'ids': self._out_value(ids),
            'updatedAt': data
        }
        headers = {}
        response = await self._fetch(self.url_meaning, params=params, headers=headers, session=self._session)
        print(response.status)
        data = await response.json()
        return self._get_meanings(data)

    async def _close(self) -> None:
        if not self._session.closed:
            print("Session is closed")
            await self._session.close()
