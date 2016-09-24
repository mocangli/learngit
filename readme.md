##### 采用django框架实现的文件管理系统，主要实现了文件的上传、下载、搜索、删除及文件上传后的审批流程。

##### django的优点：大而全，作为一个开箱即用的工具箱式框架，Django已经内 建了模板、表单、路由、认证、基本数据库管理等等，能够让人把注意力集中在view层的开发上，而且有翻译完成度极高的中文文档！

##### 缺点：优点即缺点，django由于能够实现各种各样的功能，因此学习成本比较高，相当于重新学习一门语言。而且用起来没有一些微框架来的灵活，这是最头痛的一点，开发者只能在它划出的规则内办事，稍有逾越就会带来各种各样的麻烦。

##### 前端框架采用的是uikit，个人比较喜欢它的简洁，而且有丰富的图标和组件

##### Django 支持 sqlite3, MySQL, PostgreSQL等数据库，只需要在settings.py中配置即可，不用更改models.py中的代码，丰富的API极大的方便了使用。我的数据库采用的是mysql，配置的时候要注意官方文档说明了支持MySQLdb、mysqlclient、MySQL Connector/Python 三种数据库驱动。其中MySQLdb目前只支持python2，而最新的python3.5在安装MySQL Connector/Python 时也容易安装失败，因此我选择的是mysqlclient，这也是django官方文档推荐的选择。

##### 前端的我采用了MVVM的模式，用的是尤雨溪老师的vue.js，不得不说vue真的很好用，view层和model层分离使得代码的结构一下子变得很清晰，vue必火！

##### 部署采用的是superversior + ngnix + mysql 来实现的，其中：

* Nginx：高性能Web服务器+负责反向代理；

* Supervisor：监控服务进程的工具；

* MySQL：数据库服务
