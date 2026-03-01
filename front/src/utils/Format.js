const cnpj = (string) => {
    if(!string) return string;
    while (string.length < 14) string = "0" + string;
    return string.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5")
}
const cpf = (string) => {
    if(!string) return string;
    while (string.length < 11) string = "0" + string;
    return string.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4")
}
const telefone = (string) => {
    if(!string) return string;
    // Remove caracteres não numéricos
    string = string.replace(/\D/g, '');
    // Se tiver 11 dígitos (celular com 9º dígito)
    if(string.length === 11) {
        return string.replace(/^(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
    }
    // Se tiver 10 dígitos (telefone fixo)
    if(string.length === 10) {
        return string.replace(/^(\d{2})(\d{4})(\d{4})/, "($1) $2-$3");
    }
    // Retorna sem formatação se não tiver 10 ou 11 dígitos
    return string;
}

export default {
    cnpj,
    cpf,
    telefone
}
