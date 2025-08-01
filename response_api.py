import os
import time
import base64
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

def function_call(): # need to write the function
    response = client.responses.create(  
        model=model,    
        tools=[  
            {  
                "type": "function",  
                "name": "get_weather",  
                "description": "Get the weather for a location",  
                "parameters": {  
                    "type": "object",  
                    "properties": {  
                        "location": {"type": "string"},  
                    },  
                    "required": ["location"],  
                },  
            }  
        ],  
        input=[{"role": "user", "content": "What's the weather in San Francisco?"}],  
    )  
   
    print(response.output_text)     
     
    input = []  
    for output in response.output:  
        if output.type == "function_call":  
            match output.name:  
                case "get_weather":  
                    input.append(  
                        {  
                            "type": "function_call_output",  
                            "call_id": output.call_id,  
                            "output": '{"temperature": "70 degrees"}',  
                        }  
                    )  
                case _:  
                    raise ValueError(f"Unknown function call: {output.name}")  
    second_response = client.responses.create(  
        model=model,  
        previous_response_id=response.id,  
        input=input  
    )  
    return second_response.output_text 

def code_intepreter():
    instructions = "You are a personal math tutor. When asked a math question, write and run code using the python tool to answer the question."

    response = client.responses.create(
        model=model,
        tools=[
            {
                "type": "code_interpreter",
                "container": {"type": "auto"}
            }
        ],
        instructions=instructions,
        input="I need to solve the equation 3x + 11 = 14. Can you help me?",
    )
    return response.output_text

def List_input_items():
    response = client.responses.input_items.list("your response id") 
    return response.model_dump_json(indent=2)

def image_input():

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
        
    image_path = r"some img path"  

    base64_image = encode_image(image_path)

    response = client.responses.create(
        model=model,
        input=[
        {
            "role": "user",
            "content": [
                {
                    "type":"input_text", 
                    "text": "What is in this image?"
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
                ]
            }
        ]
    )
    return response.output_text

def Upload_PDF(): # to upload a pdf file and get the file ID to use it later "assistant-EZVRdGC85AUGdc64B2QZGu"
    file = client.files.create(
        file=open("Book_Summarization_IEEE.pdf", "rb"),
        purpose="assistants"
    )
    result = file.model_dump_json(indent=2)
    file_id = file.id
    return (f"File uploaded successfully. File ID: {file_id}\n{result}")

def pdf_input(): # Process the PDF file we uploaded earlier
    response = client.responses.create(
        model=model,
        input = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file", # input type  
                        "file_id": "assistant-EZVRdGC85AUGdc64B2QZGu" # file ID of the PDF we uploaded earlier
                    },
                    {
                        "type": "input_text", # query type
                        "text": "What are the names this PDF?" #query    
                    }
                ]
            }
        ]
    )
    return response.output_text