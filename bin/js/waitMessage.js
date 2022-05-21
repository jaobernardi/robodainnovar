
const done = arguments[arguments.length - 1]

function handle_message(message) {
    if (!message.id.fromMe){
        done({
            "user": {
                "phonenumber": message.from.user,
                "id": message.from._serialized,
                "name": message.chat.contact.__x_notifyName
            },
            "message": {
                "type": message.type,
                "chatID": message.chat.id._serialized,
                "id": message.id._serialized,
                "text": message.text,
            }
        })
    }
}


window.Store.Msg.once("add", handle_message)