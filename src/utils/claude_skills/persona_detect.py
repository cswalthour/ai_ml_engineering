## 1. **Message Reception & Parsing**
def process_user_message(user_message: str):
    """Initial message intake"""
    # Normalize the message
    message = user_message.strip()
    
    return message

## 2. **Persona Detection**
import re

def detect_persona(message: str) -> dict:
    """
    Detect if a persona is specified in the message
    Returns: {
        'has_persona': bool,
        'persona_type': str or None,
        'cleaned_message': str
    }
    """
    
    # Common persona patterns
    persona_patterns = [
        r"(?:act|speak|respond|talk|behave)\s+(?:as|like)\s+(?:a|an)?\s*([^.!?\n]+)",
        r"(?:you are|you're)\s+(?:a|an)?\s*([^.!?\n]+)",
        r"(?:pretend|imagine)\s+(?:you are|you're)\s+(?:a|an)?\s*([^.!?\n]+)",
        r"in the role of\s+(?:a|an)?\s*([^.!?\n]+)",
        r"as\s+(?:a|an)\s+([^.!?\n]+),?\s+(?:please|help|tell)",
    ]
    
    for pattern in persona_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            persona = match.group(1).strip()
            # Remove the persona instruction from message
            cleaned_message = re.sub(pattern, '', message, flags=re.IGNORECASE).strip()
            
            return {
                'has_persona': True,
                'persona_type': persona,
                'cleaned_message': cleaned_message or message
            }
    
    return {
        'has_persona': False,
        'persona_type': None,
        'cleaned_message': message
    }

## 3. **Persona Template Mapping**
PERSONA_TEMPLATES = {
    'teacher': "You are a patient and knowledgeable teacher. Explain concepts clearly with examples.",
    'expert': "You are an expert in your field. Provide detailed, technical insights.",
    'friend': "You are a friendly, casual companion. Be warm and conversational.",
    'coach': "You are a motivational coach. Be encouraging and action-oriented.",
    'analyst': "You are a critical analyst. Provide balanced, objective analysis.",
    # Add more predefined personas
}

def map_persona_to_system_prompt(persona_type: str) -> str:
    """
    Convert detected persona into system prompt
    """
    persona_lower = persona_type.lower()
    
    # Check for predefined templates
    for key, template in PERSONA_TEMPLATES.items():
        if key in persona_lower:
            return template
    
    # If no template match, create dynamic prompt
    return f"You are {persona_type}. Respond accordingly in character."

## 4. **Temperature Detection**
TEMPERATURE_PATTERN = re.compile(
    r"(?:set\s+)?temp(?:erature)?\s*[=:]\s*([0-1](?:\.\d+)?)",
    re.IGNORECASE,
)

def detect_temperature(message: str) -> dict:
    """
    Detect if a temperature value is specified in the message.
    Returns: {
        'has_temperature': bool,
        'temperature': float or None,
        'cleaned_message': str
    }
    """
    match = TEMPERATURE_PATTERN.search(message)
    if match:
        return {
            'has_temperature': True,
            'temperature': float(match.group(1)),
            'cleaned_message': TEMPERATURE_PATTERN.sub('', message).strip(),
        }
    return {
        'has_temperature': False,
        'temperature': None,
        'cleaned_message': message,
    }

## 5. **System Parameter Construction**
def build_system_parameter(persona_info: dict) -> list:
    """
    Create system parameter for client.messages.create()
    """
    if not persona_info['has_persona']:
        return []  # No system message needed
    
    system_prompt = map_persona_to_system_prompt(persona_info['persona_type'])

    print(f"System prompt extracted: {system_prompt}\n")
    
    return [
        {
            "type": "text",
            "text": system_prompt
        }
    ]