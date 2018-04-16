var app;
$(function(){
    app = new Vue({
        el: '#app',
        data: {
            list: [],
            currPage: 1,
            other: [],
            page: [],
            params: {}, // 当前页面查询参数
            module: '' // 当前模块
        },
        methods: {
            
            // 获得数据列表
            getLists: function (page, params = '', action = "index") {
                var self = this;

                let url = '/apis/' + self.module + '/' + action +'?page=' + page;

                if (params == '' && JSON.stringify(this.params) != "{}") {
                    params = this.params;
                }

                if (typeof params == 'string' && params != '') {
                    url += '&keyword=' + params;
                    this.params['keyword'] = params;
                } else if (typeof params == 'object') {
                    for (const ele in params) {
                        if (params.hasOwnProperty(ele)) {
                            const val = params[ele];
                            if(val != '') {
                                url += '&' + ele + '=' + val;
                                this.params[ele] = val;
                            }
                        }
                    }
                }

                $.get(url, function (data) {
                    self.list = data.list;
                    self.page = data.page;
                    if (typeof data.other != 'undefined') {
                        self.other = data.other
                    }
                });
            },
            // 添加点击事件
            addClick: function (layer, form) {

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

                // 确定事件
                $('.identify-btn').unbind('click').click(function(){
                     if (!confirm('确定吗？')) {
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

                // 查询全部
                $('#selectAll').unbind('click').click(function(){
                    self.params = {};
                    $("#searchForm select").map((index, ele) => {
                        $(ele).val('');
                    });
                    layui.form().render('select');
                    self.getLists(1);
                });

                /**
                 * 搜索事件
                 */
                form.on("submit(searchForm)", function (data) {

                    self.getLists(1, data.field)

                    return false;
                });
            }
        },
        mounted: function () {
            
            keyword = getQueryStr("keyword") || '';
            action = getQueryStr("action") || 'index';
            this.module = location.pathname.split('/')[1];
            this.getLists(this.currPage, keyword, action);
        },
        updated: function () {
            var slef = this;
            layui.config({
                base: '/static/js/'
            }).use(['form', 'layer', 'jquery', 'laypage'], function () {
                var form = layui.form(),
                    layer = parent.layer === undefined ? layui.layer : parent.layer,
                    laypage = layui.laypage,
                    $ = layui.jquery;

                // 等数据渲染完成，再绑定事件
                slef.addClick(layer, form);

                laypage({
                    cont: 'page',
                    pages: page[0], //总页数
                    curr: page[1],
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
        }
    });
});


