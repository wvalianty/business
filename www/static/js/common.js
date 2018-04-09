/**
 * 公共js库
 * 
 */

'use strict';
layui.config({
    base: '/static/js/'
}).use(['jquery', 'layer', 'element', 'navtab'], function() {
    window.jQuery = window.$ = layui.jquery;
    window.layer = layui.layer;
    var element = layui.element(),
        navtab = layui.navtab({
            elem: '.larry-tab-box'
        });

    $('.add-btn,.edit-btn').click(function() {

        let url = this.dataset.url;
        if (!url) {
            return;
        }

        let title = this.dataset.title || '这是一个弹出框';
        let area = this.dataset.area || "600px,400px";
        layer.open({
            type: 2,
            content: [url, 'no'],
            area: area.split(','),
            title: title,
            maxmin: true,
        });
    });
});