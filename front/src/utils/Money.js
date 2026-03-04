const format = (amount, options = {}) => {
    const {
        currency = false,
        locale = "pt-BR",
        minimumFractionDigits = 2,
        maximumFractionDigits = 2
    } = options;

    const formatter = new Intl.NumberFormat(locale, {
        style: currency ? "currency" : "decimal",
        currency: currency ? "BRL" : undefined,
        minimumFractionDigits,
        maximumFractionDigits
    });

    return formatter.format(amount || 0);
};

export default {
    format
};