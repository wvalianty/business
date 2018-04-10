layui.config({
    base: '/static/js/'
}).use(['form', 'layer', 'jquery', 'laypage'], function () {
    var form = layui.form(),
        layer = parent.layer === undefined ? layui.layer : parent.layer,
        laypage = layui.laypage,
        $ = layui.jquery;

    var app = new Vue({
        el: '#app',
        data: {
            list: [],
            currPage: 1,
            module: '' // 当前模块
        },
        methods: {

            getLists: function (page, keyword='') {
                var self = this;

                let url = '/apis/' + self.module +'/index?page=' + page;
                if (keyword != '') {
                    url += '&keyword=' + keyword;
                }

                $.get(url, function (data) {
                    self.list = data.list;

                    laypage({
                        cont: 'page',
                        pages: data.page[0], //总页数
                        curr: data.page[1],
                        groups: 5, //连续显示分页数
                        jump: function (obj, first) {
                            //得到了当前页，用于向服务端请求对应数据
                            self.currPage = obj.curr;
                            if (!first) {

                                self.getLists(self.currPage);
                            }
                        }
                    });
                });
            },
            // 添加点击事件
            addClick: function () {

                var self = this; 
                /**
                 * 点击新增按钮和编辑按钮弹出新增和编辑页面
                 */
                $('.add-btn,.edit-btn').unbind('click').click(function () {
                   
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
                        end: function () {
                            self.getLists(self.currPage);
                        }
                    });
                });

                /**
                 * 删除事件
                 */
                $('.del-btn').unbind('click').click(function () {

                    if (!confirm('确认要删除吗？')) {
                        return;
                    }

                    let url = this.dataset.url;
                    if (!url) {
                        layer.msg('缺少链接');
                        return;
                    }

                    $.get(url, function (data) {
                        layer.msg(data.msg);
                        // 删除成功，刷新页面
                        if (data.status) {
                            self.getLists(self.currPage);
                        }
                    });
                });

                /**
                 * 搜索事件
                 */
                form.on("submit(searchForm)", function (data) {

                    self.getLists(1, data.field.keyword)
                    
                    return false;
                });
            }
        },
        mounted: function () {

            this.module = location.pathname.split('/')[1];
            this.getLists(this.currPage);
        },
        updated: function () {

            // 等数据渲染完成，再绑定事件
            this.addClick();
        }
    });
});