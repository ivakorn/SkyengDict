import asyncio
#from skydict import Dictionary
#from skydict.types import Meaning, BriefMeaning
from src.skydict import Dictionary
from src.skydict.types import Meaning, BriefMeaning
from typing import cast


async def main():
    tasks = []
    try:
        async with Dictionary() as dictionary:
            result = await dictionary.meaning([x for x in range(0,10)])
            for mean in result:
                mean = cast(Meaning, mean)
                print(f"{mean.prefix} {mean.text} ({mean.id})\n"
                      f"    - транскрипция: {mean.transcription}\n"
                      f"    - перевод: {mean.translation}\n"
                      f"    - определение: {mean.definition}\n"
                      f"    - часть речи: {mean.part_of_speech_code.ru}\n"
                      f"    - уровень сложности: {mean.difficulty_level}\n"
                      f"    - ссылка на изображение: {mean.images_url[0]}\n"
                      f"    - ссылка на произношение: {mean.sound_url.female_1}\n"
                      f"    - мнемоника: {mean.mnemonics}\n"
                      f"    - колокация: {mean.properties}\n")

                result = await dictionary.words('любовь')
                for word in result:
                    print(f"- {word.text} ({word.id})")
                    for mean in word.meanings:
                        mean = cast(BriefMeaning, mean)
                        print(f"    - перевод: {mean.translation}\n"
                              f"    - ссылка на изображение: {mean.image_url}\n"
                              f"    - ссылка на произношение: {mean.sound_url.female_1}\n"
                              f"    - транскрипция: {mean.transcription}\n"
                              f"    - перевод: {mean.translation}\n"
                              f"    - часть речи: {mean.part_of_speech_code.ru}\n")
    except Exception as e:
        print("исключение первое:", e)
        for index, item in enumerate(e.args, start=1):
            print(f"#{index} исключение:", item)


    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
