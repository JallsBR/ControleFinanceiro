import dayjs from "dayjs";
import "dayjs/locale/pt-br";

dayjs.locale("pt-br");

export default {

    toHoursAndMinutes(totalSeconds) {
        if (!totalSeconds || totalSeconds < 0) {
            return { h: 0, m: 0, s: 0 };
        }

        const totalMinutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;

        return { h: hours, m: minutes, s: seconds };
    },

    numberToMonth(number) {
        const meses = [
            "", "Janeiro", "Fevereiro", "Março", "Abril",
            "Maio", "Junho", "Julho", "Agosto",
            "Setembro", "Outubro", "Novembro", "Dezembro"
        ];

        return meses[parseInt(number)] || "";
    },

    dateFormat(date, options = {}) {
        const { format = "DD/MM/YYYY" } = options;

        if (!date) return "";

        return dayjs(date).format(format);
    },

    calendario(dataAtual, asObjeto = false) {
        const ano = dayjs(dataAtual).year();
        const mes = dayjs(dataAtual).month(); // 0-11

        const primeiroDia = dayjs().year(ano).month(mes).date(1);
        const diaSemanaInicio = primeiroDia.day(); // 0 = domingo

        const totalDiasMes = primeiroDia.daysInMonth();
        const diasMesAnterior = primeiroDia.subtract(1, "month").daysInMonth();

        const diasList = [];

        // Dias do mês anterior
        for (let i = diaSemanaInicio - 1; i >= 0; i--) {
            const dataObj = primeiroDia
                .subtract(1, "month")
                .date(diasMesAnterior - i);

            diasList.push({
                data: dataObj.toDate(),
                dataStr: dataObj.format("YYYY-MM-DD"),
                dia: diasMesAnterior - i,
                isMesAtual: false,
            });
        }

        // Dias do mês atual
        for (let i = 1; i <= totalDiasMes; i++) {
            const dataObj = primeiroDia.date(i);

            diasList.push({
                data: dataObj.toDate(),
                dataStr: dataObj.format("YYYY-MM-DD"),
                dia: i,
                isMesAtual: true,
            });
        }

        // Completar até 42 células
        const diasFaltando = 42 - diasList.length;

        for (let i = 1; i <= diasFaltando; i++) {
            const dataObj = primeiroDia.add(1, "month").date(i);

            diasList.push({
                data: dataObj.toDate(),
                dataStr: dataObj.format("YYYY-MM-DD"),
                dia: i,
                isMesAtual: false,
            });
        }

        if (asObjeto) {
            const diasIndexed = {};
            diasList.forEach(dia => {
                diasIndexed[dia.dataStr] = dia;
            });
            return diasIndexed;
        }

        return diasList;
    },

    isISODateString(dateStr) {
        if (!dateStr || typeof dateStr !== "string") return false;
        return dayjs(dateStr, dayjs.ISO_8601, true).isValid();
    },

    brToDate(dateStr) {
        if (!dateStr || typeof dateStr !== "string") return null;

        const parsed = dayjs(dateStr, "DD/MM/YYYY", true);

        if (!parsed.isValid()) return null;

        return parsed.toDate();
    }
};