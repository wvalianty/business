/**
 * 公共js库
 * 
 */

'use strict';

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