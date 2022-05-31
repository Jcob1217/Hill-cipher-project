import os
import re
import numpy as np
from egcd import egcd
import math
from itertools import product
from pathlib import Path
from os import path


class NoInverse(Exception):
    pass


class NwdNot1(Exception):
    pass


class HillCipher():
    def __init__(self, alphabet=None):
        self.alphabet = "abcdefghijklmnopqrstuvwxyz" if alphabet is None else alphabet
        self.letter_to_index = dict(zip(self.alphabet, range(len(self.alphabet))))
        self.index_to_letter = dict(map(reversed, self.letter_to_index.items()))
        self.modulo = len(self.alphabet)

    @staticmethod
    def gen_for_key(list_of_numbers):
        length = len(list_of_numbers)
        for i in range(length):
            yield list_of_numbers[i]

    @staticmethod
    def split(string, split_len):
        regex = r'(.{%s})' % split_len
        return [x for x in re.split(regex, string) if x]

    def matrix_to_string(self, matrix):
        string_message = ""
        for i in range(len(matrix[0])):
            for j in range(len(matrix)):
                index = int(matrix[j][i])
                string_message += self.index_to_letter[index]
        return string_message

    def solve_equation(self, small_matrix_enc, matrix_know_word, divide=1):
        print(small_matrix_enc,'\n\n\n', matrix_know_word)
        x_inv = np.linalg.solve(small_matrix_enc, matrix_know_word)
        x = np.linalg.inv(x_inv)
        det = int(np.round(np.linalg.det(small_matrix_enc))) 
        det_inv = egcd(det, len(self.alphabet))[1] % (len(self.alphabet)/divide) 
        matrix_modulus_inv = (
                det_inv * np.round(det * np.linalg.inv(x)).astype(int) % len(self.alphabet)/divide)

        matrix_good_key = np.matrix.transpose(matrix_modulus_inv)
        return matrix_good_key.astype(int)

    def get_square_matrix_from_stringkey(self, key: str):
        def is_square(i):
            return i == math.isqrt(i) ** 2

        matrix_key = []
        squared = int(math.sqrt(len(key)))

        if is_square(len(key)):
            key_ints = [str(self.letter_to_index[letter]) for letter in key]
            gen_for_matrix = self.gen_for_key(key_ints)
            for _ in range(squared):
                row = []
                for _ in range(squared):
                    row.append(int(next(gen_for_matrix)))
                matrix_key.append(row)
            return np.array(matrix_key).transpose()
        else:
            raise Exception('Z podanego klucza nie można stworzyć macierzy kwadratowej.')


    def get_inv_matrix_mod(self, matrix_key):

        det = int(np.round(np.linalg.det(matrix_key)))
        det_inv = egcd(det, self.modulo)[1] % self.modulo 
        matrix_modulus_inv = (
                det_inv * np.round(det * np.linalg.inv(matrix_key)).astype(int) % self.modulo
        )

        return matrix_modulus_inv

    def get_fixed_message_and_get_matrix(self, message: str, matrix_key):
        if len(message) % len(matrix_key) != 0:
            for i in range(len(message)):
                message += message[i]
                if len(message) % len(matrix_key) == 0:
                    break

        matrix_message = []
        for letters in self.split(message, len(matrix_key)):
            row = [self.letter_to_index[letter] for letter in letters]
            matrix_message.append(row)
        matrix_message = np.array(matrix_message)
        return matrix_message.transpose(), message


    def check_key_is_invertable(self,matrix_key, modulo):
        def nwd(a, b):
            return nwd(b, a % b) if b else a
        if np.linalg.det(matrix_key) == 0:
            raise NoInverse(
                'Z podanego klucza nie będzie można utworzyć macierzy odwrotnej, gdyż jej wyznacznik wynosi 0.')
        det = int(np.round(np.linalg.det(matrix_key)))
        is_inverse_mod = nwd(det, modulo)

        if is_inverse_mod != 1:
            raise NwdNot1(
                f'Z podanego klucza nie będzie można utworzyć macierzy odwrotnej <strong>mod {int(modulo)}</strong>, '
                f'<strong>gdyż nwd(det(A), {int(modulo)}) '
                'nie wynosi 1 </strong>(gdzie <strong>det(A)</strong> <br>to wyznacznik macierzy A utworzony z podanego klucza) '
                'przykładowe klucze: <strong>vopt, zwyt, wkhhjsnsc, aepqvzxwy, jklimtuprsusvttq ')
        return matrix_key

    def encrypt(self, key: str, message: str):
        matrix_key = self.get_square_matrix_from_stringkey(key)
        self.check_key_is_invertable(matrix_key, self.modulo)
        message_matrix, message_fixed = self.get_fixed_message_and_get_matrix(message, matrix_key)
        matrix_mutipled = np.matmul(matrix_key, message_matrix)
        encryption_matrix = np.remainder(matrix_mutipled, self.modulo)
        encrypted_message_string = self.matrix_to_string(encryption_matrix)
        return message_fixed, matrix_mutipled, message_matrix, matrix_key, encryption_matrix, encrypted_message_string

    def decrypt(self, key: str, message_enc: str):
        matrix_key = self.get_square_matrix_from_stringkey(key)
        self.check_key_is_invertable(matrix_key, self.modulo)
        matrix_key_inv = self.get_inv_matrix_mod(matrix_key)
        message_matrix, message_fixed = self.get_fixed_message_and_get_matrix(message_enc, matrix_key)
        decryption_multiplier = np.matmul(matrix_key_inv, message_matrix)
        decrypted_matrix = np.remainder(decryption_multiplier, self.modulo)
        decrypted_message_string = self.matrix_to_string(decrypted_matrix)
        return decrypted_matrix, decryption_multiplier, matrix_key, matrix_key_inv, message_matrix, decrypted_message_string

    def brute_force(self, message, path_):
        if path.exists(Path(f'{path_}/{message}.txt')):
            return
        permutation_keys = list(product(self.alphabet, repeat=4))
        with open(Path(f'{path_}/{message}.txt'), 'w+', encoding='UTF-8') as file:
            i = 0
            for keys in permutation_keys:
                key = ''.join(keys)
                try:
                    *_, text = self.decrypt(key, message)
                    i += 1
                    file.write(f"{i} - {text}     klucz - {key} \n")
                except:
                    pass
            file.write("""\n\n\nZAKOŃCZONO ŁAMANIE""")


    def decypt_with_4_letters(self, message, four_letters):
        four_letters_matrix = self.get_square_matrix_from_stringkey(four_letters).transpose()
        try:
            self.check_key_is_invertable(four_letters_matrix, self.modulo)
            message_matrix, message_fixed = self.get_fixed_message_and_get_matrix(message, four_letters_matrix)
            small_matrix_enc = [[message_matrix[0][0], message_matrix[1][0]],
                                [message_matrix[0][1], message_matrix[1][1]]]
            matrix_good_key = self.solve_equation(small_matrix_enc, four_letters_matrix)
            decrypted_matrix = np.matmul(matrix_good_key, message_matrix)
            decrypted_matrix = np.remainder(decrypted_matrix, (len(self.alphabet)))
            dectypted_string = self.matrix_to_string(decrypted_matrix)
            return [dectypted_string]


        except NwdNot1:
            self.check_key_is_invertable(four_letters_matrix, 13)
            message_matrix, message_fixed = self.get_fixed_message_and_get_matrix(message, four_letters_matrix)
            small_matrix_enc = [[message_matrix[0][0], message_matrix[1][0]],
                                [message_matrix[0][1], message_matrix[1][1]]]
            list_of_solutions = []
            for key in list(product(self.alphabet[:2], repeat=4)):
                matrix_01_matrixes = self.get_square_matrix_from_stringkey(key)
                matrix_bad_key = self.solve_equation(small_matrix_enc, four_letters_matrix, 2)
                matrix_good_key = np.add(matrix_bad_key, 13 * matrix_01_matrixes)
                decrypted_matrix = np.matmul(matrix_good_key, message_matrix)
                decrypted_matrix = np.remainder(decrypted_matrix, self.modulo)
                word = self.matrix_to_string(decrypted_matrix)
                list_of_solutions.append(word)
            return list_of_solutions


def brute_force_thread(message, alphabet=None, path_='static/bruteforce'):
    files = os.listdir(path_)
    if len(files) > 50:
        os.remove(Path(path_ + '/' + files[-1]))

    HillCipher(alphabet=alphabet).brute_force(message, path_=path_)


