/**
 * 公共js库
 * 
 */

'use strict';


/**
 * 为数组增加in_array函数
 * @param {*} element 
 */
Array.prototype.in_array = function (element) {

    for (var i = 0; i < this.length; i++) {
        if (this[i] == element) {
            return true;
        }
    } 
    return false;
}  

/**
 *  获得地址栏中的参数
 * @param {参数名} name 
 */
function getQueryStr(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return unescape(r[2]);
    return null;
}

/**
 *  获得详细收入信息
 * @param {*} income_id 
 */
function getIncomeDetail(income_id) {

    $.get('/apis/income/detail?id=' + income_id, function (res) {
        for (let key in res.info) {
            if(key != 'income_id') {

                app.$set(app.info, key, res.info[key])
            }
        }
    });
}