import ollama
import ast
from tqdm import tqdm
from colorama import Fore, Back, Style


import utils
convo = utils.Conversation


main_model = 'ATLAS-v2'
agent_model = 'llama3.2'
embedding_model = 'nomic-embed-text'

memory_init = utils.MemoryDatabase()
memoryDB = memory_init.vectorDB


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
            print(response['message']['content'])
            raise ValueError(" *NO QUERY ITEMS:")
        else:
            print(" Query amount: ", len(ast.literal_eval(response['message']['content'])))
            return ast.literal_eval(response['message']['content'])
        
    except ValueError as e:
        print(e,' Passing Original Prompt*')
        list.append(prompt) # Putting the prompt in an array to be passed as a search query
        return list

def embeddings_Agent(queries, className, results_per_query=2):
    embeddings = set()

    for query in tqdm(queries, desc=" Processing queries to vector database \n"):
        response = ollama.embeddings(model=embedding_model, prompt=query)# Uses the prompt to generate a embedding response to search the vector database for relevant information
        query_embeddings = response['embedding']# Saves the Generated embedding key

        # load the vector database
        vector_db = memoryDB.get_collection(name=memory_init.collection_name)
        # Using the embedding key to look in the database for related prompts and puts it in a query
        results = vector_db.query(
            query_embeddings=[query_embeddings], 
            n_results=results_per_query,
            where={'Class': className} 
        )
        # store the best embedding from the query
        best_embedding = results['documents'][0] 

        for best in best_embedding:
            if best not in embeddings:
                if 'yes' in retrieve_Confirmation_Agent(query=query, context=best):
                    embeddings.add(best)
                    #print(f" Best Embedding: {best}")

    return embeddings

def retrieve_Confirmation_Agent(query, context):
        # defining the agent class with user prompts
        agent = utils.RAG(query=query, context=context).Confirmation
        agent_convo = agent.sys()

        response = ollama.chat(model=agent_model, messages=agent_convo)
        #print("Confirmation Response: ", response['message']['content'].strip().lower())
        return response['message']['content'].strip().lower()


###------------------------------------------------------------- Main Functions ------------------------------------------------------------------------###
def Rag_Sys(prompt):
    #Save the Response from the Recall Agent
    recall = recall_Agent(prompt)
    
    match recall:
        case 'yes':
            print(Fore.YELLOW + f"SYSTEM:\n Accessing Memories...")

            # Makes a class for the user prompt to be used a metadata for organization
            Meta_Class = classification_Agent(prompt)
            print(f" Class: {Meta_Class}")

            # Making a python list of search queries from the user prompt
            Queries = query_Agent(prompt)
            print(f" Search queries: {Queries}")

            # retrieve the most accurate information and return it from that vector database for context 
            Embeddings = embeddings_Agent(queries=Queries, className=Meta_Class)
            #print(f'\n{len(Embeddings)} message:response embeddings added for context.')

            # Adding the user prompt to the conversation array + Embedding Memories
            if len(Embeddings):
                print(" Memories were Added...")
                return ({'role': 'user', 'content': f'MEMORIES: {Embeddings} \n\n USER PROMPT: {prompt}'})
            else:
                print(" No relevant memories were found...")
                return ({'role': 'user', 'content': f'{prompt}'})


        case 'no':
            print(Fore.YELLOW + f"SYSTEM:\n *No memories are needed*")
            return ({'role': 'user', 'content': f'{prompt}'})
        
        case _:
            print(Fore.RED + f"SYSTEM:\n *Recalling Agent Failure*")
            return ({'role': 'user', 'content': f'{prompt}'})

    #resets output color back to normal
    print(Style.RESET_ALL)

def Atlas_Response(prompt, stream=True):
    print(Fore.LIGHTBLUE_EX)
    # Upload the user input to the conversation array in a json format the lLM can understand
    convo.append(prompt)
    response = ''

    if stream:
        stream = ollama.chat(model=main_model, messages=convo, stream=True)
        print('\nATLAS:')

        for chunk in stream:
            content = chunk['message']['content']
            response += content
            print(content, end='', flush=True)
        
        print("\n")
    else:
        output = ollama.chat(model=main_model, messages=convo)
        response = output['message']['content']

        print(f'ATLAS: \n{response} \n')
    

    # Upload the AI input to the conversation array in a json format the lLM can understand
    convo.append({'role': 'assistant', 'content': response})

    #resets output color back to normal
    print(Style.RESET_ALL)

###-----------------------------------------------------------------------------------------------------------------------------------------------------###
# Usage Example 
if __name__ == "__main__":
    while True:
        prompt = input(Fore.WHITE + 'USER: \n') # Take user input
        print(Style.RESET_ALL)
        memoryPrompt = Rag_Sys(prompt=prompt)
        Atlas_Response(prompt=memoryPrompt)

    
