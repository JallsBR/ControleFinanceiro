import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";

dayjs.extend(customParseFormat);

/**
 * Formato padrão do backend Django
 * 2026-03-01 03:22:03.172821
 */
const DJANGO_DATETIME_FORMAT = "YYYY-MM-DD HH:mm:ss.SSSSSS";
const DATE_ONLY_FORMAT = "YYYY-MM-DD";

/* =========================================================
   DATE HELPERS
========================================================= */

const isDateField = (field) => {
    if (!field) return false;

    if (field instanceof Date) return true;

    if (typeof field !== "string") return false;

    return (
        dayjs(field, DJANGO_DATETIME_FORMAT, true).isValid() ||
        dayjs(field, DATE_ONLY_FORMAT, true).isValid() ||
        dayjs(field, "DD/MM/YYYY", true).isValid()
    );
};

const parseDate = (field) => {
    if (field instanceof Date) return dayjs(field);

    return (
        dayjs(field, DJANGO_DATETIME_FORMAT, true).isValid()
            ? dayjs(field, DJANGO_DATETIME_FORMAT)
            : dayjs(field)
    );
};

const dateField = (field) => {
    return parseDate(field).format(DJANGO_DATETIME_FORMAT);
};

const isDateRangeField = (fields) => {
    if (!Array.isArray(fields)) return false;
    return fields.some(isDateField);
};

const dateRangeField = (fields) => {
    return fields
        .filter(isDateField)
        .map((item, index) => {
            const date = parseDate(item);

            return index
                ? date.endOf("day").format(DJANGO_DATETIME_FORMAT)
                : date.startOf("day").format(DJANGO_DATETIME_FORMAT);
        });
};

/* =========================================================
   RECOVERY (sessionStorage)
========================================================= */

const recovery = ({ driver, defaultFilter = {}, defaultOrder = {}, defaultOther = {} }) => {
    let order = defaultOrder;
    let filter = defaultFilter;
    let other = defaultOther;

    const session = sessionStorage.getItem(driver);

    if (!session) {
        return { order, filter, other };
    }

    const parsed = JSON.parse(session);

    if (parsed.filter) {
        Object.keys(parsed.filter).forEach(key => {
            const value = parsed.filter[key];

            if (Array.isArray(value)) {
                parsed.filter[key] = value.map(v =>
                    isDateField(v) ? parseDate(v).toDate() : v
                );
            } else if (isDateField(value)) {
                parsed.filter[key] = parseDate(value).toDate();
            }
        });

        filter = parsed.filter;
    }

    if (parsed.other) {
        Object.keys(parsed.other).forEach(key => {
            const value = parsed.other[key];

            if (Array.isArray(value)) {
                parsed.other[key] = value.map(v =>
                    isDateField(v) ? parseDate(v).toDate() : v
                );
            } else if (isDateField(value)) {
                parsed.other[key] = parseDate(value).toDate();
            }
        });

        other = parsed.other;
    }

    if (parsed.order) {
        order = parsed.order;
    }

    return { order, filter, other };
};

/* =========================================================
   QUERY STRING BUILDER
========================================================= */

const toQueryString = (
    filterOriginal,
    params = [],
    name = "filter",
    personal = {}
) => {
    const filter = { ...filterOriginal };

    Object.keys(filter).forEach(filterKey => {
        const value = filter[filterKey];

        if (personal[filterKey]) {
            personal[filterKey](params, value, name, filterKey, filter);
            return;
        }

        if (Array.isArray(value)) {
            const values = isDateRangeField(value)
                ? dateRangeField(value)
                : value;

            values.forEach(v => {
                params.push(`${name}[${filterKey}][]=${v}`);
            });

            return;
        }

        if (isDateField(value)) {
            params.push(`${name}[${filterKey}]=${dateField(value)}`);
            return;
        }

        if (value !== undefined && value !== null && value !== "") {
            params.push(`${name}[${filterKey}]=${value}`);
        }
    });

    return params;
};

/* =========================================================
   INPUT CALENDAR FORMATTER (blur)
========================================================= */

const onBlurCalendar = (event) => {
    if (!event?.value) return;

    const parsed = dayjs(event.value, "DD/MM/YYYY", true);

    if (parsed.isValid()) return;

    const value = event.value.replace(/\D/g, "");

    if (value.length === 8) {
        const dia = value.substring(0, 2);
        const mes = value.substring(2, 4);
        const ano = value.substring(4, 8);

        return dayjs(`${ano}-${mes}-${dia}`)
            .format("DD/MM/YYYY");
    }

    if (value.length === 2) return value + "/";
    if (value.length === 4) {
        const dia = value.substring(0, 2);
        const mes = value.substring(2, 4);
        return `${dia}/${mes}/`;
    }

    return value;
};

/* =========================================================
   EXPORT
========================================================= */

export default {
    recovery,
    toQueryString,
    onBlurCalendar
};