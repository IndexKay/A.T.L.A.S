import os
import psycopg2
import chromadb
import ollama
from systems import Meta_Classes
from chromadb.config import Settings
from psycopg2.extras import RealDictCursor

from dotenv import load_dotenv
load_dotenv()

class PostgresBackUpDatabase: 
    def __init__(self): 
        # Initialize the Postgres BackUp Database with database connection details and table name. 
        self.dbname =  os.getenv('PG_DBNAME')
        self.user = os.getenv('PG_USER')
        self.password = os.getenv('PG_PASSWORD')
        self.host = os.getenv('PG_Host')
        self.connection = None 

    def connect(self): 
        # Establish a connection to the PostgreSQL database. 
        try: 
            self.connection = psycopg2.connect( host=self.host, database=self.dbname, user=self.user, password=self.password ) 
        except psycopg2.Error as e: 
            print(f"Error connecting to the database: {e}") 
            raise 
 
    def fetch_data(self): 

        # Fetch all rows from the specified table. 
        if self.connection is None:
            raise Exception("Database connection is not established. Call connect() first.") 
        
        # Getting the list of metadata.
        meta_classes = Meta_Classes()
        class_names = meta_classes.get_class_names()

        Backup_Data = []
        
        try:
            for name in class_names:
                with self.connection.cursor(cursor_factory = RealDictCursor) as cursor: 
                    query = f"SELECT * FROM {name}" 
                    cursor.execute(query) 
                    data = cursor.fetchall() # Retrieve all rows 
                    columns = [desc[0] for desc in cursor.description] # Retrieve column names

                    #print ({"class": name, "columns": columns, "data": data})

                    # Save all table data into an array
                    Backup_Data.append({"className": name, "columns": columns, "data": data})
            return Backup_Data
  
        except psycopg2.Error as e: 
            print(f"Error fetching data: {e}") 
            raise

    def fetch_metadata(self, Table, columns_to_include):

        try:
            # Use RealDictCursor for column-to-value mapping
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)  

            # Execute a query to fetch all rows from the prompts table
            cursor.execute(f"SELECT * FROM {Table};")
            results = cursor.fetchall()

            # Filter the columns based on the array of column names
            filtered_results = [
                {key: row[key] for key in row if key in columns_to_include}
                for row in results
            ]
            
            return filtered_results

        except Exception as e:
            print("An error occurred:", e)

    def create_class_tables(self):
        # Getting the list of metadata class names.
        meta_classes = Meta_Classes()
        class_names = meta_classes.get_class_names()

        for name in class_names:
            # SQL statement to create the table
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {name} (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL
            );
            """
            try:
                with self.connection.cursor() as cursor:
                    # Execute the table creation query
                    cursor.execute(create_table_query)

                    # Commit the changes
                    self.connection.commit()
                print(f"Table {name} created successfully!")

            except Exception as e:
                print("An error occurred:", e)



        pass

    def close(self): 
        # Close the database connection. 
        if self.connection:
            self.connection.close() 


class MemoryDatabase:
    def __init__(self):
        # Name of the collection in our vector data
        self.collection_name = 'MEMORIES'
        # Defining the directory of out DB 
        self.vectorDB = chromadb.PersistentClient(path="./utils/DB")
        # Check if Database is already created 
        self.col_exists = True
        # initializing the postgres database
        self.backupDB = PostgresBackUpDatabase()
        # Embedding LLM Model
        self.embedding_model = 'nomic-embed-text'

    def VectorDB_Check(self):
        # Check if Database is already created 
        try:
            coll = self.vectorDB.get_collection(self.collection_name)

            # Check if the collection is empty
            if coll.get()["documents"]:
                print("*Collection is not empty*")
            else:
                raise ValueError("*Database Collection is empty*")

        except (chromadb.errors.InvalidCollectionException, ValueError) as e:
            if ValueError:
                print(e)
            elif chromadb.errors.InvalidCollectionException:
                print("*Database collection does not exist*")

            self.col_exists = False

    def Initialization(self):
        # Check if Database is already created
        self.VectorDB_Check()

        # Wether the database is created or not/empty
        match self.col_exists:
            case False:
                # Deleting the 'conversations' Database if it already exists since it is empty
                try:
                    self.vectorDB.delete_collection(name=self.collection_name)
                except ValueError: # if it didn't exists
                    pass

                # Create the Vector Database Collection
                vector_db = self.vectorDB.create_collection(name=self.collection_name)


                try:
                    # Connecting to the postgres database
                    self.backupDB.connect()
                    # Fetching all backup data
                    data = self.backupDB.fetch_data()

                    # For each data table:
                    for class_type in data:
                        # Defining the metadata using table columns and removing the "Prompt"&"Response" columns
                        meta_tags = class_type['columns']
                        meta_tags.remove('id')
                        meta_tags.remove('prompt')
                        meta_tags.remove('response')

                        # For each data query:
                        for query in class_type['data']:
                            # Separating each convo into a separate prompt 
                            serialized_convo = f'prompt: {query["prompt"]} response: {query["response"]}'
                            # Running an embedding model, meaning it can only be used to generate embeddings
                            response = ollama.embeddings(model=self.embedding_model, prompt=serialized_convo)
                            # Saving the generated embedding key for the query
                            embedding = response['embedding'] 

                            # Creates the array for the metadata
                            metadata = self.backupDB.fetch_metadata(Table=class_type['className'], columns_to_include=meta_tags)
                            metadata.append({"Class": class_type['className']})
                            print("MetaData:", metadata)

                            # Adding the query to the database
                            vector_db.add(
                                ids = [str(query['id'])],
                                embeddings = [embedding],
                                documents = [serialized_convo],
                                metadatas = metadata,
                            )

                            
                except ValueError as e:
                    print("ERROR in database initialization", e)

                finally:
                    self.backupDB.close()
                    print("Initialization was completed")

            case True:
                print("*The vector database is already created*")
                pass


# Usage Example 
if __name__ == "__main__":

    try:
        memory = MemoryDatabase()
        memory.Initialization()
    except ValueError as e:
        print("An exception occurred: ", e)