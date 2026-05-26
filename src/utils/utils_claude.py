# libraries supporting env setup
from argparse import OPTIONAL
import os
from anthropic import Anthropic

# import custom modules
from .claude_skills.persona_detect import (
    detect_persona, build_system_parameter,
    detect_temperature, detect_stop_seq)

DEFAULT_ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

# method for user add message to the conversation
def add_message(conversation, message):
    conversation.append({"role": "user", "content": message})
    return conversation

# method for assistant add message to the conversation
def add_assistant_message(conversation, message, \
    prefill: list[str] | None = None):

    # if prefill is true, then add the message to the conversation as a prefilled message
    if prefill:
        # add prefilled message to the conversation
        conversation.append({"role": "assistant", "content": prefill})

        # add regular message to the conversation
        conversation.append({"role": "user", "content": message})
        
    else:
        conversation.append({"role": "assistant", "content": message})

    return conversation

# method to execute the conversation
def claude_execute(client:Anthropic, conversation:list, user_message:str,\
    prefill: list[str] | None = None):

    # detect temperature and persona before storing message so cleaned text is saved
    temp_detect = detect_temperature(user_message)
    if temp_detect["has_temperature"]:
        user_message = temp_detect["cleaned_message"]

    persona_detect = detect_persona(user_message)
    if persona_detect["has_persona"]:
        user_message = persona_detect["cleaned_message"]

    # detect if stop sequences used
    stop_detect = detect_stop_seq(user_message)
    if stop_detect["has_stop_seq"]:
        user_message = stop_detect["cleaned_message"]

    # add cleaned user message to the conversation
    add_message(conversation, user_message)

    # build system parameter
    system_parameter = build_system_parameter(persona_detect)

    # client params
    client_params = {
        "model": DEFAULT_ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "messages": conversation,
    }

    # check if system parameter is not empty
    if system_parameter:

        # extract system prompt text from system parameter
        system_prompt_text = system_parameter[0]["text"]

        # add system prompt text to client params
        client_params["system"] = system_prompt_text

    # check if temperature is detected
    if temp_detect["has_temperature"]:
        # add temperature to client params
        client_params["temperature"] = temp_detect["temperature"]

    # if stop seq words used, then add to client_parms
    if stop_detect["has_stop_seq"]:
        # add stop_seq to client params
        client_params["stop_sequences"] = stop_detect["stop_sequences"]

    # execute the conversation using claude client
    # response = client.messages.create(**client_params)

    # stream the response
    with client.messages.stream(**client_params) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

        final_message = stream.get_final_message()

    print()
    
    # check if final message is not empty
    if final_message:
        
        # extract response text from final message
        response_text = final_message.content[0].text

        # add assistant message to the conversation
        add_assistant_message(conversation, response_text, prefill=prefill)

    # return conversation
    return conversation

# method to generate datasets
def generate_dataset(client: Anthropic, prompt: str = None):

    # import json
    import json
    from pathlib import Path

    # default prompt
    prompt = '''

        Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
        that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
        each representing task that requires Python, JSON, or a Regex to complete.

        Example output:
        ```json
        [
            {
                "task": "Description of task",
            },
            ...additional
        ]
        ```

        * Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
        * Focus on tasks that do not require writing much code

        Please generate 3 objects.

    '''

    # nest messages into a list
    messages = []
    
    # execute the conversation using claude client
    conversation = claude_execute(client, messages, prompt, prefill = ["```json"])

    # extract assistant response text from last message
    response_text = conversation[-1]["content"]

    # strip markdown code fences if present
    response_text = response_text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[-1]
    if response_text.endswith("```"):
        response_text = response_text.rsplit("```", 1)[0]

    # convert response to json
    conversation = json.loads(response_text)

    # resolve folder path to root directory
    output_dir = Path(__file__).resolve().parent.parent.parent / "datasets"
    output_file = output_dir / "dataset.json"

    # create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # save json file to local directory
    with open(output_file, "w") as f:
        json.dump(conversation, f, indent=4)

    # return printed location of output file
    return f"Dataset saved to {output_file}\n"