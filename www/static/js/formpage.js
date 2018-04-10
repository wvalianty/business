// 如果存在id，则说明是编辑页面
$(function(){
    
    let id = getQueryStr('id');
    var app = new Vue({
        el: '#form',
        data: {
            info: {},
            other: {},
            module: ''  // 当前模块
        },
        mounted: function () {
            let self = this;
            this.module = location.pathname.split('/')[1];

            if (id && id != '') {
                action = 'edit';

                let url = '/apis/' + this.module + '/info?id=' + id;
                $.get(url, function (data) {
                    self.info = data.info;
                });
            }
            
            // 钩子函数，初始化的时候执行
            if (typeof (hook_init) == 'function') {
                hook_init(self)
            }
        },
        updated: function () {

            var self = this;
            
            layui.config({
                base: "/static/js/"
            }).use(['form', 'layer', 'laydate'], function () {

                var form = layui.form(),
                    layer = parent.layer === undefined ? layui.layer : parent.layer,
                    laydate = layui.laydate;

                // 表单提交事件
                form.on("submit(submitForm)", function (data) {

                    let url = '/apis/' + self.module + '/form';

                    $.post(url, data.field, function (data, textStatus, xhr) {

                        layer.msg(data.msg);
                        if (data.status) {
                            var index = parent.layer.getFrameIndex(window.name); //先得到当前iframe层的索引
                            parent.layer.close(index); //再执行关闭
                        }
                    });
                    return false;
                });
            });
            
        }
    })
})