export default {
    format(value){
        value = parseFloat(value);
        if(isNaN(value)) value = 0;
        // 4 casas decimais sem arredondar
        return (Math.trunc(value * 10000) / 10000).toFixed(4).replace('.',',');
    }
}
