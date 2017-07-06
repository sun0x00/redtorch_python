RedTorch
^^^^^^^^

简介
-----

本项目致力于为期货多账户管理提供便捷的的操作方法，由开源项目 `vnpy <http://www.vnpy.org/ >`_ 修改而来,在使用本项目之前，请首先了解vnpy的相关协议和内容。

当前项目仅支持CTP接口的动态管理

环境准备
----

请根据 `vnpy-v1.6.2 <https://github.com/vnpy/vnpy/tree/v1.6.2>`_ 准备相关软件环境

安装
----

下载 `vnpy-v1.6.2 <https://github.com/vnpy/vnpy/tree/v1.6.2>`_ 或通过命令pip install vnpy==1.6.2安装vnpy

下载本项目，使用IDE导入，推荐使用 `PyCharm <https://www.jetbrains.com/pycharm/>`_ ,运行redtorch/trader/run.py

**如果使用解压安装vnpy,可能导致redtorch无法访问vnpy中的包,请将vnpy复制到redtorch同级目录,如下**

 + redtorch_project

    - redtorck
    - vnpy

兼容性说明
-------

当前版本基于vnpy 1.6.2修改,主要引用了vnpy.api包中的内容,其他包名均已变更,修改不影响vnpy原版的正常使用,因此请注意,vnpy/api包中的内容为vnpy和redtorch共用，请谨慎修改

有兼容vnpy后续版本的计划

联系作者
------
sun0x00@gmail.com

License
---------
MIT

用户在遵循本项目协议的同时，如果用户下载、安装、使用本项目中所提供的软件，软件作者对任何原因在使用本项目中提供的软件时可能对用户自己或他人造成的任何形式的损失和伤害不承担任何责任。
作者有权根据有关法律、法规的变化修改本项目协议。修改后的协议会随附于本项目的新版本中。
当发生有关争议时，以最新的协议文本为准。如果用户不同意改动的内容，用户可以自行删除本项目。如果用户继续使用本项目，则视为您接受本协议的变动。




