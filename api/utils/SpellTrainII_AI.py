import json
import os
import google.generativeai as genai
from typing import List, Optional
from devtools import pprint
from fastapi import HTTPException
from openai import OpenAI, OpenAIError
from api.schemas.schemas import EvaluatedTopic, WordInfo


class SpellTrain2AI:
    _NUMB_OF_WORDS = 30
    _RETRY_COUNT = 1

    def __init__(self):
        """
            OpenAI available models:
            - gpt-3.5-turbo-1106
            - gpt-4-1106-preview

            Google Gemini available models:
            - gemini-pro
        """
        self.openai_model = 'gpt-3.5-turbo-1106'
        self.openai_gpt4_model = 'gpt-4-1106-preview'
        self.gemini_model = 'gemini-pro'
        self.default_word_details = WordInfo(
            definition="",
            rootOrigin="",
            usage="",
            languageOrigin="",
            partsOfSpeech="",
            alternatePronunciation=""
        )

    def evaluate_topic(self, topic: str) -> EvaluatedTopic:
        """
        Evaluates whether a given topic is a valid Spelling Bee topic.

        Args:
            topic (str): The topic to be evaluated.

        Returns:
            EvaluatedTopic: An object representing the evaluation result, including whether the topic is valid and the reason.

        Raises:
            HTTPException: If there is an error evaluating the topic.
        """
        client = self._openai_client()
        user_prompt = f'Is "{topic}" a valid Spelling Bee topic? Why or why not?'

        messages = [
            {'role': 'system', 'content': 'You are a helpful dictionary assistant that evaluates whether a topic is a valid Spelling Bee topic.'},
            {'role': 'system', 'content': 'A valid spelling bee topic encompasses a clear category or subject area with enough scope and depth to generate an appropriate word list, but avoids overly niche or sensitive subjects.'},
            {'role': 'system',
                'content': 'The JSON response should be in the following format: {"isValid": true, "reason": "why is a suitable spelling bee topic"} or {"isValid": false, "reason": "why is not a suitable spelling bee topic"}'},
            {'role': 'system', 'content': 'The reason should be within 10 words.'},
            {'role': 'user', 'content': user_prompt},
        ]
        try:
            completion = client.chat.completions.create(
                messages=messages,
                model=self.openai_model,
                response_format={"type": "json_object"},
                temperature=0
            )
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=500, detail="Error evaluating Topic. Please try again later.")

        json_response = json.loads(completion.choices[0].message.content)

        # Convert to EvaluatedTopic type and return
        return EvaluatedTopic.model_validate(json_response)

    def get_word_list(self, topic: str, existing_words: Optional[List] = None, model: Optional[str] = 'gpt-3.5-turbo-1106') -> list[str]:
        """
        Retrieves a list of spelling bee words related to the given topic.

        Args:
            topic (str): The topic for which to retrieve the words.
            existing_words (Optional[List], optional): A list of existing words to avoid repeating. Defaults to None.
            model (Optional[str], optional): The OpenAI model to use for generating the words. Defaults to 'gpt-3.5-turbo-1106'.

        Returns:
            list[str]: A list of spelling bee words related to the topic.
        """
        client = self._openai_client()
        user_prompt = f'Provide {self._NUMB_OF_WORDS} spelling bee words in English related to the topic: {topic}.'

        messages = [
            {'role': 'system', 'content': 'You are a helpful dictionary. You are asked to provide a list of words on a topic.'},
            {'role': 'system',
                'content': 'The JSON response should be in the following format: {"words": ["word1", "word2", "word3"]}'},
            {'role': 'system', 'content': 'All the key-value pairs cannot be empty.'},
            {'role': 'user', 'content': user_prompt},
        ]

        if existing_words is not None:
            messages.append(
                {'role': 'system', 'content': f'Do not repeat any words from the following list: {existing_words}'})

        completion = client.chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=messages,
        )

        self._print_cost(completion)

        json_response = json.loads(completion.choices[0].message.content)

        word_list = list(json_response['words'])
        # Remove duplicates
        if existing_words is not None:
            word_list = [
                word for word in word_list if word not in existing_words]

        return word_list

    def get_word_details(self, word: str, topic: str) -> WordInfo:
        """
        Retrieves the details of a word using different AI models.

        Args:
            word (str): The word to retrieve details for.
            topic (str): The topic associated with the word.

        Returns:
            WordInfo: The details of the word.

        Raises:
            Exception: If an error occurs while retrieving word details from any of the models.
        """

        models = [
            ("Google Gemini AI", self._get_word_details_from_GEMINI_AI, "gemini-pro"),
            ("OpenAI gpt-3.5-turbo-1106",
             self._get_word_details_from_OPENAI, self.openai_model),
            ("OpenAI gpt-4-1106-preview",
             self._get_word_details_from_OPENAI, self.openai_gpt4_model),
        ]

        results_with_unknown = []

        for model_name, get_details_func, model in models:
            print(f"\nTopic: {topic}\nModel: {model_name}")
            try:
                word_details: WordInfo = get_details_func(
                    word, topic, model)

                undesired_results = self._validate_word_info(word_details)

                if len(undesired_results) == 0:
                    print('Word: ', word)
                    pprint(word_details)
                    print(f"{model_name} succeeded.")
                    return word_details

                print(f"{model_name} failed.")
                # Append results to list
                results_with_unknown.append(word_details)
            except Exception as e:
                print(e)
                print(f"{model_name} failed.")
                continue

        return self._merge_results(results_with_unknown)

    def _openai_client(self) -> OpenAI:
        """
        Returns an instance of the OpenAI client.

        Raises:
            HTTPException: If there is an error configuring the OpenAI API Key.

        Returns:
            OpenAI: An instance of the OpenAI client.
        """
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            return client
        except OpenAIError:
            raise HTTPException(
                status_code=500, detail="Error configuring OpenAI API Key")

    def _google_gemini_client(self, model: str = 'gemini-pro') -> genai.GenerativeModel:
        """
        Initializes and configures the Google Gemini client.

        Args:
            model (str): The model to use for the Gemini client. Defaults to 'gemini-pro'.

        Returns:
            genai.GenerativeModel: The configured Gemini client.

        Raises:
            HTTPException: If there is an error configuring the Google Gemini API Key.
        """
        try:
            genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
            gemini = genai.GenerativeModel(model)

            return gemini
        except Exception:
            raise HTTPException(
                status_code=500, detail="Error configuring Google Gemini API Key")

    def _get_word_details_from_GEMINI_AI(self, word: str, topic: str, default_model='gemini-pro') -> WordInfo:
        """
        Retrieves word details from the GEMINI AI model.

        Args:
            word (str): The word for which to retrieve details.
            topic (str): The topic related to the word.
            default_model (str, optional): The default GEMINI AI model to use. Defaults to 'gemini-pro'.

        Returns:
            WordInfo: An object containing the details of the word.

        Raises:
            Exception: If an error occurs during the retrieval process.
        """
        client = self._google_gemini_client(model=default_model)
        config = {
            "temperature": 0
        }
        prompt = f'The word "{word}" is related to the topic "{topic}". Provide information about this word: "{word}". The JSON response should be in the following format: {{"word": "word", "definition": "simple definition within 7 words", "rootOrigin": "root of origin", "usage": "usage of the word in a short sentence", "languageOrigin": "country where the the word comes from", "partsOfSpeech": "parts of speech", "alternatePronunciation": "International Phonetic Alphabet (IPA) pronunciation of the word."}}'

        for i in range(self._RETRY_COUNT):
            try:
                response = client.generate_content(
                    prompt, generation_config=config)

                # Extract JSON response starting from the first '{' to the last '}'
                json_text = response.text[response.text.find(
                    '{'):response.text.rfind('}') + 1]

                # print("JSON response: ", json.dumps(
                #     json.loads(json_text), indent=1))

                json_response = json.loads(json_text)

                # Convert partsOfSpeech to string (noun, verb, etc.)
                if isinstance(json_response['partsOfSpeech'], list):
                    json_response['partsOfSpeech'] = ', '.join(
                        json_response['partsOfSpeech'])

                # Convert to WordInfo type
                word_info = WordInfo(**json_response)

                return word_info
            except Exception as e:
                print("Gemini Error: ", e)
                print(response.prompt_feedback)
                return self.default_word_details

    def _get_word_details_from_OPENAI(self, word: str, topic: str, model: str) -> WordInfo:
        """
        Retrieves word details from the OpenAI API.

        Args:
            word (str): The word for which to retrieve details.
            topic (str): The topic related to the word.
            model (str): The model to use for generating the response.

        Returns:
            WordInfo: An object containing the word details.

        Raises:
            Exception: If there is an error parsing the JSON response.
        """
        client = self._openai_client()

        user_prompt = f'The word "{word}" is related to the topic "{topic}". Provide information about this word: "{word}".'

        messages = [
            {'role': 'system', 'content': 'You are a helpful dictionary assistant designed to output JSON.'},
            {'role': 'system',
                'content': 'The JSON response should be in the following format: {"word": "word", "definition": "simple definition within 7 words", "rootOrigin": "root of origin", "usage": "usage of the word in a short sentence", "languageOrigin": "country where the the word comes from", "partsOfSpeech": "parts of speech", "alternatePronunciation": "International Phonetic Alphabet (IPA) pronunciation of the word.}'},
            {'role': 'system', 'content': 'If you have no result for a key-value pairs, leave it as "Unknown"'},
            {'role': 'user', 'content': user_prompt},
        ]

        completion = client.chat.completions.create(
            messages=messages,
            model=model,
            response_format={"type": "json_object"},
        )

        self._print_cost(completion)

        json_response = dict(json.loads(completion.choices[0].message.content))

        # Try to parse json_response to WordInfo
        try:
            word_info = WordInfo(**json_response)

            return word_info
        except Exception as e:
            print(e)
            print("Failed to parse json_response to WordInfo.")
            return self.default_word_details

    def _print_cost(self, completion):
        """
        Prints the total tokens used and the corresponding cost.

        Parameters:
        - completion: The completion object.

        Returns:
        None
        """
        # print the total tokens used
        print(completion.usage.total_tokens)
        total_cost = (completion.usage.total_tokens / 1000) * 0.0010
        print(f"total cost: ${total_cost}")

    def _merge_results(self, fail_results: List[WordInfo]):
        """
        Merges the results from failed word lookups into a combined result.

        Args:
            fail_results (List[WordInfo]): A list of WordInfo objects containing the failed word lookups.

        Returns:
            WordInfo: The combined result of the failed word lookups.
        """
        invalid_fields = ["", "unknown", "n/a", "none"]
        combined_results = self.default_word_details

        for word in fail_results:
            if word.definition.lower() not in invalid_fields:
                combined_results.definition = word.definition
            if word.rootOrigin.lower() not in invalid_fields:
                combined_results.rootOrigin = word.rootOrigin
            if word.usage.lower() not in invalid_fields:
                combined_results.usage = word.usage
            if word.languageOrigin.lower() not in invalid_fields:
                combined_results.languageOrigin = word.languageOrigin
            if word.partsOfSpeech.lower() not in invalid_fields:
                combined_results.partsOfSpeech = word.partsOfSpeech
            if word.alternatePronunciation.lower() not in invalid_fields:
                combined_results.alternatePronunciation = word.alternatePronunciation
        print("FINAL RESULT: ", combined_results)
        return combined_results

    def _validate_word_info(self, word: WordInfo):
        """
        Validates the given WordInfo object and returns a list of unknown fields.

        Args:
            word (WordInfo): The WordInfo object to be validated.

        Returns:
            list: A list of unknown fields in the WordInfo object.
        """
        invalid_values = ["", "unknown", "n/a", "none"]
        unknown_fields = []

        if word.definition.lower() in invalid_values:
            unknown_fields.append("definition")
        if word.rootOrigin.lower() in invalid_values:
            unknown_fields.append("rootOrigin")
        if word.usage.lower() in invalid_values:
            unknown_fields.append("usage")
        if word.languageOrigin.lower() in invalid_values:
            unknown_fields.append("languageOrigin")
        if word.partsOfSpeech.lower() in invalid_values:
            unknown_fields.append("partsOfSpeech")
        if word.alternatePronunciation.lower() in invalid_values:
            unknown_fields.append("alternatePronunciation")

        return unknown_fields
