import telebot as tb
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import base64
from PIL import Image
from io import BytesIO
import os

llm = ChatGoogleGenerativeAI(model='models/gemini-1.5-flash',api_key='AIzaSyBbVXzvCICAXBZfYOMV9wEUU_VKdROT4sQ',temperature=0.1)
prompt_mensagem = ChatPromptTemplate.from_messages(
    [
        ('system',
        """
        Você é um chef de cozinha que responde perguntas 
        diárias pelo telegram, sobre comida receitas e outros assuntos diarios,
        """
        ),
        ('human','{mensagem}')
    ]
)
prompt_foto = ChatPromptTemplate.from_messages(
    [
        ('system',
        """
        Você é um chef de cozinha que vai analizar um ambiente de cozinha
        e dizer os igredientes dentro dela e algumas refeiçoes
        e receitas que tem com fazer com os igredientes.
        """
        ),
        ('human','{mensagem}')
    ]
)
bot = tb.TeleBot("7505165870:AAGoRdoIKQi_l62wm69IzxwpAclp6BcPgJg")

@bot.message_handler(content_types=['photo'])
def mensagem_bot_imagem(mensagem):
    if os.path.exists("./imagens/imagem.png"):
        os.remove('./imagens/imagem.png')
    foto = mensagem.photo[-1]
    file_id = foto.file_id
    print(f'fileid: {file_id}')
    file = bot.get_file(file_id)
    download = bot.download_file(file.file_path)
    
    image = Image.open(BytesIO(download))
    image.save('./imagens/imagem.png','PNG')

    with open('./imagens/imagem.png','rb') as foto:
        imagem_data = base64.b64encode(foto.read()).decode("utf-8")

    chain = prompt_foto | llm
    resposta = chain.invoke({'mensagem':f'data:image/png;base64,{imagem_data}'})
    bot.reply_to(mensagem,resposta.content)
    if os.path.exists("./imagens/imagem.png"):
        os.remove('./imagens/imagem.png')


@bot.message_handler(func=lambda m:True)
def mensagem_bot(mensagem):
    chain = prompt_mensagem | llm
    resposta = chain.invoke({'mensagem':mensagem.text})
    bot.reply_to(mensagem,resposta.content)


bot.polling()