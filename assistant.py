import ollama
import chromadb
import ast
from tqdm import tqdm
from colorama import Fore, Back, Style


import utils
convo = utils.Conversation


main_model = 'ATLAS:v0.2'
agent_model = 'llama3.2'
embedding_model = 'nomic-embed-text'

client = chromadb.Client() # Start the vector Database on my PC


###------------------------------------------------------------- AGENTS --------------------------------------------------------------------------------###
def recall_Agent(prompt):
    # defining the agent class with user prompts
    agent = utils.RAG(userPrompt=prompt, Classes=None).Recall
    agent_convo = agent.sys()

    # LLM Response
    response = ollama.chat(model=agent_model, messages=agent_convo)
    return (response['message']['content'].strip().lower())

def classification_Agent(prompt):
    # Getting all class names and descriptions
    Meta_Classes = utils.Meta_Classes()
    Classes = Meta_Classes.get_descriptions()

    # defining the agent class with user prompt and class descriptions
    agent = utils.RAG(userPrompt=prompt, Classes=Classes).Classification
    agent_convo = agent.sys()

    # LLM Response
    response = ollama.chat(model=agent_model, messages=agent_convo)
    return (response['message']['content'])

def query_Agent(prompt):
    #list for search queries
    list = []

    # defining the agent class with user prompts
    agent = utils.RAG(userPrompt=prompt, Classes=None).Query
    agent_convo = agent.sys()

    # LLM Response
    response = ollama.chat(model=agent_model, messages=agent_convo)

    # Validating if the response was a python list or if it is empty
    try:
        if not ast.literal_eval(response['message']['content']): # if array is empty
            raise ValueError(" *NO QUERY ITEMS:")
        else:
            print(" Query amount: ", len(ast.literal_eval(response['message']['content'])))
            return ast.literal_eval(response['message']['content'])
        
    except ValueError as e:
        print(e,' Passing Original Prompt*')
        list.append(prompt) # Putting the prompt in an array to be passed as a search query
        return list

def embeddings_Agent(queries, results_per_query=2):
    embeddings = set()

    for query in tqdm(queries, desc="Processing queries to vector database"):
        response = ollama.embeddings(model=embedding_model, prompt=query)# Uses the prompt to generate a embedding response to search the vector database for relevant information
        query_embeddings = response['embedding']# Saves the Generated embedding key



###------------------------------------------------------------- Main Functions ------------------------------------------------------------------------###
def Memories(prompt):
    #Save the Response from the Recall Agent
    recall = recall_Agent(prompt)
    
    match recall:
        case 'yes':
            print(Fore.YELLOW + f"SYSTEM:\n Accessing Memories...")

            # Makes a class for the user prompt to be used a metadata for organization
            Meta_Class = classification_Agent(prompt)
            print(Fore.YELLOW + f" Class: {Meta_Class}")

            # Making a python list of search queries from the user prompt
            Queries = query_Agent(prompt)
            print(f" Search queries: {Queries}")

            # retrieve the most accurate information and return it from that vector database for context 
            Embeddings = embeddings_Agent(Queries)
            print(f" Embeddings results: {Embeddings}")


            pass

        case 'no':
            print(Fore.YELLOW + f"SYSTEM:\n *No memories are needed*")
            pass
        
        case _:
            print(Fore.RED + f"SYSTEM:\n *Recalling Agent Failure*")
            pass

    #resets output color back to normal
    print(Style.RESET_ALL)


def Atlas_Response(prompt):
    pass


###-----------------------------------------------------------------------------------------------------------------------------------------------------###
while True:
    prompt = input(Fore.WHITE + 'USER: \n') # Take user input
    print(Style.RESET_ALL)
    Memories(prompt=prompt)
    Atlas_Response(prompt=prompt)

    
