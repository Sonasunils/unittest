import unittest

from unittest.mock import mock_open, patch
from hangman import *
import random
import sys
from io import StringIO
import json

class TestHangman(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"words": ["test", "hangman", "python"]}))
    def test_load_words_from_file(self, mock_file):
        expected_words = ["test", "hangman", "python"]
        file_name = "dummy_file.json"
        
        words = load_words_from_file(file_name)
        
        # Check if the open function was called with the correct file name
        mock_file.assert_called_with(file_name, 'r')
        
        # Check if the function returns the correct list of words
        self.assertEqual(words, expected_words)
    wordlist = ['testword', 'example', 'hangman', 'python', 'unittest']

    @patch('hangman.random.choice')
    def test_get_random_word(self, mock_random_choice):
        mock_random_choice.return_value = 'python'
        word = get_random_word(self.wordlist)
        self.assertEqual(word, 'python')

    def test_get_blanks(self):
        word = 'python'
        blanks = get_blanks(word)
        self.assertEqual(blanks, '______')

    def test_update_blanks(self):
        blanks = update_blanks("python", "pythn")
        self.assertEqual(blanks, "pyth_n")

    def test_count_missed_letters(self):
        
        self.assertEqual(count_missed_letters('ab'), 2)
        self.assertEqual(count_missed_letters('abcdef'), 6)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_hangman_initial(self, mock_stdout):
        display_hangman(0)
        self.assertEqual(mock_stdout.getvalue().strip(), HANGMAN_PICS[0].strip())

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_hangman_final(self, mock_stdout):
        display_hangman(6)
        self.assertEqual(mock_stdout.getvalue().strip(), HANGMAN_PICS[6].strip())
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_blanks(self, mock_stdout):
        blanks = "_ a _ _ "
        display_blanks(blanks)
        self.assertEqual(mock_stdout.getvalue().strip(), "_   a   _   _")
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_remaining_info(self, mock_stdout):
        missed_letters = 'aeiou'
        blanks = 'a_ _ _ _'
        display_remaining_info(missed_letters, blanks)
        expected_output = "No of chances remaining = 1\nYou have to uncover 4 more letters"
        self.assertEqual(mock_stdout.getvalue().strip(), expected_output)
    @patch('hangman.count_missed_letters', return_value=3)
    @patch('hangman.update_blanks', return_value='a_ _ le')
    @patch('hangman.display_hangman')  # Mocked, no return value needed
    @patch('hangman.display_missed_letters')  # Mocked, no return value needed
    @patch('hangman.display_remaining_info')  # Mocked, no return value needed
    @patch('hangman.display_blanks')  # Mocked, no return value needed
    def test_display_board(self, mock_display_blanks, mock_display_remaining_info, mock_display_missed_letters,
                           mock_display_hangman, mock_update_blanks, mock_count_missed_letters):
        # Call the function under test
        missed_letters = 'xyz'
        correct_letters = 'ae'
        secret_word = 'apple'
        display_board(missed_letters, correct_letters, secret_word)

        # Assert that display_hangman is called with the correct argument
        mock_display_hangman.assert_called_once_with(3)

        # Assert that the other display functions are called
        mock_display_missed_letters.assert_called_once_with(missed_letters)
        mock_display_remaining_info.assert_called_once()
        mock_display_blanks.assert_called_once_with('a_ _ le')
    @patch('builtins.input', side_effect=['a'])
    @patch('hangman.validate_guess', return_value=True)
    def test_get_guess_valid(self, mock_validate_guess, mock_input):
        already_guessed = ['b', 'c']
        expected_guess = 'a'
        
        # Call the function under test
        guess = get_guess(already_guessed)

        # Assertions
        self.assertEqual(guess, expected_guess)
        mock_validate_guess.assert_called_once_with('a', already_guessed)
        mock_input.assert_called_once()

    @patch('builtins.input', side_effect=['1', 'ab', 'd'])
    @patch('hangman.validate_guess', side_effect=[False, False, True])
    def test_get_guess_invalid_then_valid(self, mock_validate_guess, mock_input):
        already_guessed = ['x', 'y', 'z']
        expected_guess = 'd'
        
        # Call the function under test
        guess = get_guess(already_guessed)

        # Assertions
        self.assertEqual(guess, expected_guess)
        self.assertEqual(mock_validate_guess.call_count, 3)
        mock_input.assert_any_call()  # Asserts that input() was called at least once

    def test_validate_guess_valid(self):
        guess = 'a'
        already_guessed = ['b', 'c']
        expected_result = True

        # Call the function under test
        result = validate_guess(guess, already_guessed)

        # Assertion
        self.assertEqual(result, expected_result)

    def test_validate_guess_invalid(self):
        guess = '1'
        already_guessed = ['a', 'b']
        expected_result = False

        # Call the function under test
        result = validate_guess(guess, already_guessed)

        # Assertions
        self.assertEqual(result, expected_result)
    @patch('builtins.input', side_effect=['yes'])
    def test_play_again_yes(self, mock_input):
        self.assertTrue(play_again())
        mock_input.assert_called_once()

    @patch('builtins.input', side_effect=['no'])
    def test_play_again_no(self, mock_input):
        self.assertFalse(play_again())
        mock_input.assert_called_once()
    def test_check_win_true(self):
        self.assertTrue(check_win(['a', 'p', 'l', 'e'], 'apple'))

    def test_check_win_false(self):
        self.assertFalse(check_win(['a', 'p', 'l'], 'apple'))

    def test_check_win_empty_correct_letters(self):
        self.assertFalse(check_win([], 'apple'))

    def test_check_win_empty_secret_word(self):
        self.assertTrue(check_win(['a', 'p', 'l', 'e'], ''))
    def test_check_loss_false(self):
        self.assertFalse(check_loss(['a', 'b', 'c']))

    def test_check_loss_true(self):
        self.assertTrue(check_loss(['a', 'b', 'c', 'd', 'e', 'f', 'g']))

    def test_check_loss_exact_limit(self):
        self.assertTrue(check_loss(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']))

    def test_check_loss_over_limit(self):
        self.assertTrue(check_loss(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']))
    def test_check_loss_no_missed_letters(self):
        # Test with no missed letters
        missed_letters = []
        self.assertFalse(check_loss(missed_letters))
    def test_no_missed_letters(self):
        # Test with no missed letters
        missed_letters = []
        expected_remaining_chances = len(HANGMAN_PICS) - 1
        self.assertEqual(calculate_remaining_chances(missed_letters), expected_remaining_chances)

    def test_some_missed_letters(self):
        # Test with some missed letters
        missed_letters = ['a', 'b']
        expected_remaining_chances = (len(HANGMAN_PICS) - 1) - len(missed_letters)
        self.assertEqual(calculate_remaining_chances(missed_letters), expected_remaining_chances)

    def test_max_missed_letters(self):
        # Test with the maximum missed letters
        missed_letters = ['a', 'b', 'c', 'd', 'e', 'f']
        expected_remaining_chances = 0
        self.assertEqual(calculate_remaining_chances(missed_letters), expected_remaining_chances)

    def test_over_max_missed_letters(self):
        # Test with more than the maximum missed letters
        missed_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        expected_remaining_chances = -1
        self.assertEqual(calculate_remaining_chances(missed_letters), expected_remaining_chances)
    def test_no_missed_letters(self):
        # Test with no missed letters
        missed_letters = []
        expected_remaining_chances = len(HANGMAN_PICS) - 1
        self.assertEqual(calculate_remaining_chances(missed_letters), expected_remaining_chances)

    def test_some_missed_letters(self):
        # Test with some missed letters
        missed_letters = ['a', 'b']
        expected_remaining_chances = (len(HANGMAN_PICS) - 1) - len(missed_letters)
        self.assertEqual(calculate_remaining_chances(missed_letters), expected_remaining_chances)
    def test_correct_guess_not_won(self):
        guess = 'e'
        missed_letters = ''
        correct_letters = 'tst'
        secret_word = 'test'
        
        new_missed_letters, new_correct_letters, game_is_done = update_game_state(guess, missed_letters, correct_letters, secret_word)
        
        self.assertEqual(new_missed_letters, '')
        self.assertEqual(new_correct_letters, 'tste')
        self.assertTrue(game_is_done)

    def test_correct_guess_and_won(self):
        guess = 'e'
        missed_letters = ''
        correct_letters = 'tst'
        secret_word = 'test'
        
        # Adjust correct letters to ensure game is won
        correct_letters = 'tst'
        
        new_missed_letters, new_correct_letters, game_is_done = update_game_state(guess, missed_letters, correct_letters, secret_word)
        
        self.assertEqual(new_missed_letters, '')
        self.assertEqual(new_correct_letters, 'tste')
        self.assertTrue(game_is_done)

    def test_incorrect_guess(self):
        guess = 'x'
        missed_letters = 'abcde'
        correct_letters = 't'
        secret_word = 'test'
        
        new_missed_letters, new_correct_letters, game_is_done = update_game_state(guess, missed_letters, correct_letters, secret_word)
        
        self.assertEqual(new_missed_letters, 'abcdex')
        self.assertEqual(new_correct_letters, 't')
        self.assertTrue(game_is_done)

    def test_incorrect_guess_and_loss(self):
        guess = 'x'
        missed_letters = 'abcdef'
        correct_letters = 't'
        secret_word = 'test'
    
        with patch('hangman.display_board') as mock_display_board:
            new_missed_letters, new_correct_letters, game_is_done = update_game_state(guess, missed_letters, correct_letters, secret_word)
    
        self.assertEqual(new_missed_letters, 'abcdefx')
        self.assertEqual(new_correct_letters, 't')
        self.assertTrue(game_is_done)
        mock_display_board.assert_called_once()
   
if __name__ == '__main__':
    unittest.main()

