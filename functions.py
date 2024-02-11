import random

with open('1vs1200.txt', 'r', encoding='KOI8-R') as file:
    lines = file.readlines()

question_answer_pairs = {}
question = ''
answer = ''
for index, line in enumerate(lines):
    if line.startswith('Вопрос'):
        for current_line in lines[index + 1:]:
            if not current_line.startswith('Ответ'):
                question += current_line
            else:
                break
    if line.startswith('Ответ'):
        for current_line in lines[index + 1:]:
            if not current_line == '\n':
                answer += current_line
            else:
                break
    if question and answer:
        question_answer_pairs[question] = answer
        question = ''
        answer = ''


def send_question():
    random_question = random.choice(list(question_answer_pairs.keys()))
    return random_question
