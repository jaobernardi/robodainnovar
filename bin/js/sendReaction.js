const done = arguments[arguments.length - 1]



async function sendMsg(chatId, message, reaction) {
    const chatWid = window.Store.WidFactory.createWid(chatId);
    const chat = await window.Store.Chat.find(chatWid);

    window.WWebJS.sendSeen(chatId);

    await window.WWebJS.sendReaction(message, reaction);
}

setTimeout(() => {
    sendMsg(arguments[0], arguments[1], arguments[2])
    .then(e => console.log('Sent reaction'))
}, 200);
