import openai 
import streamlit as st
import logging, sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Valerie spul
import awnserQuestion
import readCSVfile



# pip install streamlit-chat  
from streamlit_chat import message

openai.api_key = "sk-xxxxxxxxxxxxxxxxxxxxxx"

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    count = 0
    while count < 3:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature, # this is the degree of randomness of the model's output
            )
            count = 3
        except:
            count= count+1
            print('Rate limit occured, retrying\n')

    return response.choices[0].message["content"]

def get_completion_via_word_embeddings(prompt):
    df = readCSVfile.readCSV()
    response = awnserQuestion.answer_question(df, question=prompt)
    print(f"Response is {response} \n")
    return response

text = f"""
    Dat is onze missie; daar staan we voor. Door de ICT aan te passen aan bedrijfsprocessen en niet andersom" \
    , maken wij ICT binnen organisaties weer onzichtbaar, zodat onze klanten zich 100% kunnen focussen op hun bedrijfsdoelstellingen." \
    Wij onderscheiden ons door onze mensen. Professionals die stuk voor stuk een passie hebben voor ICT en betrokken zijn bij het succes \
    van onze klanten. Hierbij zijn transparantie, toegankelijkheid en wederzijds vertrouwen leading.Phact werkt agile en lean: \
    wij ontwikkelen onze software in teams en werken met korte en overzichtelijke perioden met veel evaluatiemomenten. \
    Bij ons geen ellenlange rapporten maar persoonlijk contact. In elk deelproces wordt iets gemaakt, opgeleverd en werkend gedemonstreerd. \
    Dit deel wordt geëvalueerd en indien nodig kan direct worden bijgestuurd. Door deze continue verbetering worden risico’s beperkt en \
    weten wij en de opdrachtgever dat we op de goede weg zitten.Dit alles maakt Phact dé one-stop-shop voor innovatieve totaaloplossingen. \
    Dit zijn enkele leuke weetjes over Phact: \
    1.	Er liggen 112 zonnepanelen op het dak bij Phact. \
    2.	De plant uit de Phackathon editie 2022 heet Henk. \
    3.	Er werden 30.7 kilo (plakken) kaas in de maand maart 2023 gegeten tijdens de (Phact) lunch. \
    4.	Er zitten 351 elementen (stipjes/blokjes) in het logo van Phact verwerkt. Volgens Richard zijn het er twee minder!\
    5.	Bijzondere lunchgewoontes: \
    Dit zijn enkele leuke weetjes over werknemers van Phact: \
    1.	Peter Hendrix eet tijdens de lunch boterhammen met ketchup, kaas en augurk. \
    2.	Jeroen Grijmans eet vaak een augurk in kaas gerold, zonder boterham. \
    3.	Johan Kleuskens beeindigd zijn lunch vaak met een lik pindakaas.\
    4.	Anne de Swart vindt ontbijtkoek met pindakaas en hagelslag lekker. Getver!\
    5.	Er zijn twee mensen die Natasja altijd nadrukkelijk, persoonlijk en iedere keer weer bedanken voor de lunch: Daniël Hettema en Johan Kleuskens. \
    6.	Jeroen Grijmans zijn guilty pleasure is ABBA. \
    7.	Jeroen Grijmans en Marc Herruer hebben in 2023 meer Phact-chocolade gegeten dan al het personeel bij elkaar dat heeft gedaan. \
    """

context = [ {'role':'system', 'content':f""" 
I want you to act as a Sales Development Representative (SDR) of the company Phact and reach out to a potential client who has been on our website for several minutes.
Your name is Deborah . A user is a potential customer. \
You should first get the name and email adres of the user before you answer any questions. After that, answer the questions of the user in a nice and polite way. \
By default start in Dutch. \
Your location is Venray and the timezone is the timezone of Amsterdam. \
If the user mentions \"jullie\", the company Phact is meant.\
The answer to a question can also be found in the content delimited by triple backticks.\
If help is needed or if there is an issue, ask to send the request to support@phact.nl \
 


Content: ```{text}``` \
"""} ] 

#Creating the chatbot interface
st.title("Incredible phactGPT chatbot")

# Storing the chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'context' not in st.session_state:
    st.session_state['context']=[]
if 'input' not in st.session_state:
    st.session_state.input = ''
if 'text_input' not in st.session_state:
    st.session_state.text_input = ''
if 'firstround' not in st.session_state:
    st.session_state.firstround=True



def clear_text():
    st.session_state.input = ''

def submit():
    if st.session_state.firstround == True:
        st.session_state['context'].append(context[0])

    if st.session_state.input != '' or st.session_state.firstround == True:
        st.session_state.text_input = st.session_state.input
        prompt = st.session_state.input
        context_user = {'role':'user', 'content':f"{prompt}"}
        st.session_state['context'].append(context_user)
        # First try to get a valid answer via word embeddings
        output=''
        if st.session_state.firstround == False and "weetjes" not in prompt and '+' not in prompt:
            output = get_completion_via_word_embeddings(prompt)
            # Remove incomplete sentences from string
            # pos = output.rfind('.')
            # if pos > -1:
            #     output = output[:pos+1]
        if "I do not know" in output or output == '' or "Ik weet het niet" in output or "weetje" in output:
            output = get_completion_from_messages(st.session_state['context'])
        context_assistant = {'role':'assistant', 'content':f"{output}"}
        st.session_state['context'].append(context_assistant)

        # store the output 
        st.session_state.past.append(prompt)
        st.session_state.generated.append(output)

        st.session_state.firstround = False

        clear_text()

def send_email(sender_email, sender_password, receiver_email, subject, message):
    # Set up the SMTP server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Create a secure connection to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    # Create the email message
    email_message = MIMEMultipart()
    email_message['From'] = sender_email
    email_message['To'] = receiver_email
    email_message['Subject'] = subject
    email_message.attach(MIMEText(message, 'plain'))

    # Send the email
    server.send_message(email_message)

    # Close the SMTP server connection
    server.quit()

  
st.text_input("You: ", key="input", on_change=submit())

if st.button("Close chat"):
    messages = st.session_state['context']
    messages.append({'role':'system', 'content': 'provide a transscript of the entire conversation.'})
    output = get_completion_from_messages(messages)
    # Provide the necessary details
    sender_email = 'sales@melderse.nl'
    sender_password = 'pietpiet'
    receiver_email = 'johan.kleuskens@phact.nl'
    subject = 'phactGPT chatbot email'

    # Send the email
    send_email(sender_email, sender_password, receiver_email, subject, output)
    print("\n--------Sent email to Sales----------\n")

    # Clear chat
    st.session_state['generated'] = []
    st.session_state['past'] = []
    
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        if st.session_state['past'][i] != '':
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

