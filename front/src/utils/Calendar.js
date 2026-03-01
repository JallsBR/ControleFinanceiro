import moment from "moment";

export default {
    toHoursAndMinutes(totalSeconds) {
        const totalMinutes = Math.floor(totalSeconds / 60);

        const seconds = totalSeconds % 60;
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;

        return { h: hours, m: minutes, s: seconds };
    },
    numberToMonth(number) {
        switch (parseInt(number)) {
            case 1:
                return "Janeiro";
            case 2:
                return "Fevereiro";
            case 3:
                return "Março";
            case 4:
                return "Abril";
            case 5:
                return "Maio";
            case 6:
                return "Junho";
            case 7:
                return "Julho";
            case 8:
                return "Agosto";
            case 9:
                return "Setembro";
            case 10:
                return "Outubro";
            case 11:
                return "Novembro";
            case 12:
                return "Dezembro";
            default:
                return "";
        }
    },
    dateFormat(date, options = {}) {
        const {
            format = 'DD/MM/YYYY'
        } = options;

        return moment(date).format(format);
    },
    calendario(dataAtual, asObjeto = false) {
        const ano = dataAtual.getFullYear();
        const mes = dataAtual.getMonth();

        const primeiroDia = new Date(ano, mes, 1);
        const diaSemanaInicio = primeiroDia.getDay(); // 0 = domingo

        const totalDiasMes = new Date(ano, mes + 1, 0).getDate();
        const diasMesAnterior = new Date(ano, mes, 0).getDate();

        const diasList = []; // Renomeado para evitar confusão com o objeto final

        // Dias do mês anterior (para preencher início)
        for (let i = diaSemanaInicio - 1; i >= 0; i--) {
            const dataObj = new Date(ano, mes - 1, diasMesAnterior - i);
            diasList.push({
                data: dataObj,
                dataStr: dataObj.toISOString().substring(0, 10),
                dia: diasMesAnterior - i,
                isMesAtual: false,
            });
        }

        // Dias do mês atual
        for (let i = 1; i <= totalDiasMes; i++) {
            const dataObj = new Date(ano, mes, i);
            diasList.push({
                data: dataObj,
                dataStr: dataObj.toISOString().substring(0, 10),
                dia: i,
                isMesAtual: true,
            });
        }

        // Dias do mês seguinte (para completar 42 células)
        const diasFaltando = 42 - diasList.length;
        for (let i = 1; i <= diasFaltando; i++) {
            const dataObj = new Date(ano, mes + 1, i);
            diasList.push({
                data: dataObj,
                dataStr: dataObj.toISOString().substring(0, 10),
                dia: i,
                isMesAtual: false,
            });
        }

        if(asObjeto) {
            // Convertendo a lista de dias para um objeto indexado por dataStr
            const diasIndexed = {};
            diasList.forEach(dia => {
                diasIndexed[dia.dataStr] = dia;
            });
            return diasIndexed; // Retorna o objeto indexado
        }

        return diasList; // Retorna o objeto indexado
    },
    isISODateString(dateStr) {
        // Verifica se a string está no formato completo ISO 8601
        return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(dateStr);
    },
    brToDate(dateStr) {
        if (!dateStr || typeof dateStr !== 'string') return null;
        const [day, month, year] = dateStr.split('/');
        if (!day || !month || !year) return null;
        return new Date(parseInt(year, 10), parseInt(month, 10) - 1, parseInt(day, 10));
    }
}
