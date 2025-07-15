class Protocols:

    class Response:
        NICKNAME = "protocol.request_nickname"
        QUESTIONS = "protocol.questions"
        START = "protocol.start"
        OPPONENT = "protocol.opponent"
        OPPONENT_ADVANCE = "protocol.opponent_advance"
        ANSWER_VALID = "protocol.answer_valid"
        ANSWER_INVALID = "protocol.answer_invalid"
        WINNER = "protocol.winner"
        OPPONENT_LEFT = "protocol.opponent_left"
        ACTIVATE_SUPER_POWER = "activate_super_power"
        CHAT_MESSAGE = "protocol.chat_message"

    class Request:
        ANSWER = "protocol.answer"
        NICKNAME = "protocol.send_nickname"
        LEAVE = "protocol.leave"
        JOIN_ROOM = "protocol.join_room"
        CREATE_GAME = "protocol.create_game"
        GET_POS = "protocol.get_pos"
        UPDATE_POSITION = "protocol.update_position"
        SEND_CHAT_MESSAGE = "protocol.send_chat_message"
