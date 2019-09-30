import itunes
import random
import re
import string
## Creating SQL from natural language
# Import necessary modules
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config

# Create a trainer that uses this config
trainer = Trainer(config.load("config_spacy.yml"))

# Load the training data
training_data = load_data('data-itunes-9.json')

# Create an interpreter by training the model
interpreter = trainer.train(training_data)

# Define the global variables:
global pending_item
pending_entities = []
global_name = None
global global_price
# Define the states

INIT = 0
GREET = 1
INTRODUCTION = 2
MOVIE_CHOOSE = 3
MUSIC_CHOOSE = 4
APP_CHOOSE = 5
GOODBYE = 6
ORDERED = 7
MOVIE_ORDERED = 8
MUSIC_ORDERED = 9
APP_ORDERED = 10
ASKED_PRICE = 11
AFFIRM_PRAISE = 12
RECOMMEND_RANDOM = 13


responses = {"greet":["Hi!,I'm Patrick","Good morning!"], "introduction":["Hi, {}","Very nice to know you, {}!"],
             "goodbye":["Bye,{}","See you {}"],"music":"This song - {} is very great, you can click: {}",
             "movie":"This may work for you: {}",
             "app":"Do you like this app:{}?",
             "music":"This album may meet your requirement:{}",
             "affirm_praise":"It's my pleasure,boss!",
             "cost":"This stuff needs you {} dollars"}

Deny_Answer=["All,right! Now, ","Ok, how about this one: ","Sure, please click this one: "]

policy_rules = {
    (INIT, "greet"): (GREET, random.choice(responses["greet"])+" Can I have your name? "),
    (INIT,"movie"):(MOVIE_CHOOSE,responses["movie"]),
    (INIT,"app"):(APP_CHOOSE,responses["app"]),
    (INIT,"music"):(MUSIC_CHOOSE,responses["music"]),

    (GREET,"introduction"):(INTRODUCTION, responses["introduction"]),


    (INTRODUCTION,"movie"):(MOVIE_CHOOSE,responses["movie"]),
    (INTRODUCTION,"music"):(MUSIC_CHOOSE,responses["music"]),
    (INTRODUCTION,"app"):(APP_CHOOSE,responses["app"]),

    (MOVIE_CHOOSE,"movie"):(MOVIE_CHOOSE,responses["movie"]),
    (MUSIC_CHOOSE,"music"):(MUSIC_CHOOSE,responses["music"]),
    (APP_CHOOSE,"app"):(APP_CHOOSE,responses["app"]),

    (MOVIE_CHOOSE,"deny"):(MOVIE_CHOOSE,random.choice(Deny_Answer)+responses["movie"]),
    (MUSIC_CHOOSE,"deny"):(MUSIC_CHOOSE,random.choice(Deny_Answer)+responses["music"]),
    (APP_CHOOSE,"deny"):(APP_CHOOSE,random.choice(Deny_Answer)+responses["app"]),

    (MOVIE_CHOOSE,"ask_price"):(ASKED_PRICE,responses["cost"]),
    (MUSIC_CHOOSE,"ask_price"):(ASKED_PRICE,responses["cost"]),
    (APP_CHOOSE,"ask_price"):(ASKED_PRICE,responses["cost"]),

    (ASKED_PRICE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),
    (ASKED_PRICE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),
    (ASKED_PRICE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),


    (AFFIRM_PRAISE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),
    (AFFIRM_PRAISE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),
    (AFFIRM_PRAISE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),


    (MOVIE_CHOOSE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),
    (MUSIC_CHOOSE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),
    (APP_CHOOSE,"affirm" or "praise"):(AFFIRM_PRAISE,responses['affirm_praise']),

    (AFFIRM_PRAISE,"goodbye"):(GOODBYE,responses["goodbye"])


    #(INTRODUCTION,"goodbye"):(GOODBYE,responses["goodbye"])
}
## Utilize regex to find users' names
def find_name(message):
    name = None
    # Create a pattern for checking if the keywords occur
    name_keyword = re.compile("name|call")
    # Create a pattern for finding capitalized words
    name_pattern = re.compile("[A-Z]{1}[a-z]*")
    if name_keyword.search(message):
    #if re.match(name_keyword,message):
        # Get the matching words in the string
        name_words = name_pattern.findall(message)
        #print(name_words)
        if len(name_words) > 0:
            # Return the name if the keywords are present
            name = ' '.join(name_words)
    return name

def find_item(params):
    '''

    :param params: a dictionary
    :return: a tuple (name_of_stuff, links_of_stuff)
    '''
    # initiate a string for query
    global global_price
    query = ""
    result = []
    par = []  # designed to store the parameters
    for k, v in params.items():
        if v not in ["movie", "music"]:
            # just need query parameters
            par.append(v)
        else: par = [v]
    # create query
    query = " ".join(par)
    #print("query:{}".format(query))

    # Match the stuff that the user want
    if "movie" in list(params.keys()):

        result = itunes.search_movie(query=query)

    elif "app" in list(params.keys()):

        result = itunes.search_app(query=query)

    elif "music" in list(params.keys()):

        result = itunes.search_album(query=query)

    if result:

        display_result = random.choices(result)[0]
        # Because the results are too many, then we just return the random one

        # refresh the price of the newest inquire result:
        global_price = display_result.price
       # print("get_item_price:{}".format(display_result.price))

        return display_result.name, display_result.url


    else:
        return None



## Asking contextual questions
def send_message(state, message):
    print("USER : {}".format(message))
    new_state, response = respond(state, message)

    # print("new_state:{},response:{}".format(new_state,response))

    print("BOT : {}".format(response))
    return new_state,response


# Define respond()
def get_item(pending_entities):
    '''
    :param message: a list of entities (dictionary)
    :return: a tuple of (name_of_app, links)
    '''
    # print("pending_entities:",pending_entities)

    params = {}
    for ent in pending_entities:
        # print("ent:{}".format(ent))
        params[ent["entity"]] = str(ent["value"])

    # Find hotels that match the dictionary
    # print("params: {}".format(params))
    results = find_item(params)
    # Get the names of the hotels and index of the response

    print("result: ",results)
    if results:
        name = results[0]
        link = results[1]
        # price = results[2]

        # Select the nth element of the responses array
        return name, link
    else:
        return None


def respond(state, message):
    # initiate variables
    global global_name, global_name
    global global_price, global_price
    global pending_item
    condition = ""
    name = ""
    item_name, item_link = "", ""
    asked = False
    price = 0
    # pending_entities = []  # designed to keep all entites that we want to parse
    data = interpreter.parse(message)
    print("data:{}".format(data))
    for item in data["entities"]:
        print("item:", item)
        #if item['entity'] == []:
            #continue
        if item['entity'] == "name":
            # print("item:", item)
            name = find_name(message)
            global_name = name

        elif item['entity'] == "ask_price":
            price = global_price


        elif item["entity"] == "deny":
            changed_item_name, changed_item_link = get_item(pending_entities)
            item_link = changed_item_link

        elif item["entity"] == "affirm":
            condition = "affirm"

        else:
            # print("item:", item)
            # save to the global value, if the last result is unsatisfying, we can change
            pending_item = item
            pending_entities.append(item)
            print("what happend:",pending_entities)
            stuff = get_item(pending_entities)
            if stuff:
                item_name, item_link = stuff

    # print("state:{},interpret(message):{}".format(state,interpret(message)))

    if (state,interpret(message)) in list(policy_rules.keys()):
        (new_state, response) = policy_rules[(state, interpret(message))]
    else:
        return state, "sorry, I couldn't understand what are you talking about?"

    # print("interpreted message:{}".format(interpret(message)))

    if type(response) == list:
        response = random.choice(response)

    if data["intent"]["name"] == "goodbye":
        response = response.format(global_name)

    if data["intent"]["name"] == "ask_price":
        response = response.format(price)
        asked = True

    if name and "{}" in response:
        response = response.format(name)


    if condition == "affirm":
        return new_state, response



    else:
        if "{}" in response:
            response = response.format(item_link)

    return new_state, response


def interpret(message):
    # interpret the state:
    '''
    :param message: str, messages
    :return: str
    '''
    entities = interpreter.parse(message)
    # print(entities)
    # print(entities['intent']['name'])
    if entities['intent']['name'] == "introduction":
        return "introduction"

    elif entities["intent"]['name'] == "inquire":
        return "inquire"

    elif entities['intent']['name'] == "music_search":
        return 'music'

    elif entities['intent']['name'] == "app_search":
        return 'app'

    elif entities['intent']['name'] == "movie_search":
        return 'movie'

    elif entities['intent']['name'] == "greet":
        return 'greet'

    elif entities['intent']['name'] == "goodbye":
        return 'goodbye'

    elif entities['intent']['name'] == "deny":
        return 'deny'

    elif entities['intent']['name'] == "affirm" or entities['intent']['name'] == "praise":
        return 'affirm'

    elif entities['intent']['name'] == "ask_price":
        return 'ask_price'


    #if "n't" or "not" or "no" in message:
        #return "deny"

    return 'none'

# Define send_messages()
def send_messages(messages):
    state = INIT
    for msg in messages:
        state,response = send_message(state, msg)
        # print("current state:{}".format(state))
