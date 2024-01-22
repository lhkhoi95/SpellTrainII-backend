from api.utils.SpellTrainII_AI import SpellTrain2AI


def test_evaluate_input():
    test_cases = [
        # Invalid topics
        ("killing", False),
        ("drug", False),
        ("unknown", False),
        ("weapons", False),
        ("xyz", False),
        ("sexual assault", False),
        ("Abuse", False),
        ("dark magic", False),
        ("Spelling Bee", False),
        ("profanity", False),
        ("controversial", False),
        ("inappropriate", False),
        ("illegal", False),
        ("too obscure", False),
        ("too narrow", False),
        ("unclear", False),
        ("hate speech", False),
        ("violence", False),
        ("racism", False),
        ("terrorism", False),
        ("murder", False),
        ("drugs", False),
        ("firearms", False),
        ("abc", False),
        ("sexual harassment", False),
        ("Domestic Violence", False),
        ("black magic", False),
        ("vulgar language", False),

        # Valid topics
        ("fruit", True),
        ("Harry Potter", True),
        ("Vietnamese cuisine", True),
        ("Geography", True),
        ("Science", True),
        ("History", True),
        ("Literature", True),
        ("Music", True),
        ("Art", True),
        ("Sports", True),
        ("Language Arts", True),
        ("Math", True),
        ("Pop Culture", True),
        ("Food", True),
        ("Movies", True),
        ("Animals", True),
        ("Plants", True),
        ("Countries", True),
        ("Vocabulary", True),
        ("Environment", True),
        ("Technology", True),
        ("Business", True),
        ("Culture", True),
        ("unethical", True),
        ("dangerous", True),
        ("positive", True),
        ("inspiring", True),
        ("vegetable", True),
        ("Lord of the Rings", True),
        ("Italian cuisine", True),
        ("Astronomy", True),
        ("Biology", True),
        ("Politics", True),
        ("Philosophy", True),
        ("Dance", True),
        ("Fashion", True),
        ("Travel", True)
    ]

    unmatched_results = []
    spelltrain2AI = SpellTrain2AI()

    for input_topic, expected_output in test_cases:
        evaluated_result = spelltrain2AI.evaluate_topic(input_topic)
        print('Topic: ', input_topic, ' --> ', 'Valid' if evaluated_result.isValid else 'Invalid',
              ' | ', 'Reason: ', evaluated_result.reason)

        assert isinstance(evaluated_result.isValid, bool)
        # Add unmatched results to the list
        if evaluated_result.isValid != expected_output:
            unmatched_results.append(
                (input_topic, evaluated_result.isValid, expected_output))

    # Print the unmatched results
    print(
        f"\n{len(unmatched_results)}/{len(test_cases)} results are unmatched.")
    for result in unmatched_results:
        print("Topic: ", result[0], " | Actual: ",
              result[1], " | Expected: ", result[2])
