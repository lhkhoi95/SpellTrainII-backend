import json
import random
from typing import List

from api.models.models import Word
from api.utils.SpellTrainII_AI import SpellTrain2AI

LANGUAGE_ORIGINS = [
    "Old English",
    "Latin",
    "Greek",
    "French",
    "Spanish",
    "Italian",
    "German",
    "Japanese",
    "Chinese",
    "Korean",
    "Arabic",
    "Hindi",
    "Russian",
    "Portuguese",
    "Dutch",
    "Swedish",
    "Norwegian",
    "Danish",
    "Finnish",
    "Turkish",
    "Hungarian",
    "Czech",
    "Polish",
    "Romanian",
    "Bulgarian",
    "Croatian",
    "Serbian",
    "Slovak",
    "Slovenian",
    "Ukrainian",
    "Belarusian",
    "Lithuanian",
    "Latvian",
    "Estonian",
    "Georgian",
    "Armenian",
    "Azerbaijani",
    "Kazakh",
    "Uzbek",
    "Turkmen",
    "Kyrgyz",
    "Tajik",
    "Mongolian",
    "Vietnamese",
    "Thai",
    "Burmese",
    "Khmer",
    "Lao",
    "Indonesian",
    "Malay",
    "Filipino",
    "Hawaiian",
    "Maori",
    "Samoan",
    "Tongan",
    "Fijian",
    "Tahitian",
    "Marquesan",
    "Rapa Nui",
    "Rarotongan",
    "Tahitian",
    "Hawaiian",
    "Maori",
    "Samoan",
    "Tongan",
    "Fijian",
    "Tahitian",
    "Marquesan",
    "Rapa Nui",
    "Rarotongan",
    "Tahitian",
    "Hawaiian",
]


class Game:
    def __init__(self, words: List[Word], level: int = 1):
        self.words_bank: List[Word] = sorted(
            words, key=lambda word_obj: len(word_obj.word), reverse=True)
        self.games_bank = []
        self.level = level

    def generate_games(self):
        self.games_bank = {
            "spellWord": self.spell_word(),
            "quizOrigin": self.quiz_origin(),
            "hangman": self.hangman(),
            "findMissingLetter": self.find_missing_letter(),
            "matchingPair": self.matching_pair(),
            "chooseSpokenWord": self.choose_spoken_word()
        }

        return self.games_bank

    def spell_word(self):
        spell_word_bank = []
        for word_obj in self.words_bank:
            spell_word_bank.append({
                "gameTitle": "Spell the Word",
                "word": word_obj.word,
                "audioUrl": word_obj.audioUrl,
            })

        return spell_word_bank

    def quiz_origin(self):
        quizzes_origin_bank = []

        for word_obj in self.words_bank:
            origin = word_obj.languageOrigin
            while True:
                options = random.sample(LANGUAGE_ORIGINS, k=3)
                if origin not in options:
                    options.append(origin)
                    random.shuffle(options)
                    break

            quizzes_origin_bank.append({
                "gameTitle": "Quiz of Origin",
                "question": "What is the origin of the word '{}'?".format(word_obj.word),
                "options": options,
                "correctAnswer": origin,
            })

        return quizzes_origin_bank

    def hangman(self):
        right_usage_bank = []
        for word_obj in self.words_bank:
            usage = word_obj.usage.lower()
            word_to_hide = word_obj.word.lower()
            usage_with_blanks = usage.replace(
                word_to_hide, len(word_obj.word) * '_').capitalize()

            right_usage_bank.append({
                "gameTitle": "Guess the Word",
                "defaultAttempts": 6,
                "usageWithBlanks": usage_with_blanks,
                "correctAnswer": word_obj.word,
            })

        return right_usage_bank

    def find_missing_letter(self):
        find_missing_letter_bank = []
        for word_obj in self.words_bank:
            while True:
                letter_index = random.randint(0, len(word_obj.word) - 1)
                if word_obj.word[letter_index] != ' ':
                    break

            word_with_blanks = word_obj.word[:letter_index] + \
                '_' + word_obj.word[letter_index + 1:]
            find_missing_letter_bank.append({
                "gameTitle": "Find the Missing Letter",
                "wordWithMissingLetter": word_with_blanks,
                "correctAnswer": word_obj.word[letter_index],
            })

        return find_missing_letter_bank

    def matching_pair(self):
        matching_pairs_bank = []
        for i in range(len(self.words_bank)):
            word_objs = random.sample(self.words_bank, k=3)
            words = []
            pronunciations = []
            correct_pairs = []
            # Create a list of correct pairs
            for word_obj in word_objs:
                words.append(word_obj.word)
                pronunciations.append(word_obj.alternatePronunciation)
                correct_pairs.append({
                    str(word_obj.word): str(word_obj.alternatePronunciation)
                })

            # Shuffle the words and pronunciations
            random.shuffle(pronunciations)
            random.shuffle(words)
            shuffled_pairs = []

            # Create a list of shuffled pairs
            for i in range(len(words)):
                shuffled_pairs.append({
                    str(words[i]): str(pronunciations[i])
                })

            matching_pairs_bank.append({
                "gameTitle": "Matching Pairs",
                "correctPairs": correct_pairs,
                "shuffledPairs": shuffled_pairs
            })

        return matching_pairs_bank

    def choose_spoken_word(self):
        choose_spoken_word_bank = []
        for word_obj in self.words_bank:
            # Select another 4 random words that are not the same as the word
            other_words = random.sample(
                [w for w in self.words_bank if w != word_obj], k=4)
            options = [word_obj.word] + [w.word for w in other_words]
            random.shuffle(options)
            choose_spoken_word_bank.append({
                "gameTitle": "Choose the Spoken Word",
                "audioUrl": word_obj.audioUrl,
                "options": options,
                "correctAnswer": word_obj.word
            })

        return choose_spoken_word_bank
