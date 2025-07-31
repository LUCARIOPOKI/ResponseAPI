import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  # your deployment name
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

client = OpenAI(
    api_key=api_key,
    base_url=f"{endpoint}/openai/v1/",
    default_query={"api-version": "preview"},
)

def get_response():

  start = time.time()
  response = client.responses.create(
      model=model,
      input="My name is 'Poki', sing a song for me"
  )
  api_response = response.output_text 
  response_id = response.id  
  message_id = response.output[0].id 
  end = time.time()
  return (f"Bot: {api_response}\n Response ID: {response_id}\n Message ID: {message_id}\n Time taken: {end - start:.2f} seconds")

def retrieve_response(response_id):
    start = time.time()
    response = client.responses.retrieve(response_id)
    api_response = response.output_text
    end = time.time()
    return (f"Retrieved response: {api_response}\n Time taken: {end - start:.2f} seconds")

def delete_response(response_id): 
    "if you run this code twice with same response_id, it will throw an error"
    """openai.NotFoundError: Error code: 404 - {
        'error': {
        'message': "Response with id 'resp_688b02e41510819f9f5' not found.", 
        'type': 'invalid_request_error', 
        'param': None, 
        'code': None
        }
      }
    """
    start = time.time()
    response = client.responses.delete(response_id) # prints just "None"
    end = time.time()
    return (f"Response deleted successfully .\n Time taken: {end - start:.2f} seconds")

def chaining_response():
    start = time.time()
    response = client.responses.create(
        model=model,
        input="My name is 'Poki', sing a song for me",
    )
    second_response = client.responses.create(
        model=model,
        previous_response_id=response.id,
        input=[{"role":"user","content":"Now, now explain the song you just sang."}]
    )
    response_1 = response.output_text
    response_2 = second_response.output_text
    end = time.time()
    return (f"Bot: {response_1}\n Bot: {response_2}\n Time taken: {end - start:.2f} seconds")

def streaming_response():
  start = time.time()
  response = client.responses.create(
      model=model,
      input="My name is 'Poki', sing a song for me",
      stream=True
  ) 
  end = time.time()
  for event in response:
    if event.type == 'response.output_text.delta':
        print(event.delta, end='')
  print("Time taken: {:.2f} seconds".format(end - start)) 