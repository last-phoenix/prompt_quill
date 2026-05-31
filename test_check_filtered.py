import sys
import os

sys.path.append(os.path.abspath('llama_index_pq/pq'))

# Mock numpy
class MockNumpy:
    def all(self, *args, **kwargs):
        pass
sys.modules['numpy'] = MockNumpy()

import shared

class DummyG:
    def __init__(self):
        self.settings_data = {
            'sailing': {
                'sail_filter_not_text': '',
                'sail_filter_text': ''
            }
        }

shared.g = DummyG()

def test():
    # Test sail_filter_text (blacklist) OR logic
    shared.g.settings_data['sailing']['sail_filter_text'] = 'bad, ugly'
    shared.g.settings_data['sailing']['sail_filter_not_text'] = ''

    prompt1 = "This is a bad prompt."
    prompt2 = "This is an ugly prompt."
    prompt3 = "This is a good prompt."

    assert shared.check_filtered(prompt1) == True, "Failed to filter 'bad'"
    assert shared.check_filtered(prompt2) == True, "Failed to filter 'ugly'"
    assert shared.check_filtered(prompt3) == False, "Incorrectly filtered 'good'"

    # Test sail_filter_not_text (whitelist) OR logic
    shared.g.settings_data['sailing']['sail_filter_text'] = ''
    shared.g.settings_data['sailing']['sail_filter_not_text'] = 'good, nice'

    prompt4 = "This is a good prompt."
    prompt5 = "This is a nice prompt."
    prompt6 = "This is a bad prompt."

    assert shared.check_filtered(prompt4) == False, "Incorrectly filtered 'good'"
    assert shared.check_filtered(prompt5) == False, "Incorrectly filtered 'nice'"
    assert shared.check_filtered(prompt6) == True, "Failed to filter 'bad' (not in whitelist)"

    # Test case sensitivity (since parse_filter_set lowercases the filter words)
    # The prompt should match if it contains the *exact* lowercase word from the filter.
    shared.g.settings_data['sailing']['sail_filter_text'] = 'bad'
    shared.g.settings_data['sailing']['sail_filter_not_text'] = ''

    # "bad" is in the prompt, so it gets filtered
    assert shared.check_filtered("This is a bad prompt.") == True
    # "Bad" is in the prompt, but it's not lowercase "bad", so it should NOT be filtered
    assert shared.check_filtered("This is a Bad prompt.") == False

    print("All tests passed!")

if __name__ == '__main__':
    test()
