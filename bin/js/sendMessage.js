const done = arguments[arguments.length - 1]



async function sendMsg(chatId, message, options = {}) {
    const chatWid = window.Store.WidFactory.createWid(chatId);
    const chat = await window.Store.Chat.find(chatWid);

    window.WWebJS.sendSeen(chatId);

    if (options.attachment) {
        options.caption = message;
        message = '';
    }

    const msg = await window.WWebJS.sendMessage(chat, message, options, true);
    return msg.serialize();
}


await sendMsg(arguments[0], arguments[1], arguments[2])