import random
import os


def get_quiz_pairs(txt_file):
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, txt_file)
    with open(file_path, 'r', encoding='KOI8-R') as file:
        lines = file.readlines()
    question_answer_pairs = {}
    question = ''
    answer = ''
    for index, line in enumerate(lines):
        if line.startswith('Вопрос') or line.startswith('Ответ'):
            for current_line in lines[index + 1:]:
                if (
                        not current_line.startswith('Ответ')
                        and line.startswith('Вопрос')
                ):
                    question += current_line
                elif (
                        not current_line == '\n'
                        and line.startswith('Ответ')
                ):
                    answer += current_line
                else:
                    break
        if question and answer:
            question_answer_pairs[question] = answer
            question = ''
            answer = ''
    return question_answer_pairs


def get_question(question_answer_pairs):
    random_question = random.choice(list(question_answer_pairs.keys()))
    return random_question
