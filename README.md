# Quiz bot


A bot that asks you quiz questions in tg and vk.


An example of tg bot - https://t.me/devman_lesson_quiz_bot.

An example of vk bot - https://vk.com/club224667007.

## Environment


### Requirements

Python 3.10 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```bash
pip install -r requirements.txt
```

### Environment variables

- TG_TOKEN
- VK_TOKEN
- MASTER_ID

1. Put `.env` file near `main.py`.
2. `.env` contains text data without quotes.

For example, if you print `.env` content, you will see:

```bash
$ cat .env
TG_TOKEN=684537...
VK_TOKEN=vk1.a.sF...
MASTER_ID=42...
```

#### How to get

- Create a tg chatbot to get its token with [BotFather](https://telegram.me/BotFather). 

- Create a VK group and get its token [here](https://vk.com/club224221946?act=tokens).

- Get your chat id [here](https://t.me/userinfobot).


### Run

Launch on Linux(Python 3) or Windows:
```bash
python tg_quiz_bot.py 'txt_file'
```
```bash
python vk_quiz_bot.py 'txt_file'
```
*txt_file content's structure must look like [1vs1200.txt](https://github.com/duke-doki/quiz-bot/blob/main/1vs1200.txt).
## Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
