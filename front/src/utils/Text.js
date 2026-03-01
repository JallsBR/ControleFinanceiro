function validaEmail(emails) {
    let re = /\S+@\S+\.\S+/;
    for(let val of emails) {
        if(!re.test(val)) {
            return false;
        }
    }
    return true;
}

export default {
    validaEmail,
    capitalizeFirstLetter(text) {
        return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
    }
}
