# DEPRECATED: This file is no longer used. It is kept for reference purposes only.

from typing import List
import json
from api.schemas.schemas import EvaluatedTopic, WordInfo
from api.dependencies import openai_client, google_gemini_client
from devtools import pprint

"""
    OpenAI available models:
    - gpt-3.5-turbo-1106
    - gpt-4-1106-preview
    
    Google Gemini available models:
    - gemini-pro
"""
NUMB_OF_WORDS = 30
GEMINI_TRIALS = 1


def get_word_list_from_AI(topic: str, get_more=False, existing_words=[]):

    client = openai_client()

    user_prompt = f'Provide {NUMB_OF_WORDS} spelling bee words in English related to the topic: {topic}.'

    if get_more:
        words_to_str = ', '.join(existing_words)
        user_prompt = f"Provide {NUMB_OF_WORDS} spelling bee words in English related to the topic: '{topic}', excluding the following words (case-insensitive): {words_to_str}."

    messages = [
        {'role': 'system', 'content': 'You are a helpful dictionary. You are asked to provide a list of words on a topic.'},
        {'role': 'system',
            'content': 'The JSON response should be in the following format: {"words": ["word1", "word2", "word3"]}'},
        {'role': 'system', 'content': 'All the key-value pairs cannot be empty.'},
        {'role': 'user', 'content': user_prompt},
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=messages,
    )

    print_cost(completion)

    json_response = json.loads(completion.choices[0].message.content)

    word_list = list(json_response['words'])

    return word_list


def get_word_details(word: str, topic: str) -> WordInfo:
    """Retrieves word details from multiple AI models, prioritizing Gemini AI."""
    models = [
        ("Google Gemini AI", get_word_details_from_GEMINI_AI, "gemini-pro"),
        ("OpenAI gpt-3.5-turbo-1106",
         get_word_details_from_OPENAI, "gpt-3.5-turbo-1106"),
        ("OpenAI gpt-4-1106-preview",
         get_word_details_from_OPENAI, "gpt-4-1106-preview"),
    ]

    results_with_unknown = []

    for model_name, get_details_func, model in models:
        print(f"\nTopic: {topic}\nModel: {model_name}")
        try:
            word_details: dict = get_details_func(word, topic, model)

            undesired_results = validate_word_info(word_details)

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

    return merge_results(results_with_unknown)


def get_word_details_from_GEMINI_AI(word: str, topic: str, desired_model: str) -> WordInfo:
    client = google_gemini_client(model=desired_model)
    config = {
        "temperature": 0
    }
    prompt = f'The word "{word}" is related to the topic "{topic}". Provide information about this word: "{word}". The JSON response should be in the following format: {{"word": "word", "definition": "simple definition within 7 words", "rootOrigin": "root of origin", "usage": "usage of the word in a short sentence", "languageOrigin": "country where the the word comes from", "partsOfSpeech": "parts of speech", "alternatePronunciation": "International Phonetic Alphabet (IPA) pronunciation of the word."}}'

    for i in range(GEMINI_TRIALS):
        # print("Gemini Pro AI retry count: ", i + 1)
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
            return WordInfo(
                definition="",
                rootOrigin="",
                usage="",
                languageOrigin="",
                partsOfSpeech="",
                alternatePronunciation=""
            )


def get_word_details_from_OPENAI(word: str, topic: str, model: str) -> WordInfo:
    client = openai_client()

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

    print_cost(completion)

    json_response = dict(json.loads(completion.choices[0].message.content))

    # Try to parse json_response to WordInfo
    try:
        word_info = WordInfo(**json_response)

        return word_info
    except Exception as e:
        print(e)
        print("Failed to parse json_response to WordInfo.")
        return WordInfo(
            definition="",
            rootOrigin="",
            usage="",
            languageOrigin="",
            partsOfSpeech="",
            alternatePronunciation=""
        )


def validate_word_info(word: WordInfo):
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


def print_cost(completion):
    # print the total tokens used
    print(completion.usage.total_tokens)
    total_cost = (completion.usage.total_tokens / 1000) * 0.0010
    print(f"total cost: ${total_cost}")


def merge_results(fail_results: List[WordInfo]):
    invalid_fields = ["", "unknown", "n/a", "none"]
    combined_results = WordInfo(
        definition="",
        rootOrigin="",
        usage="",
        languageOrigin="",
        partsOfSpeech="",
        alternatePronunciation=""
    )

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


def evaluate_topic(topic: str, model="gpt-3.5-turbo-1106") -> EvaluatedTopic:
    client = openai_client()

    user_prompt = f'Is "{topic}" a valid Spelling Bee topic? Why or why not?'

    messages = [
        {'role': 'system', 'content': 'You are a helpful dictionary assistant that evaluates whether a topic is a valid Spelling Bee topic.'},
        {'role': 'system', 'content': 'A valid spelling bee topic encompasses a clear category or subject area with enough scope and depth to generate an appropriate word list, but avoids overly niche or sensitive subjects.'},
        {'role': 'system',
            'content': 'The JSON response should be in the following format: {"isValid": true, "reason": "why is a suitable spelling bee topic"} or {"isValid": false, "reason": "why is not a suitable spelling bee topic"}'},
        {'role': 'system', 'content': 'The reason should be within 10 words.'},
        {'role': 'user', 'content': user_prompt},
    ]

    completion = client.chat.completions.create(
        messages=messages,
        model=model,
        response_format={"type": "json_object"},
        temperature=0
    )

    json_response = json.loads(completion.choices[0].message.content)

    # Convert to EvaluatedTopic type and return
    return EvaluatedTopic.model_validate(json_response)


# def get_word_info_from_openAI(word: str, topic: str, client):
#     tools = [{
#         "type": "function",
#         "function": {
#                 "name": "get_word_info",
#                 "description": "Get information about a word related to a topic.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "word": {
#                             "type": "string",
#                             "description": "The word to provide information about."
#                         },
#                         "definition": {
#                             "type": "string",
#                             "description": "brief definition of the word"
#                         },
#                         "rootOrigin": {
#                             "type": "string",
#                             "description": "The root of origin of the word"
#                         },
#                         "usage": {
#                             "type": "string",
#                             "description": "Usage of the word in a sentence"
#                         },
#                         "languageOrigin": {
#                             "type": "string",
#                             "description": "The language origin of the word"
#                         },
#                         "partsOfSpeech": {
#                             "type": "string",
#                             "description": "Parts of speech"
#                         },
#                         "alternatePronunciation": {
#                             "type": "string",
#                             "description": "Alternate pronunciation of the word"
#                         }
#                     }
#                 }
#         }
#     }]
#     messages = [
#         {'role': 'user', 'content': f'The word "{word}" is related to the topic "{topic}". Provide information about this word: "{word}".'},
#     ]
#     response = client.chat.completions.create(
#         model="gpt-4-1106-preview",
#         messages=messages,
#         tools=tools,
#         tool_choice={
#             "type": "function",
#             "function": {"name": "get_word_info"},
#         }
#     )
#     json_response = dict(json.loads(response.choices[0].message.content))
#     print(json_response)

#     return json_response
