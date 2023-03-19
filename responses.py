def handle_response(message) -> str:
    p_message = message.lower()

    if p_message == 'hello':
        return 'Hey there!'

    if p_message == 'roll':
        return 'D20'

    if p_message == "help":
        return "`This is a help message that you can modify.`"

    if p_message == "Hush: private_send":
        return '`What user do you want me to message?`'
