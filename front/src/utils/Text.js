const validaEmail = (input) => {
    const emails = Array.isArray(input) ? input : [input];

    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return emails.every(email =>
        typeof email === "string" &&
        re.test(email.trim())
    );
};

const capitalizeFirstLetter = (text = "") =>
    text
        ? text[0].toUpperCase() + text.slice(1).toLowerCase()
        : "";

export default {
    validaEmail,
    capitalizeFirstLetter
};