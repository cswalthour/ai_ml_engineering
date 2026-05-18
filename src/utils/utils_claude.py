# libraries supporting env setup
import os
from anthropic import Anthropic

# import custom modules
from utils.claude_skills.persona_detect import detect_persona, build_system_parameter, detect_temperature

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

    # detect temperature and persona before storing message so cleaned text is saved
    temp_detect = detect_temperature(user_message)
    if temp_detect["has_temperature"]:
        user_message = temp_detect["cleaned_message"]

    persona_detect = detect_persona(user_message)
    if persona_detect["has_persona"]:
        user_message = persona_detect["cleaned_message"]

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
        add_assistant_message(conversation, response_text)

    # return conversation
    return conversation
