# Ollama Python Library

The Ollama Python library provides the easiest way to integrate Python 3.8+ projects with [Ollama](https://github.com/ollama/ollama).

## Install

```sh
pip install ollama
```

## Usage

```python
import ollama
response = ollama.chat(model='llama3', messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])
print(response['message']['content'])
```

## Streaming responses

Response streaming can be enabled by setting `stream=True`, modifying function calls to return a Python generator where each part is an object in the stream.

```python
import ollama

stream = ollama.chat(
    model='llama3',
    messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)
```

## API

The Ollama Python library's API is designed around the [Ollama REST API](https://github.com/ollama/ollama/blob/main/docs/api.md)

### Chat

```python
ollama.chat(model='llama3', messages=[{'role': 'user', 'content': 'Why is the sky blue?'}])
```

### Generate

```python
ollama.generate(model='llama3', prompt='Why is the sky blue?')
```

### List

```python
ollama.list()
```

### Show

```python
ollama.show('llama3')
```

### Create

```python
modelfile='''
FROM llama3
SYSTEM You are mario from super mario bros.
'''

ollama.create(model='example', modelfile=modelfile)
```

### Copy

```python
ollama.copy('llama3', 'user/llama3')
```

### Delete

```python
ollama.delete('llama3')
```

### Pull

```python
ollama.pull('llama3')
```

### Push

```python
ollama.push('user/llama3')
```

### Embeddings

```python
ollama.embeddings(model='llama3', prompt='The sky is blue because of rayleigh scattering')
```

### Ps

```python
ollama.ps()
```

## Custom client

A custom client can be created with the following fields:

- `host`: The Ollama host to connect to
- `timeout`: The timeout for requests

```python
from ollama import Client
client = Client(host='http://localhost:11434')
response = client.chat(model='llama3', messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])
```

## Async client

```python
import asyncio
from ollama import AsyncClient

async def chat():
  message = {'role': 'user', 'content': 'Why is the sky blue?'}
  response = await AsyncClient().chat(model='llama3', messages=[message])

asyncio.run(chat())
```

Setting `stream=True` modifies functions to return a Python asynchronous generator:

```python
import asyncio
from ollama import AsyncClient

async def chat():
  message = {'role': 'user', 'content': 'Why is the sky blue?'}
  async for part in await AsyncClient().chat(model='llama3', messages=[message], stream=True):
    print(part['message']['content'], end='', flush=True)

asyncio.run(chat())
```

## Errors

Errors are raised if requests return an error status or if an error is detected while streaming.

```python
model = 'does-not-yet-exist'

try:
  ollama.chat(model)
except ollama.ResponseError as e:
  print('Error:', e.error)
  if e.status_code == 404:
    ollama.pull(model)
```

## Assistants API v1 Beta

The Assistants API is an extension providing integrated state management, similar to the @OpenAI Assistants API. 

All state information is stored in a Docker container and may remain as such on local devices, or be deployed in a data center of choice. Built with a focus on absolute privacy whilst implementing advanced infrastructure required to host a scalable and diverse number of distinct AI entities.


### Initializing the Assistants API v1 Beta Client

```python
from ollama import OllamaClient

# Initialize the assistants client 
client = OllamaClient()

# Creating a User 
user1 = client.user_service.create_user(name='Test')
print(f"Created user with ID: {user1.id}")

# Creating an Assistant

assistant = client.assistant_service.create_assistant(
    name='Mathy',
    description='My helpful maths tutor',
    model='llama3.1',
    instructions='Be as kind, intelligent, and helpful',
    tools=[{"type": "code_interpreter"}]
)

print(f"Created assistant with ID: {assistant.id}")

# Creating a Thread

thread = client.thread_service.create_thread()
print(thread)

# Creating a Message

client.message_service.create_message(
    thread_id=thread.id,
    content='Can you help me solve a math equation?',
    role='user',
    sender_id=user1.id
)

# Creating Run

run = client.run_service.create_run(assistant_id=assistant.id, thread_id=thread.id)
print(run)
```
### Steps

Set the initial state and execute a message by following the steps above. The message is sent to the assistant, and conversation dialogue is automatically saved to a thread instance.



