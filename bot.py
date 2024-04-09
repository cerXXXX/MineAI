from javascript import require, On
import time, os
from openai import OpenAI
from deep_translator import GoogleTranslator as Translator


version = '1.20.4' # minecraft version
hostname = '12345.aternos.me' # server address
port = '12345' # server port
botname = 'Bot' # bot's nickname
auth = 'offline' # for offline mode servers ('microsoft' if license, not recomended)

sourse_l = 'ru' # questions and answers language ('ru', 'de'...), 'auto' if you want to automatically detect the language
                  # but all the answers will be in English
target_l = 'en' # AI language

ai_model = 'TheBloke/Mistral-7B-Instruct-v0.2-GGUF/mistral-7b-instruct-v0.2.Q4_K_M.gguf' # AI name in LM Studio

addresing_the_bot = False # if True, your message must contain @bot_nickname (replace with the bot's nickname)

client = OpenAI(base_url='http://localhost:1234/v1', api_key='lm-studio')

history = [
    {'role': 'system', 'content': 'You are a minecraft player, helping other players. \
     You always provide well-reasoned answers that are both correct and helpful.'},
]

def send_to_ai(text):
    history.append({'role': 'user', 'content': Translator(sourse=sourse_l, target=target_l).translate(text) + \
                    ' Your answer must be less than 256 characters and not include information about the length of your answer.'})

    completion = client.chat.completions.create(
        model=ai_model,
        messages=history,
        temperature=0.7,
    )

    new_message = {'role': 'assistant', 'content': completion.choices[0].message.content}
    history.append(new_message)

    print('A:'  + new_message['content'])
    print(f'Translated into {sourse_l}: ' + ''.join(Translator(source='en', target=sourse_l).translate(new_message['content'])))
    print()


    return ''.join(Translator(source='en', target=sourse_l).translate(new_message['content']))
    

def follow(thefile):
    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            continue
        yield line


mineflayer = require('mineflayer')
bot = mineflayer.createBot({
    'host': hostname,
    'port': port,
    'username': botname,
    'version': version,
    'auth':auth,
})

while True:
    logfile = open(os.getenv('APPDATA')+'/.minecraft/logs/latest.log', 'r')
    loglines = follow(logfile)
    text = ''
    for line in loglines:
        if '[CHAT]' in line and ('@' + botname in line if addresing_the_bot else botname not in line) and '>' in line:
            text = line.split('>')[1][1:-1]

            print(f'Q: {text}')
            print(f'Translated into {target_l}: {Translator(sourse=sourse_l, target=target_l).translate(text)}')
            print()

            break
    
    bot.chat(send_to_ai(text))
    