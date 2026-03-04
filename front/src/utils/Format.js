const onlyNumbers = (value) => {
    return (value || "").toString().replace(/\D/g, "");
};

const cnpj = (value) => {
    if (!value) return value;

    let string = onlyNumbers(value).padStart(14, "0");

    if (string.length !== 14) return value;

    return string.replace(
        /^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/,
        "$1.$2.$3/$4-$5"
    );
};

const cpf = (value) => {
    if (!value) return value;

    let string = onlyNumbers(value).padStart(11, "0");

    if (string.length !== 11) return value;

    return string.replace(
        /^(\d{3})(\d{3})(\d{3})(\d{2})$/,
        "$1.$2.$3-$4"
    );
};

const telefone = (value) => {
    if (!value) return value;

    const string = onlyNumbers(value);

    if (string.length === 11) {
        return string.replace(
            /^(\d{2})(\d{5})(\d{4})$/,
            "($1) $2-$3"
        );
    }

    if (string.length === 10) {
        return string.replace(
            /^(\d{2})(\d{4})(\d{4})$/,
            "($1) $2-$3"
        );
    }

    return value;
};

export default {
    cpf,
    cnpj,
    telefone
};