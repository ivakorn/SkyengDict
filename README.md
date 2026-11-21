# SkyengDict: Асинхронная библиотека для работы с Dictionary API Skyeng  
  
## Описание  
  
**SkyengDict** — это асинхронная библиотека на Python, предоставляющая доступ к API словаря Skyeng. Она позволяет искать слова, получать их значения и обрабатывать лингвистические данные, такие как части речи, переводы и произношения.  
  
### Установка  
  
```bash  
pip install skyengdict
```  
  
### Пример использования  
  
```python
import asyncio
from skyengdict import Dictionary


async def main():
    async with Dictionary() as dictionary:
        result_1 = await dictionary.words('любовь', pagesize=1)
        for word in result_1:
            print(f"{word.text} - {word.meanings[0].translation}")

        result_2 = await dictionary.meaning(45)
        for mean in result_2:
            print(f"{mean.text} - {mean.translation}\n")


if __name__ == '__main__':
    asyncio.run(main())
```  
  
  
### Класс `Dictionary`  
  
  **Параметры**:    
    - `logging`: Логировать процесс получения данных. По умолчанию `False`  
    - `rising`: Возбуждать исключения, если не найдены слова (значения), либо возвращать пустой список. По умолчанию `True`  
  
Основной класс для взаимодействия с API Skyeng Dictionary. Он предоставляет методы для поиска слов и получения их значений.  
  
#### Методы:  
  
- **`words(word: str, page: int = 1, pagesize: int = 0) -> list[Word]`**    
Возвращает **одну страницу** результатов поиска, а не все найденные слова.    
  
  **Параметры**:    
    - `word`: слово для поиска (на английском или русском).    
    - `page`: номер страницы, начиная с 1.    
    - `pagesize`: сколько слов вернуть за один запрос. `0` — значение по умолчанию (15 слов). Максимум — 128; большее значение вызывает `ValueError`.    
    
  **Возвращает**:    
  - Список объектов `Word` — только текущую страницу.  
  
  **Пример**:
```python
async with Dictionary() as dictionary:
    page_1 = await dictionary.words('cat')              # до 15 слов
    page_2 = await dictionary.words('cat', page=2)     # следующие до 15 слов
```

- **`iter_words(word: str, pagesize: int = 128) -> AsyncIterator[Word]`**    
Автоматически проходит по всем страницам и отдаёт **все** найденные слова.    
  
  **Параметры**:    
    - `word`: слово для поиска.    
    - `pagesize`: размер одной страницы, от 1 до 128. По умолчанию 128.    
    
  **Пример**:
```python
async with Dictionary() as dictionary:
    async for word in dictionary.iter_words('cat'):
        print(word.text)
```

  **Важно**: запрос к API выполняется **на каждую страницу**, а не на каждое слово.    
  Например, для `cat` это 4 запроса и 390 слов (страницы по 128, 128, 128 и 6).    
  Для `example` — 1 запрос и 10 слов, потому что все они помещаются в одну страницу.  
  
- **`meaning(ids: int | list[int], data: str = None) -> list[Meaning]`**    
Получает подробную информацию о значениях слов по их идентификаторам.    
  
  **Параметры**:    
    - `ids`: Один идентификатор значения или список идентификаторов.    
    - `data`: Дата в формате строки.    
  
  **Возвращает**:    
  - Список объектов `Meaning`, представляющих полную информацию о значениях.  
  
## Типы данных  
  
### `Word`  
  
Представляет слово и связанные с ним краткие значения.  
  
- **Атрибуты**:  
  - `id`: Уникальный идентификатор слова.  
  - `text`: Слово в текстовом виде.  
  - `meanings`: Список объектов `BriefMeaning`, представляющих краткие значения слова.  
  
### `BriefMeaning`  
  
Краткое описание значения слова.  
  
- **Атрибуты**:  
  - `id`: Уникальный идентификатор значения.  
  - `part_of_speech_code`: Часть речи, представляемая перечислением `PartOfSpeechCode`.  
  - `translation`: Перевод текста.  
  - `translation_note`: Примечания к переводу.  
  - `image_url`: URL изображения.  
  - `transcription`: Фонетическая транскрипция в формате IPA.  
  - `sound_url`: Объект `Pronunciation`, содержащий ссылку на произношение слова.  
  - `text`: Слово на английском.  
  
### `Meaning`  
  
Подробное описание значения слова на английском.  
  
- **Атрибуты**:  
  - `id`: Уникальный идентификатор значения.  
  - `word_id`: Идентификатор слова, к которому относится значение.  
  - `difficulty_level`: Уровень сложности (от 1 до 6).  
  - `part_of_speech_code`: Часть речи для данного значения.  
  - `prefix`: Приставка или артикли (например, "to" или "the").  
  - `text`: Слово на английском.  
  - `sound_url`: Объект `Pronunciation`, представляющий ссылку URL на произношение.  
  - `transcription`: Фонетическая транскрипция.  
  - `properties`: Объект `Properties`, содержащий грамматическую информацию.  
  - `updated_at`: Дата последнего обновления значения.  
  - `mnemonics`: Мнемоническая подсказка для значения.  
  - `translation`: Перевод текста значения.  
  - `translation_note`: Примечания к переводу (если есть).  
  - `images_url`: Список URL изображений.  
  - `definition`: Описание значения.  
  - `definition_sound_url`: Объект `Pronunciation` со ссылкой на произношение описания.  
  - `examples`: Список объектов `Example`, содержащих примеры использования.  
  - `meanings_with_similar_translation`: Список объектов `MeaningWithSimilarTranslation`, представляющих значения с похожими переводами.  
  - `alternative_translations`: Список объектов `AlternativeTranslation`, представляющих альтернативные переводы.  
  
### `PartOfSpeechCode` (Enum)  
  
Перечисление, представляющее часть речи слова. Доступны следующие значения:  
  
- `n`: существительное    
- `v`: глагол    
- `j`: прилагательное    
- `r`: наречие    
- `prp`: предлог    
- `prn`: местоимение    
- `crd`: количественное числительное    
- `cjc`: союз    
- `exc`: междометие    
- `det`: артикль    
- `abb`: сокращение    
- `x`: частица    
- `ord`: порядковое числительное    
- `md`: модальный глагол    
- `ph`: фраза    
- `phi`: идиома  
  
### `Pronunciation`  
  
Возвращает URL-адрес на аудио-запись с определенным произношением. 
  
- **Методы**:  
  - `british_male`: Возвращает URL-адрес для мужского голоса c британским произношением.  
  - `american_male`: Возвращает URL-адрес для мужского голоса c американским произношением.  
  - `british_female`: Возвращает URL-адрес для женского голоса c британским произношением.  
  - `american_female`: Возвращает URL-адрес для женского голоса c американским произношением.  

Все голоса — английские: `Dictionary` всегда создаёт `Pronunciation` с `Language.en`, поэтому `Language.ru` в текущей версии не используется.

пример использования:
```
from skyengdict.types import Pronunciation, Language

url = "https://vimbox-tts.skyeng.ru/api/v1/tts?text=Hello&lang=en&voice=male_2"
pronunciation = Pronunciation(url, Language.en)
print(pronunciation.american_male)
```
  
### `Properties`  
  
Грамматические свойства слова.  
  
- **Атрибуты**:  
  - `collocation`: Указывает, является ли слово коллокацией.  
  - `irregular`: Указывает, является ли слово неправильным.  
  - `past_tense`: Прошедшая форма глагола (если применимо).  
  - `past_participle`: Причастие прошедшего времени (если применимо).  
  - `transitivity`: Переходность глагола (если применимо).  
  - `phrasal_verb`: Указывает, является ли слово фразовым глаголом.  
  - `sound_url`: Прямая ссылка (URL) на аудиофайл.  
  - `false_friends`: Список ложных друзей (если есть).  
  
### `Translation`  
  
Представляет перевод слова или фразы.  
  
- **Атрибуты**:  
  - `text`: Текст перевода.  
  - `note`: Примечания к переводу.  
  
### `Example`  
  
Представляет пример использования слова.  
  
- **Атрибуты**:  
  - `text`: Пример предложения.  
  - `sound_url`: Объект `Pronunciation` для произношения примера.  

## Исключения (Exceptions)

Библиотека предоставляет следующие пользовательские исключения:

### `SkyConnectorError`

Исключение, возникающее при отсутствии соединения с сервером.

```
from skyengdict.exc import SkyConnectorError

try:
    async with Dictionary() as dictionary:
        await dictionary.words("example")    
except SkyConnectorError:
    print("Ошибка соединения с сервером SkyEng.")
```

### `WordsNotFound`

Исключение, возникающее, если слово не найдено.

```
from skyengdict.exc import WordsNotFound

try:
    async with Dictionary() as dictionary:
        word = await dictionary.words("nonexistentword0101010")
except WordsNotFound:
    print("Слово не найдено.")
```

### `MeaningsNotFound`

Исключение, возникающее, если значения слова не найдены.

```
from skyengdict.exc import MeaningsNotFound

try:
    async with Dictionary() as dictionary:
        meaning = await dictionary.meaning(1000)
except MeaningsNotFound:
    print("Значения для слова не найдены.")
```

## Предложения

Присоединяйтесь к обсуждению и развитию проекта. Буду рад вашим предложениям и пулреквестам. Мои другие текущие проекты читайте в [моем Telegram-канале](https://t.me/crunch_brain). 

## Лицензия  
  
Эта библиотека лицензирована под лицензией MIT.