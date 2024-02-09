import re
with open('1vs1200.txt', 'r', encoding='KOI8-R') as file:
    file_content = file.read()
question_answer_pairs = re.findall(
    r'Вопрос (\d+):\n(.*)\n\nОтвет:\n(.*)\.',
    file_content,
    re.DOTALL
)
standardized_dict = {
    f"Вопрос {q_num}:\n{question}":
    f"Ответ: {answer}" for q_num, question, answer in question_answer_pairs
}

for k, v in standardized_dict.items():
    print(f'QUESTION\n{k}\nANSWER\n{v}')

