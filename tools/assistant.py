import ollama
import chromadb
import psycopg
import ast
from tqdm import tqdm
from psycopg.rows import dict_row

# VIDEO : 22:10 function

main_model = 'ATLAS:v0.2'
sub_model = 'llama3.2'
embedding_model = 'nomic-embed-text'

client = chromadb.Client() # Start the vector Database on my PC

#system prompt for RAG (vector/postgres databases)
system_prompt = (
    'You are an AI assistant that has memory of every conversation you have ever had with this user.'
    'On every prompt from the user, the system has checked for any relevant messages you have had with the user.'
    'If any embedded previous conversations are attached, use them for context for responding to the user,'
    'if the context is relevant and useful to responding. If the recalled conversations is irrelevant,'
    'disregard speaking about them and respond normally as an AI assistant. Do not talk about recalling conversations. '
    'Just use any useful data from the pervious conversations and respond normally as an intelligent AI assistant.'
)
convo = [] # Array for the user and assistant current conversation

DB_PARAMS = { # PostgresSQL parameters for connecting to database
    'dbname': 'memory_agent',
    'user': 'atlas',
    'password': 'April1203',
    'host': 'localhost',
    'port': '5432'
}

# Connecting to the postgres database
def connect_db():
    conn = psycopg.connect(**DB_PARAMS)
    return conn

# Get all the queries from the database 
def fetch_conversations():
    conn = connect_db() # Connects to database
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute('SELECT * FROM conversations') # sql querying all the available data in the database 
        conversations = cursor.fetchall() # Saving all
    conn.close() # close the connection to the database
    return conversations

# Storing the conversation into a query
def store_conversations(prompt, response):
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(
            'INSERT INTO conversations (timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, %s, %s)',
            (prompt, response)
        )
        conn.commit()
    conn.close()

# Generating the llm responses in full
def full_response(prompt):

    convo.append({'role': 'user', 'content': prompt}) # Upload the user input to the conversation array in a json format the lLM can understand

    output = ollama.chat(model=main_model, messages=convo)
    response = output['message']['content']

    print(f'ATLAS: \n{response} \n')
    store_conversations(prompt=prompt, response=response) # Upload convo to postgres database
    convo.append({'role': 'assistant', 'content': response}) # Upload the AI input to the conversation array in a json format the lLM can understand

# Generating the llm responses in chunks
def stream_response(prompt):
    convo.append({'role': 'user', 'content': prompt}) # Upload the user input to the conversation array in a json format the lLM can understand
    response = ''

    stream = ollama.chat(model=main_model, messages=convo, stream=True)
    print('\nATLAS:')

    for chunk in stream:
        content = chunk['message']['content']
        response += content
        print(content, end='', flush=True)
    
    print("\n")
    store_conversations(prompt=prompt, response=response) # Upload convo to postgres database
    convo.append({'role': 'assistant', 'content': response}) # Upload the AI input to the conversation array in a json format the lLM can understand

# Creating and Saving conversations into the LLM'S Vector database 
def create_vector_db(conversations):
    vector_db_name = 'conversations'

    # Deleting the 'conversations' Database if it already exists, so copies of the message history isn't added every time the program is ran.
    try: 
        client.delete_collection(name=vector_db_name)
    except ValueError: # if it didn't exists
        pass

    vector_db = client.create_collection(name=vector_db_name)

    # looping though each conversation
    for c in conversations:
        serialized_convo = f'prompt: {c["prompt"]} response: {c["response"]}' # separating each convo into a separate prompt 
        response = ollama.embeddings(model=embedding_model, prompt=serialized_convo) # running an embedding model, meaning it can only be used to generate embeddings
        embedding = response['embedding'] # Saving the generated embedding key

        #Adding the conversation in a the vector db with the id, embedding number ,and the conversation prompt
        vector_db.add(
            ids=[str(c['id'])],
            embeddings=[embedding],
            documents=[serialized_convo]
        )

# Using prompt given, looks in the vector database to retrieve the most accurate information and return it for context
def retrieve_embeddings_prompt(prompt):
    response = ollama.embeddings(model=embedding_model, prompt=prompt) # Uses the prompt to generate a embedding response to search the vector database for relevant information
    prompt_embedding = response['embedding'] # Saves the Generated embedding key 

    vector_db = client.get_collection(name='conversations') # load the vector database 
    results = vector_db.query(query_embeddings=[prompt_embedding], n_results=1) # Using the embedding key to look in the database for related prompts and puts it in a query
    best_embedding = results['documents'][0][0] # store the best embedding from the query

    return best_embedding

# Using queries given, looks in the vector database to retrieve the most accurate information and return it for context
def retrieve_embeddings(queries, results_per_query=2):
    embeddings = set()

    for query in tqdm(queries, desc="Processing queries to vector database"):
        response = ollama.embeddings(model=embedding_model, prompt=query)# Uses the prompt to generate a embedding response to search the vector database for relevant information
        query_embeddings = response['embedding']# Saves the Generated embedding key 


        vector_db = client.get_collection(name='conversations') # load the vector database
        results = vector_db.query(query_embeddings=[query_embeddings], n_results=results_per_query) # Using the embedding key to look in the database for related prompts and puts it in a query
        best_embedding = results['documents'][0] # store the best embedding from the query
        
        for best in best_embedding:
            if best not in embeddings:
                if 'yes' in classify_embedding(query=query, context=best):
                    embeddings.add(best)

    return embeddings

# Generate a list a queries to send to the vector embedding database
def create_queries(prompt):
    # System prompt for the LLM to behave as a Ai Agent that turns the user prompt into queries related to the prompt
    query_msg = (
        'You are a first principle reasoning search query AI agent.'
        'Your list of search queries will be ran on an embedding database of all your conversations '
        'you have ever had with the user. With first principles create a Python list of queries to '
        'search the embeddings database for any data that would be necessary to have access to in '
        'order to correctly respond to the prompt. Your response must be a Python list with no syntax errors. '
        'Do not explain anything and do not ever generate anything but a perfect syntax Python list'
    )
    # Example conversations for Multi Shot learning (a technics used for training a model with examples to respond in certain way)
    query_convo = [
        {'role': 'system', 'content': query_msg},
        {"role": "user", "content": "How do I debug a segmentation fault in C?"},
        {"role": "assistant", "content": "['segmentation fault debugging', 'debugging segmentation faults in C', 'common causes of segmentation faults', 'tools for debugging C programs', 'steps to resolve segmentation faults']"},
        {"role": "user", "content": "What are the benefits of using Docker in development?"},
        {"role": "assistant", "content": "['benefits of Docker', 'Docker advantages in development', 'why use Docker', 'Docker for developers', 'Docker use cases']"},
        {"role": "user", "content": "Explain how blockchain ensures data security."},
        {"role": "assistant", "content": "['blockchain data security', 'how blockchain works', 'blockchain cryptography', 'data integrity in blockchain', 'blockchain consensus mechanisms']"},
        {"role": "user", "content": "What are the key principles of effective time management?"},
        {"role": "assistant", "content": "['effective time management principles', 'time management techniques', 'improving productivity', 'time organization strategies', 'prioritizing tasks effectively']"},
        {"role": "user", "content": "Why is photosynthesis important for life on Earth?"},
        {"role": "assistant", "content": "['importance of photosynthesis', 'role of photosynthesis in ecosystems', 'photosynthesis and oxygen production', 'energy cycle in nature', 'how photosynthesis supports life']"},
        {"role": "user", "content": "What are some ways to reduce stress in daily life?"},
        {"role": "assistant", "content": "['stress reduction methods', 'daily stress management techniques', 'mental health improvement tips', 'relaxation strategies', 'ways to handle stress effectively']"},
        {"role": "user", "content": "How does gravity affect the motion of celestial bodies?"},
        {"role": "assistant", "content": "['gravity and celestial motion', 'Newton's law of gravitation', 'how gravity influences planets', 'gravitational interactions in space', 'orbits and gravity']"},
        {'role': 'user', 'content': prompt}
    ]

    response = ollama.chat(model=sub_model, messages=query_convo) # running the model for query generation
    print(f"\nVector database queries: {response['message']['content']} \n") # Print query response

    try: 
        return ast.literal_eval(response['message']['content']) # Convert response from a "string" into a "python list"
    except:
        print('DID NOT MAKE THE PYTHON QUERIES!!!')
        return [prompt]

def classify_embedding(query, context):
    classify_msg = (
        'You are an embedding classification AI agent. Your input will be a prompt and one embedded chunk of text. '
        'You will not respond as Ai assistant. You only respond "yes or "no". '
        'Determine whether the context contains data that directly is related to the search query. '
        'If the context is seemingly exactly what the search query needs, respond "yes" if it is anything but directly '
        'related respond "no". Do not respond "yes" unless the content is highly relevant to the search query.'
    )
    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {"role": "user", "content": f"SEARCH QUERY: What is the user's name? \n\nEMBEDDED CONTEXT: You are Kavin Lajara. How can I help you today, sir?"},
        {"role": "assistant", "content": "yes"},
        {"role": "user", "content": f"SEARCH QUERY: Llama3 Python voice assistant \n\nEMBEDDED CONTEXT: Siri is a voice assistant on Apple iOS and macOS."},
        {"role": "assistant", "content": "no"},
        {"role": "user", "content": f"SEARCH QUERY: What are the benefits of using Docker? \n\nEMBEDDED CONTEXT: Docker enables consistent development environments by using containers, which isolate applications and dependencies."},
        {"role": "assistant", "content": "yes"},
        {"role": "user", "content": f"SEARCH QUERY: Explain blockchain consensus mechanisms \n\nEMBEDDED CONTEXT: Consensus mechanisms ensure all nodes in a blockchain network agree on the current state of the ledger."},
        {"role": "assistant", "content": "yes"},
        {"role": "user", "content": f"SEARCH QUERY: History of the internet \n\nEMBEDDED CONTEXT: The embedded text discusses the invention of the printing press and its impact on information dissemination."},
        {"role": "assistant", "content": "no"},
        {'role': 'user', 'content': f"SEARCH QUERY: {query} \n\nEMBEDDED CONTEXT: {context}"}
    ]

    response = ollama.chat(model=sub_model, messages=classify_convo)

    return response['message']['content'].strip().lower()

def recall(prompt):
    queries = create_queries(prompt=prompt)
    embeddings = retrieve_embeddings(queries=queries)
    convo.append({'role': 'user', 'content': f'MEMORIES: {embeddings} \n\n USER PROMPT: {prompt}'})
    print(f'\n{len(embeddings)} message:response embeddings added for context.')

 
conversations = fetch_conversations() # Fetching sql data content
create_vector_db(conversations=conversations) # Uploading content to the vector database

while True:
    prompt = input('USER: \n') # Take user input
    recall(prompt=prompt)
    stream_response(prompt=prompt)
    