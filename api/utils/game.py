import json
import random
from typing import List
from api.models.models import Word


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
TOTAL_LEVEL = 8


class Game:
    def __init__(self, words: List[Word]):
        self.words_bank: List[Word] = words
        self.challenge = dict()
        self.spell_word_bank = self.spell_word()
        self.quizzes_origin_bank = self.quiz_origin()
        self.hangman_bank = self.hangman()
        self.find_missing_letter_bank = self.find_missing_letter()
        self.matching_pairs_bank = self.matching_pair()
        self.choose_spoken_word_bank = self.choose_spoken_word()
        self.find_correct_word_bank = self.find_correct_word()

    def generate_games(self):
        game_banks = [
            self.find_missing_letter_bank,
            self.find_correct_word_bank,
            self.spell_word_bank,
            self.quizzes_origin_bank,
            self.hangman_bank,
            self.matching_pairs_bank,
            self.choose_spoken_word_bank,
            # more games...
        ]

        for i in range(TOTAL_LEVEL):
            level = i + 1
            self.challenge[f"level{level}"] = []
            # Fill the current level with games. Each level has level number of games
            while len(self.challenge[f"level{level}"]) < level:
                # Choose a random game from the bank
                game_bank = random.choice(game_banks)
                # Add the game to the current level of the challenge
                if game_bank:
                    self.challenge[f"level{level}"].append(game_bank.pop())

        return self.challenge

    def spell_word(self):
        spell_word_bank = []
        for word_obj in self.words_bank:
            spell_word_bank.append({
                "gameType": "spellWord",
                "gameTitle": "Spell the Word",
                "word": word_obj.word,
                "audioUrl": word_obj.audioUrl,
            })

        random.shuffle(spell_word_bank)

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
                "gameType": "quizOrigin",
                "gameTitle": "Quiz of Origin",
                "question": "What is the origin of the word '{}'?".format(word_obj.word),
                "options": options,
                "correctAnswer": origin,
            })
        random.shuffle(quizzes_origin_bank)
        return quizzes_origin_bank

    def hangman(self):
        right_usage_bank = []
        for word_obj in self.words_bank:
            usage = word_obj.usage.lower()
            word_to_hide = word_obj.word.lower()
            usage_with_blanks = usage.replace(
                word_to_hide, len(word_obj.word) * '_').capitalize()

            right_usage_bank.append({
                "gameType": "hangman",
                "gameTitle": "Guess the Word",
                "defaultAttempts": 6,
                "usageWithBlanks": usage_with_blanks,
                "correctAnswer": word_obj.word,
            })
        random.shuffle(right_usage_bank)
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
                "gameType": "findMissingLetter",
                "gameTitle": "Find the Missing Letter",
                "wordWithMissingLetter": word_with_blanks,
                "correctAnswer": word_obj.word[letter_index],
            })
        random.shuffle(find_missing_letter_bank)
        return find_missing_letter_bank

    def matching_pair(self):
        matching_pairs_bank = []
        for i in range(0, len(self.words_bank), 3):
            word_objs = random.sample(self.words_bank, k=3)
            words = []
            pronunciations = []
            correct_pairs = []
            # Create a list of correct pairs
            for word_obj in word_objs:
                words.append(word_obj.word)
                pronunciations.append(word_obj.audioUrl)
                correct_pairs.append({
                    str(word_obj.word): str(word_obj.audioUrl)
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
                "gameType": "matchingPair",
                "gameTitle": "Match the word with its pronunciation",
                "correctPairs": correct_pairs,
                "shuffledPairs": shuffled_pairs
            })
        random.shuffle(matching_pairs_bank)
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
                "gameType": "chooseSpokenWord",
                "gameTitle": "Choose the Spoken Word",
                "audioUrl": word_obj.audioUrl,
                "options": options,
                "correctAnswer": word_obj.word
            })
        random.shuffle(choose_spoken_word_bank)
        return choose_spoken_word_bank

    def find_correct_word(self):
        find_correct_word_bank = []
        for word_obj in self.words_bank:
            words = [word_obj.word]
            while len(words) < 4:
                random_word = random.choice(self.words_bank)
                if random_word.word not in words:
                    words.append(random_word.word)

            random.shuffle(words)
            find_correct_word_bank.append({
                "gameType": "findCorrectWord",
                "gameTitle": "Choose the Word that matches the Definition",
                "definition": word_obj.definition.capitalize(),
                "options": words,
                "correctAnswer": word_obj.word
            })
        random.shuffle(find_correct_word_bank)
        return find_correct_word_bank
