# libraries supporting env setup
import os
from anthropic import Anthropic

# import custom modules
from utils.claude_skills.persona_detect import detect_persona, build_system_parameter

DEFAULT_ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

# method for user add message to the conversation
def add_message(conversation, message):
    conversation.append({"role": "user", "content": message})
    return conversation

# method for assistant add message to the conversation
def add_assistant_message(conversation, message):
    conversation.append({"role": "assistant", "content": message})
    return conversation

# method to execute the conversation
def claude_execute(client:Anthropic, conversation:list, user_message:str):

    # add user message to the conversation
    add_message(conversation, user_message)

    # detect persona
    persona_detect = detect_persona(user_message)

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

    # execute the conversation using claude client
    response = client.messages.create(**client_params)

    # get the response and print it in console
    response_text = response.content[0].text
    print(response_text)

    # add assistant message to the conversation
    add_assistant_message(conversation, response_text)

    return conversation
