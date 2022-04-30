
const done = arguments[arguments.length - 1]

function handle_message(message) {
    if (!message.id.fromMe){
        done({
            "user": {
                "userID": message.from.user
            },
            "message": {
                "chatID": message.chat.id._serialized,
                "id": message.id._serialized,
                "text": message.text,
            }
        })
    }
}


window.Store.Msg.once("add", handle_message)