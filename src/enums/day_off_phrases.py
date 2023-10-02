from enums.base_enum import BaseEnum


class DayOffPhrases(BaseEnum):
    PHRASE_0 = None
    PHRASE_1 = "Сегодня день отдыха, друзья!"
    PHRASE_2 = "Доброе утро! Сегодня воскресенье, наслаждайтесь свободным днем."
    PHRASE_3 = "Отличные новости: сегодня воскресенье, вы можете отдохнуть!"
    PHRASE_4 = "Сегодняшний день - это ваш шанс расслабиться, потому что это воскресенье."
    PHRASE_5 = "Сегодня воскресенье, и вы можете насладиться днем без учебы или работы."
    PHRASE_6 = "Не забывайте, что сегодня воскресенье, и у вас есть возможность расслабиться."
    PHRASE_8 = "Поздравляю, вы достигли воскресенья! Время расслабиться и насладиться выходным."
    PHRASE_9 = "Воскресенье пришло, день для отдыха и забавы."
    PHRASE_10 = "Запомните, сегодня воскресенье, и вы заслужили отдых."

    @classmethod
    def get_weights(cls):
        return [3] + [1] * (len(DayOffPhrases.names()) - 1)
