
const done = arguments[arguments.length - 1]

function handle_message(message, ignore_checks) {
    if (message.type == 'e2e_notification' || !message.isNewMsg) {
        return
    }
    
    if (!message.id.fromMe){
        window.Store.Msg.removeListener();
        done({
            "type": message.type,
            "user": {
                "phonenumber": message.from.user,
                "id": message.from._serialized,
                "name": message.chat.contact.__x_notifyName ? message.chat.contact.__x_notifyName : ''
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

window.Store.call_message = handle_message
window.Store.Msg.on("add", handle_message)