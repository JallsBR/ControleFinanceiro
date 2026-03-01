import moment from 'moment';

function recovery (options) {
    const {
        driver,
        defaultFilter = {},
        defaultOrder = {},
        defaultOther = {}
    } = options;

    let order = defaultOrder;
    let filter = defaultFilter;
    let other = defaultOther;

    let session = sessionStorage.getItem(driver);
    if (session) {
        session = JSON.parse(session);
        if(session.filter) {
            for(let filterKey in session.filter) {
                const filterField = session.filter[filterKey];
                if(Array.isArray(filterField)) {
                    session.filter[filterKey] = filterField.map((filterFieldValue) => {
                        if (isDateField(filterFieldValue)) {
                            return new Date(Date.parse(filterFieldValue));
                        }

                        return filterFieldValue;
                    });
                } else if(filterField){
                    let value = filterField;
                    if (isDateField(value)) {
                        value = new Date(Date.parse(value));
                    }
                    session.filter[filterKey] = value;
                }
            }
            filter = session.filter;
        }
        if(session.other) {
            for(let otherKey in session.other) {
                const otherField = session.other[otherKey];
                if(Array.isArray(otherField)) {
                    session.other[otherKey] = otherField.map((otherFieldValue) => {
                        if (isDateField(otherFieldValue)) {
                            return new Date(Date.parse(otherFieldValue));
                        }

                        return otherFieldValue;
                    });
                } else if(otherField){
                    let value = otherField;
                    if (isDateField(value)) {
                        value = new Date(Date.parse(value));
                    }
                    session.other[otherKey] = value;
                }
            }
            other = session.other;
        }
        if(session.order) {
            order = session.order;
        }
    }

    return {
        order,
        filter,
        other
    }
}

const toQueryString = (filterOriginal, params = [], name = 'filter', personal = {}) => {
    // Copiando o objeto para não modificar o original
    let filter = { ...filterOriginal };
    if(Object.keys(filter).length > 0) {
        for(const filterKey in filter) {
            const filterField = filter[filterKey];
            if(personal[filterKey]) {
                personal[filterKey](params, filterField, name, filterKey, filter);
            } else if(Array.isArray(filterField)){
                Array.from(
                    isDateRangeField(filterField)
                        ? dateRangeField(filterField)
                        : filterField
                ).forEach((value) => {
                    params.push(`${name}[${filterKey}][]=${value}`);
                });
            } else if (isDateField(filterField)){
                params.push(`${name}[${filterKey}]=${dateField(filterField)}`);
            } else if(filterField) {
                params.push(`${name}[${filterKey}]=${filterField}`);
            }
        }
    }

    return params;
}

const dateRangeField = (fields) => {
    const items = Array.from(fields).filter((value) => isDateField(value));

    // if (items.length === 1) {
    //     items.push(items[0]);
    // }
    return items.map((item, index) => {
        const date = new Date(Date.parse(item));
        if (index) {
            date.setUTCHours(23, 59, 59, 999);
        } else {
            date.setUTCHours(0, 0, 0, 0);
        }

        return dateField(date);
    });
}

const isDateRangeField = (fields) => {
    const items = Array.from(fields || []);
    if (!items.length) return false;

    const item = items.find((field) => isDateField(field));
    return !!item;
}

const isDateField = (field) => {
    if(field instanceof Date) return true;
    if (!field || !isNaN(field)) return false;
    /**
     * Regex valida formatos de datas
     * DD-MM-YYYY
     * DD/MM/YYYY
     * YYYY-MM-DD
     * YYYY-MM-DDT00:00:00.0000Z
     */
    const regexData = /^\d{2}-\d{2}-\d{4}$|^\d{4}-\d{2}-\d{2}$|^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;

    return regexData.test(field);
}

const dateField = (field) => {
    const date = new Date(
        field instanceof Date
        ? field
        : Date.parse(field)
    );
    return date.toJSON();
}

export default {
    onBlurCalendar(event) {
        if(event.value){
            if (moment(event.value, 'DD/MM/YYYY', true).isValid()) {
                return;
            }

            let value = event.value.replace(/\D/g, '');

            if(value.length == 8){
                let dia = value.substring(0,2);
                let mes = value.substring(2,4);
                let ano = value.substring(4,8);

                return moment(`${ano}-${mes}-${dia}`).format('DD/MM/YYYY');
            } else {
                if(value.length == 2){
                    return value + '/';
                } else if(value.length == 4){
                    let dia = value.substring(0,2);
                    let mes = value.substring(2,4);
                    return dia + '/' + mes + '/';
                } else {
                    return value;
                }
            }
        }
    },
    toQueryString,
    recovery
}
