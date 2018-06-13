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

/**
 *  获得表单初始化数据， 要使用同步的ajax方法，
 * 要保证先渲染数据，再渲染页面
 * @param {*} vue  对象
 * @param {*} module  模块名
 * @param {*} cb  成功后的回调函数
 */
function getFromInit(vueObj, module, cb) {

    let id = getQueryStr('id') || 0;
    $.ajax({
        type: 'get',
        url: '/apis/' + module + '/formInit?id=' + id,
        async: false,
        success: function (data) {
            vueObj.other = data;

            if (typeof cb == 'function') {
                cb(vueObj, id, data);
            }
        }
    })
}