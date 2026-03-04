const format = (value) => {
    if (!value) return "0,0000";

    const stringValue = value.toString().replace(',', '.');

    const [inteiro, decimal = ""] = stringValue.split('.');

    const decimalTruncado = decimal.padEnd(4, '0').substring(0, 4);

    return `${inteiro},${decimalTruncado}`;
};

export default { format };