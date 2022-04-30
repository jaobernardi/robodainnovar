async function sendSeen(chatID) {
    await window.WWebJS.sendSeen(chatID)
}

sendSeen(arguments[0])