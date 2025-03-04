from random import choice, randint

def get_response(user_input) -> str:
    lowered = user_input.lower()
    
    if lowered[:4] == '!rat ':
        return
    else:
        message = user_input[5:]
    return message