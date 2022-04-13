# FRAM文档

[toc]

## 1、前言

### 1.1软件部分：

- `face_recognition_opt`（`c++`编写的人脸识别算法部分，基于中科院计算机所开源的`seetaface6`人脸识别算法的基础上实现，`jetsn nano`环境的性能调优及`python<基于pybin11>的库warp`）

- `FRAME`:人脸识别打卡机前端，包括`arm`版本`pyqt5`界面+`face_recohintion_opt`后端生成的`python.so`文件，在`arm ubuntu18.04`上进行部署，并且包含一套后台管理系统，基于`fastapi+html`原生`js`的接口和界面开发。

### 1.2硬件部分:

 硬件采用`NVIDIA jetson nano 4G`进行软件部署，其中，`jetson nano`是英伟达设计制造的人工智能边缘终端，配备`tagrex1` 芯片，集成128核`Maxwell`核心，具备37`GFOPS`算力，其成本低廉（芯片涨价前`2G`版`400`元人民币，`4G`版`800RMB`），对于人脸识别等深度学习算法具有较好的适用性，及较高的性价比。

- `CPU：Tagrex1` 四核`A53+128`核`Maxwell GPU`核心
- 内存：`4G`（显存共用）
- 峰值功耗：`15w`
- 硬盘：金士顿`TF`卡 `64G C10`

### 1.3算法相关

人脸识别算法其中配套有，人脸检测，人脸对比，人脸核验，人脸跟踪，性别识别，年龄识别，人脸质量检测等等内容，其设计的面比较广泛，但是其中算法比较单纯，重在优化检测识别的速度和准确度。

除了中科大`seetaface6`，还有包括虹软人脸识别`SDK`（基于`arcface`的商业化模型），开源`facenet`，`insightface`、基于`dlib`的`face_recognition`库等等人脸识别方案。对于人脸检测有`MTNN`、 `blazeface`、`RetinaFace`、`FaceBox`，等等多种算法，其重点是如何应用、调优与集成。其中各深度算法依赖于特定的推来引擎，不同的推理引擎具有不同的集成方式、跨平台能力、性能和部署差异，比如使用`tnn`进行人脸检测推来，但是使用`mnn`进行人脸识别，不同的模型以及推理引擎相互串联，必定会导致部署难度增加、性能低下、优化困难。在选取`SOTA`模型的同时，一定要注重其算法生态。

**一句话：你不一定需要非常清楚模型为什么要怎么搭建，模型组件的做能有什么优势，但是你一定要明白，这个模型怎么部署，调整方向、调优方法。因为产业化落地是大多数企业的重头戏，而不仅仅是去发表成堆的学术论文将落地架空(比如为了精度采用超级繁琐的数据集，庞大的算法等等），当然，想要去做优化，选型，优化、部署，对推理引擎等有较深的理解是前提，知其然不知其所以然走不长远)**。

## 2、人脸识别核心

### 2.1组件和库构成

- `opencv-4.5.2` 开源计算机视觉库，集成图像的基础处理，如图像编解码、图像读取、裁剪、缩放、甚至深度学习，详情请参考[opencv-home](https://opencv.org/) 、[opencv-github](https://github.com/opencv/opencv)。
- `seetaface6` 人脸势识别算法核心由中科院计算机所开源 ，集成tennis推理引擎，具体请参考[seetaface6](https://blog.csdn.net/xiaonannanxn/article/details/52556278)。
- `freetype-2.11.0`：`FreeType`库是一个完全免费（开源）的、高质量的且可移植的字体引擎，它提供统一的接口来访问多种字体格式，对于`opencv`的扩充，`opencv`在图像中绘制文字仅支持`ASCII`，不支持中文，阿拉伯文，特殊字符等其它文字，因此人脸识别，框选人脸后再框上标注中名字就采用该库
- `harfbuzz-4.0.0`：`HarfBuzz`是一个文本塑造库。使用 `HarfBuzz` 库，程序可以将 Unicode 输入序列转换为格式正确且定位正确的字形输出 — 适用于任何书写系统和语言。详情参考[harfbuzz](https://github.com/harfbuzz/harfbuzz)， [harfbuzz.github.io](https://harfbuzz.github.io/)
- `jsoncpp-1.9.5`:`c++`的`json`解析库，详情参考[jsoncpp](https://github.com/open-source-parsers/jsoncpp)
- `spdlog-1.9.2`：`c++`的日志库，详情参考[spdlog](https://github.com/gabime/spdlog)
- `OMP`：`c++`并行库，c++底层基础库，用于多线程并行计算
- `pybind11`：`c++`的`python`绑定库，详情参考[pybind11](https://github.com/pybind/pybind11)
- `fastapi`：用于`python` `web`服务部署

### 2.2基础流程及优化方案

#### 2.2.1人脸识别基础流程

- 人脸检测（在人脸打卡机上对人脸的定位/框选）
- 人脸关键点检测（五点检测，左眼-右眼-鼻子-左嘴角-右嘴角，人脸`align`及特征提取之用）
- 人脸识别（通过人两人连训练的特征提取器，一般为`resnet50`，`mobilenetv3`等模型，然后根据特征距离<`arcface`采用球面距离，`seetaface`采用余弦距离>计算得分，设定特征距离阈值得到符合条件的特征）。

#### 2.2.2优化方案

##### 2.2.2.1 底层优化

- `cuda`加速优化：`seetaface6`中集成的`tennis`推理引擎支持`cuda`加速计算，`jetson nano`支持`cuda`的加速计算，因此可以进行源码编译加上`cuda`的优化
- `neno`加速：`NEON` 技术是 `ARM Cortex™-A` 系列处理器的 128 位`SIMD`（单指令，多数据）架构扩展，旨在为消费性多媒体应用程序提供灵活、强大的加速功能，从而显著改善用户体验。它具有 32 个寄存器，64 位宽（双倍视图为 16 个寄存器，128 位宽。）
  目前主流的`arm`芯片`ARM NEON`加速，因此在编写移动端算法时，可利用`NEON`技术进行算法加速，以长度为4的寄存器大小为例，相应的提速倍数约是原始的4倍。在推tennis理引擎的编译过程中，打开`neno`加速计算开关。

##### 2.2.2.2 应用优化

- 算法优化

  人脸跟踪优化方案：减小搜索深度，将画面中较小的人脸排除在外。在人脸检测过程中，算法啊会不断搜索画面中的人脸，但是可以约束其搜索深度。比如原始画面为300*300大小，可以通过`anchor`去拟合人脸区域，其中`anchor`可以有多个尺度，比如三个尺度，`(40x40),(80x80),(160x160)`,那么模型将进行三个尺度的搜索，如果限值搜索尺度最小为80，那么只需要搜索`（80x80）（160x160）`两个尺度，当然这只是一个直观的感觉，具体情况可参考常规的对象检测（`objectdetection`算法说明），可以查看经典的[yolov3](https://blog.csdn.net/wq_0708/article/details/120824980)模型原理。其源码示例如下：

  ```c++
  //人脸跟踪需要指定跟踪狂大小，2、3参数
  FT = std::make_shared<FaceTracker>(ft_setting, tracker_rect[0], tracker_rect[1]);
  // 设置最小人脸尺度，具体根据业务调整
  FT->SetMinFaceSize(160);
  ```

  模型优化：前面描述对于人脸特征提取，可以采用重量级的`resnet50`作为特征提取网络，也可以使用`mobilenetv3`等等轻量级的网络做特征提取，其对应网络结构，及如何优化加速可自行查找相关资料。更换特征提取网络能有效的进行模型加速，当然其精度也会些许降低，具体应用权衡请结合实际场景使用。

  ```C++
  ModelSetting ft_setting;
  // face_detector.csta模型问重量型模型，精度该，可选face_detector_light.csta 轻量莫兴国
  ft_setting.append(model_base_dir + "face_detector.csta");
  ft_setting.set_device(device);
  // morden c++ 智能指针包裹裸指针 
  FR = std::make_shared<FaceRecognizer>(fr_setting);
  ```

  流程优化：人脸识别流程见[人脸识别流程](#### 2.2.1)，其中最耗时耗性能的是人脸识别过程，人脸识别过程中需要将目标人脸特征与库中人脸进行逐一对比，但是，为了提升画面的流畅性，可以考虑跳帧识别。此外，在识别过程中存在单个人长时间在画面中的情况，当人脸跟踪相同的人在画面中时，进行识别优化。优化策略目前采用的是，当同一个人脸在画面中时通过`ignore_nums`控制，代码如下：

  ```python
  # 初始化的时候
  def __init__(self, camera_index: int = 0,
  				...
               	record_freq=20,
               	# 忽视40帧进行一次识别，如果机器性能较高，每秒达到20帧，那么两秒钟重新进行一次识别计算
                  ignore_nums: int = 40,
                	# 1min记录一次，如果嫌频率太低，可以降低单位
         			self._record_time = 60
  				...
  # 人脸id改变或者ignore_nums达到指定的数量后进行识别
   if face_id != self._last_id or self._frame_nums == self._ignore_nums:
  ```

  并行库优化，通过`openmp`进行并行优化，`c++`底层采用并行循环的方式进行加速，其代码实现如下：

  ```c++
  // 用宏开启并行优化
  #pragma omp parallel num_threads(m_thread_nums)
  for (int64_t index = 0; index < m_face_dbs.size(); ++index) {
      auto &face_lb_info = m_face_dbs[index];
      float current_sim = FR->CalculateSimilarity(feature.get(), face_lb_info.feature.get());
      if (current_sim > max_sim) {
          max_sim = current_sim;
          target_index = index;
      }
  }
  ```

- 应用优化

  人脸识别打卡机内部采用多任务机制，比如显示线程，计算线程，打卡结果写入线程独立，但是来一张人脸就进行一次数据库写入操作必定会导致数据库堵塞以及计算资源的紧张，可以将已经打卡的人脸信息，放入列表中进行缓存，当达到一定条件后进行集中批量写入，其实现具体如下：

  ```python
  # 达到一定条件后开启线程进行记录的写入
  def condition_send_attend_signal(self):
      # self._records中记录的数量达到指定的数量或者超过一定的时间后进行数据写入
      # 当初可能存在的bug是，没加入时间约束，最后一个人打完卡后很可能一直存在缓存中未持久化到数据库
      if self._record_nums == self._record_freq or time.time() - self._record_last_time > self._record_time:
          if len(self._records) != 0:
              self.record_attend_signal.emit(self._records)
              self._record_nums = 0
              self._records = []
              self._record_last_time = time.time()
  ```

- 硬解优化

  摄像头画面读取采用硬件解码的方式，画面更流程，cpu占用更少

  ```python
   @staticmethod
   def gstreamer_pipeline(capture_width, capture_height, display_width, display_height, framerate, flip_method):
   	return "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)" + str(capture_width) + ", height=(int)" + \
      str(capture_height) + ", format=(string)NV12, framerate=(fraction)" + str(framerate) + \
      "/1 ! nvvidconv flip-method=" + str(flip_method) + " ! video/x-raw, width=(int)" + \
      str(display_width) + ", height=(int)" + str(
          display_height) + ", format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
  ```

  

- 其它优化

  底层应用采用`c++`编写，并进行高度封装，避免在`python`代码中大量使用`for`循环，在兼具底层高效的同时，使应用速度最大化。其它可能存在的优化部分未一一列出，具体体可参见源码文件（代码不多）

## 3 人脸识别jetson nano 部署

1. 根据硬件版本下载镜像文件

```bash
# 注意：jetsonnano 4G版本与2G版本镜像有些许差异，比如资源调度等等，混用可能存在一定的问题
https://developer.nvidia.com/embedded/jetpack-archive
```

2. 格式化SD卡（可选）

```bash
# 使用 SD 协会的 SD Memory Card Formatter 格式化 microSD 卡
```

3. 使用[Etcher](https://www.balena.io/etcher/) 将 `Jetson Nano` 开发者套件 `SD` 卡镜像写入 `microSD` 卡；
4. 首次启动连接显示器、键盘和鼠标，用户设置

```bash
# 参考 https://www.myfreax.com/how-to-add-and-delete-users-on-debian-9/
# --1要使用adduser命令创建一个名为username的新用户帐户，请运行：
sudo adduser username
# 如果您希望新创建的用户具有管理权限，请将该用户添加到sudo组：
sudo usermod -aG sudo username
# 如果不再需要该用户帐户，则可以使用userdel或deluser将其删除,通常应该使用deluser命令。
# 要删除用户而不删除用户文件，请运行：
sudo deluser username
# 如果您要删除用户的主目录和邮件后台处理程序，请使用--remove-home标志：
sudo deluser --remove-home username
```

5. 设置交换空间

```bash
sudo fallocate -l 2G /swapfile
# 如果fallocate工具在你的系统上不可用，或者你获得一个消息：fallocate failed: Operation not supported，使用下面的命令去创建交换文件：
sudo dd if=/dev/zero of=/swapfile bs=1024 count=2097152
# 1.2、设置文件权限到600阻止常规用户读写这个文件：
sudo chmod 600 /swapfile
# 1.3、在这个文件上创建一个 Linux 交换区：
sudo mkswap /swapfile
# 输出如下：
# Setting up swapspace version 1, size = 2 GiB (2147479552 bytes)
# no label, UUID=fde7d2c8-06ea-400a-9027-fd731d8ab4c8
# 1.4、通过运行下面的命令，激活交换区：
sudo swapon /swapfile
# 想要持久化，打开/etc/fstab文件：
sudo nano /etc/fstab
并且粘贴下面的行：
/swapfile swap swap defaults 0 0
# 调整 Swappiness 值
cat /proc/sys/vm/swappiness
# 输出如下：
60
# Swappiness 为 60 适合大部分 Linux操作系统，对于生产服务器，你需要将这个值设置成更低。
# 将 Swappiness 值修改成 10，运行：
sudo sysctl vm.swappiness=10
# 想要将这个参数持久化，在重启时仍然起作用，将下面的内容附加到/etc/sysctl.conf文件：
vm.swappiness=10
# 移除一个交换文件
# 01.首先，取消激活交换空间：
sudo swapoff -v /swapfile
# 02.从/etc/fstab文件中移除交换文件条目/swapfile swap swap defaults 0 0。
# 03.使用rm命令删除实际的交换区文件：
sudo rm /swapfile
```

5. 更新源和软件

```bash
sudo apt-get update
sudo apt-get upgrade
```

6. pip安装及更新，设置国内源

```bash
# 安装pip
sudo apt-get install python3-pip python3-dev -y
# 更新pip
sudo python3 -m pip install --upgrade pip
# 设置国内源
# 创建文件`~/.pip/pip.conf`(`windows` 为 `Users/xx/.pip/pip.ini`),文件中编写如下内容
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host=mirrors.aliyun.com
```

7. 设置分辨率（可选）

```bash
# 参考 https://blog.csdn.net/dream_allday/article/details/77896194
xrandr # 查看支持的分辨率
# 设置分辨率
xrandr -s 1024×768
# 修改屏幕显示方向
xrandr -o left # 向左旋转90度
xrandr -o right # 向右旋转90度
xrandr -o inverted # 上下翻转
xrandr -o normal # 回到正常角度
# 永久保存屏幕显示方向：
# 终端输入
sudo gedit  /etc/X11/Xsession.d/55gnome-session_gnomerc      
# 在打开的文件末端添加
xrandr --output Virtual1 --rotate left
```

8. python库安装

```bash
# 日志库安装
pip install loguru
# 串口库安装
pip install pyserial
# 界面库安装(注意安装时会进行源码编译，所以安装较慢并且pip版本需要较高>20.3)
pip install pyqt5 或者 sudo apt-get install python3-pyqt5
# fastapi安装（如果编译ujson报错，请升级pip）
pip install fastapi[all]
```

9. 锁屏设置‘从不’，锁定‘关闭’

10. 环境变量设置

```bash
sudo vim ~/.bashrc
# 添加以下内容：指定链接库
LD_LIBRARY_PATH=/home/yw/Desktop/face_recognitin_opt_back/build/jetsonface:$LD_LIBRARY_PATH
```

11. 设置执行sudo免密码

```bash
sudo vim /etc/sudoers
# 文件最后加入 
yourusername ALL=(ALL) NOPASSWD : ALL
```

12. 添加开机，进程管理等等

```bash
# 1、安装
sudo apt-get install supervisor(python3 -m pip install supervisor)
# 2、安装完后主要有以下命令模块
supervisord #这个是supervisor服务的主要管理器，负责管理我们配置的子进程，包括重启崩溃或异常退出的子进程，同时也响应来自客户端的请求。
supervisorctl:#supervisord服务的客户端命令行。听过这个，我们可以获得由主进程控制的子进程的状态，停止和启动子进程，并获得主进程的运行列表。
Web Server：#和supervisorctl功能娉美。这个是通过web界面查看和控制进程状态。
XML-RPC Interface：#服务于web UI的同一个HTTP服务器提供一个XML-RPC接口，可以用来询问和控制管理程序及其运行的程序
# 3、生成配置文件
echo_supervisord_conf > /etc/supervisor/supervisord.conf
# 4、修改配置文件其中两部分最重要开启web管理界面，执行子进行程序
# 4.1、解开以下部分注释（;）设置好ip，端口，用户名和密码
...
[inet_http_server]         ; inet (TCP) server disabled by default
port=127.0.0.1:9018        ; ip_address:port specifier, *:port for all iface
username=aichao              ; default is no username (open server)
password=1234               ; default is no password (open server)
...
# 4.2、子进程配置文件将所有目录下的ini文件全部添加进去
[include]
files = /usr/supervisor/supervisord.d/*.ini

# 5、子进程配置文档编写
[program:backend]
stopasgroup=true
#supervisor启动的时候是否随着同时启动，默认True
autostart=true
user=aichao #用户
# 环境变量，同一个环境变量用(:)分隔，不同的环境变量请用，分割使用方式如下
environment=PYTHONPATH="/home/aichao/.local/lib/python3.8/site-packages",LD_LIBRARY_PATH="/home/aichao/index/build/lib/aarch64"
# 执行文件目录
directory=/home/aichao
# 执行命令
command=python3 test.py
#这个选项是子进程启动多少秒之后，此时状态如果是running，则我们认为启动成功了。默认值为1
startsecs=1
#把stderr重定向到stdout，默认 false
redirect_stderr=true
# 日志输出
stdout_logfile=/home/aichao/out.log
stderr_logfile=/home/aichao/out.err
#stdout日志文件大小，默认 50MB
#stdout_logfile_maxbytes = 20MB
#stdout日志文件备份数可以走默认
#stdout_logfile_backups = 20

# 6、启动supervisor
supervisor -c /etc/supervisor/supervisord.conf
# 7、常用命令
supervisorctl status        //查看所有进程的状态
supervisorctl stop es       //停止es
supervisorctl start es      //启动es
supervisorctl restart       //重启es
supervisorctl update        //配置文件修改后使用该命令加载新的配置
supervisorctl reload        //重新启动配置中的所有程序
# 8、开机自启动1
# 8.1、在目录/usr/lib/systemd/system/ 新建文件supervisord.service,并添加配置内容
[Unit]
Description=Process Monitoring and Control Daemon
After=rc-local.service nss-user-lookup.target

[Service]
Type=forking
# 这个相当之重要，不然执行东西没有root权限就很傻
User=root 
ExecStart=/usr/bin/supervisord -c /usr/supervisor/supervisord.conf ;开机启动时执行
ExecStop=/usr/bin/supervisord shutdown
ExecReload=/usr/bin/supervisord reload
killMode=process
Restart=on-failure
RestartSec=42s

[Install]
WantedBy=multi-user.target
# 8.2、启动服务：
systemctl enable supervisord
# 8.3、验证是否开机启动：
systemctl is-enabled supervisord
# 开机自启动2
# supervisor挂掉不属于我们的处理范畴，我们想要的就是supervisor可以在开机时自动启动，监管并启动我们想要的进程
# 执行命令
sudo vim /etc/rc.local
# 将下面这句话添加文件rc.local中exit 0一行的前面
/usr/bin/python3 /usr/bin/supervisord -c /usr/supervisor/supervisord.conf
# 修改执行权限
sudo chmod +x /etc/rc.local
# enjoy ----其它简单的开机自启也可以搞
```
