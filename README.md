# FRAM文档

[toc]

## 1、概述

### 1.1 研发背景

在赛摩博晟产品研发战略方针指导下，探索事实可行的软硬结合的产品，在提升企业影响力的同时开辟一条新的企业盈利途径。其研发要求我总结大体为：

- 1.成本低

当前公司的总体技术栈为：后端.net core（EFweb框架）.netframe/cs框架，前端angular.js框架。其部署硬件及操作系统主要为：x86平台/windows操作系统，但是缺点显而易见：工业级x86平台成本极高，功耗大对配套（供电、散热）要求高，不易实现边缘端部署，正版windows操作系统较为昂贵。因此，以当前技术栈做边缘端软硬结合的产品，其市场竞争力较低，且存在拼凑嫌疑（无法体现自身的设计能力及集成能力）。因为需要摆脱当前公司定性思维。

- 生态优

目前除了x86平台外，另一个主流平台为arm平台，由于cpu授权问题，x86严重依托于国外的芯片（仅仅intel和AMD,国内兆芯等等成本高，技术水平低），但是国内arm平台呈现出一片欣欣向荣的景象，华为鲲鹏、阿里倚天、瑞芯微RK等等，其国产化在稳步推进，后期发展迅猛，风头正盛。目前arm平台其主推操作系统为linux与Android，均可使用商业免费版本，但其存在使用（运维）难度较大、软件生态相对匮乏（但Android生态及其丰富）等等缺点。

- 应用广

对于软硬结合的产品一定能够解决一定用户痛点，并且该问题涉及广泛，遍及于各行各业。

- 定制强

市面上必定存在竞品，但是需要做出与竞争力，个性化的产品，大厂不愿投入的我们可以去做。

- 噱头足

产品一定要具备一定要以技术为导向，把我技术驱动型的技术风向，尽可能高大上，具备较强的议价能力。

### 1.2 研发方向

综合以上问题，经过公司内部讨论，结合市场主流平台及方案以及公司当前人员配备现状，决定考虑采用arm平台的硬件，以视觉方向，对AI视觉终端进行尝试性研发。目前已经存在的使用场景是火车车号皮重抓拍识别，通过外部输入与抓拍相机联动实现图像抓拍，结合定制化的算法对火车车厢上的车号与皮重数据进行识别，目前由于疫情施工等原因停滞。但其应用也开辟了新的认知，及研发方向，主要包含

- 人脸识别门禁

当然在头脑风暴的同时，也有提到公司门禁机打卡系统问题。目前门禁采用工牌刷卡的方式，但是依旧存在诸多的不便，比如忘记带工牌，工牌被滥用等等，因此考虑生人脸识别的方式实现门禁系统的控制。

- 人脸识别打卡机

当前人脸识别打卡机无法实时同步打卡信息，导致某些同事由于种种原因没打上卡，但是在系统中又无法查看打卡信息，导致无法补卡。因此该问题经常被诟病。自己开发一款可控的，可个性化定制的人脸识别打卡机被提上日程。

**在功能上，人脸识别门禁是人脸识别打卡机的子集，因为可以直接上人脸识别打卡机，一步到位。**

- 拓展应用

人脸识别，人脸打卡等公司内部级别的使用不是目的。对于火电厂，化工等工厂等安全生产的需求，可以考虑安全行为识别：安全帽、反光背心等穿戴识别，翻越，闯入识别，人员摔倒、追逐等识别；设备状态识别：机械开关状态，大门开关状态，设备倾倒状态；质量检测：裂纹、气泡、数量、大小等检测。

### 1.2 系统构成

#### 1.2.1 硬件

-  计算核心

主体硬件采用`NVIDIA jetson nano 4G`进行软件部署，其中，`jetson nano`是英伟达设计制造的人工智能边缘终端，配备`tagrex1` 芯片，集成128核`Maxwell`核心，具备37`GFOPS`算力，其成本低廉（芯片涨价前`2G`版`400`元人民币，`4G`版`800RMB`），对于人脸识别等深度学习算法具有较好的适用性，及较高的性价比。

|   项目   | 参数                                                         |
| :------: | :----------------------------------------------------------- |
|   CPU    | `Tagrex1` aarm四核A57多核处理器                              |
|   GPU    | 128核`NVIDIA Maxwell GPU`核心                                |
|   内存   | `4G`LPDDR4（显存共用）                                       |
|   硬盘   | 金士顿`TF`卡 `64G C10`                                       |
|   I/O    | USB3.0 typeAx1、USB2.0 TypeAx2、<br> USB 2.0 model B、HDMI、<br>Gigabit Ethernet、MIPI屏幕/CSI摄像头接口，<br>40pin扩展口[UART、SPI、I2S、I2C、GPIO] |
| 峰值功耗 | 15w                                                          |
| 输入电源 | 5v/3A                                                        |

- 摄像头

摄像头采用CSI接口摄像头，最高支持800w像素，可以通过NVIDIA实现硬件解码，画面更加流畅，CPU占用更低

| 项目       | 参数                                       |
| ---------- | ------------------------------------------ |
| 感光芯片   | 索尼IMX219                                 |
| 接口类型   | CSI                                        |
| 像素       | 800w（最高支持3280x2464，最低支持640x480） |
| 光圈       | 2.0                                        |
| 焦距       | 2.96mm                                     |
| 对角视场角 | 77°                                        |

- TOF距离传感器

| 项目     | 参数             |
| -------- | ---------------- |
| 型号     | TOF200F          |
| 测量距离 | 2M（max）        |
| 测量盲区 | 0-3cm            |
| 波长     | 940nm            |
| 工作电压 | 3.5-5v/40ma(max) |

- 屏幕

| 项目               | 参数                           |
| ------------------ | ------------------------------ |
| 屏幕大小           | 3.5寸LCD                       |
| 分辨率             | 480x320                        |
| 显示接口:          | HDMI                           |
| 触摸接口           | GPIO                           |
| 外形尺寸: 工作电压 | 85.5* 60.6(mm)3.5-5v/40ma(max) |

#### 1.2.2 软件

- `face_recognition_opt`（`c++`编写的人脸识别算法部分，基于中科院计算机所开源的`seetaface6`人脸识别算法的基础上实现，`jetsn nano`环境的性能调优及`python<基于pybin11>的库warp`），程序编译完成后生成so动态库。
- `FRAME`:人脸识别打卡机前端，包括`arm`版`pyqt5`界面，基于fastapi+html的后台管理系统。

####  1.2.3 算法

人脸识别算法其中配套有，人脸检测，人脸对比，人脸核验，人脸跟踪，性别识别，年龄识别，人脸质量检测等等内容，其设计的面比较广泛，但是其中算法比较单纯，重在优化检测识别的速度和准确度。

除了中科大`seetaface6`，还有包括虹软人脸识别`SDK`（基于`arcface`的商业化模型），开源`facenet`，`insightface`、基于`dlib`的`face_recognition`库等等人脸识别方案。对于人脸检测有`MTNN`、 `blazeface`、`RetinaFace`、`FaceBox`，等等多种算法，其重点是如何应用、调优与集成。其中各深度算法依赖于特定的推来引擎，不同的推理引擎具有不同的集成方式、跨平台能力、性能和部署差异，比如使用`tnn`进行人脸检测推来，但是使用`mnn`进行人脸识别，不同的模型以及推理引擎相互串联，必定会导致部署难度增加、性能低下、优化困难。在选取`SOTA`模型的同时，一定要注重其算法生态。

**一句话：你不一定需要非常清楚模型为什么要怎么搭建，模型组件的做能有什么优势，但是你一定要明白，这个模型怎么部署，调整方向、调优方法。因为产业化落地是大多数企业的重头戏，而不仅仅是去发表成堆的学术论文将落地架空(比如为了精度采用超级繁琐的数据集，庞大的算法等等），当然，想要去做优化，选型，优化、部署，对推理引擎等有较深的理解是前提，知其然不知其所以然走不长远)**。

## 2、人脸识别核心

### 2.1 组件和库构成

- `opencv-4.5.2` 开源计算机视觉库，集成图像的基础处理，如图像编解码、图像读取、裁剪、缩放、甚至深度学习，详情请参考[opencv-home](https://opencv.org/) 、[opencv-github](https://github.com/opencv/opencv)。
- `seetaface6` 人脸势识别算法核心由中科院计算机所开源 ，集成tennis推理引擎，具体请参考[seetaface6](https://blog.csdn.net/xiaonannanxn/article/details/52556278)。
- `freetype-2.11.0`：`FreeType`库是一个完全免费（开源）的、高质量的且可移植的字体引擎，它提供统一的接口来访问多种字体格式，对于`opencv`的扩充，`opencv`在图像中绘制文字仅支持`ASCII`，不支持中文，阿拉伯文，特殊字符等其它文字，因此人脸识别，框选人脸后再框上标注中名字就采用该库
- `harfbuzz-4.0.0`：`HarfBuzz`是一个文本塑造库。使用 `HarfBuzz` 库，程序可以将 Unicode 输入序列转换为格式正确且定位正确的字形输出 — 适用于任何书写系统和语言。详情参考[harfbuzz](https://github.com/harfbuzz/harfbuzz)， [harfbuzz.github.io](https://harfbuzz.github.io/)
- `jsoncpp-1.9.5`:`c++`的`json`解析库，详情参考[jsoncpp](https://github.com/open-source-parsers/jsoncpp)
- `spdlog-1.9.2`：`c++`的日志库，详情参考[spdlog](https://github.com/gabime/spdlog)
- `OMP`：`c++`并行库，c++底层基础库，用于多线程并行计算
- `pybind11`：`c++`的`python`绑定库，详情参考[pybind11](https://github.com/pybind/pybind11)
- `fastapi`：用于`python` `web`服务部署

### 2.2人脸识别基础流程

- 人脸检测（在人脸打卡机上对人脸的定位/框选）
- 人脸关键点检测（五点检测，左眼-右眼-鼻子-左嘴角-右嘴角，人脸`align`及特征提取之用）
- 人脸识别（通过人两人连训练的特征提取器，一般为`resnet50`，`mobilenetv3`等模型，然后根据特征距离<`arcface`采用球面距离，`seetaface`采用余弦距离>计算得分，设定特征距离阈值得到符合条件的特征）。

### 2.3优化方案

#### 2.3.1 底层优化

- `cuda`加速优化：`seetaface6`中集成的`tennis`推理引擎支持`cuda`加速计算，`jetson nano`支持`cuda`的加速计算，因此可以进行源码编译加上`cuda`的优化
- `neno`加速：`NEON` 技术是 `ARM Cortex™-A` 系列处理器的 128 位`SIMD`（单指令，多数据）架构扩展，旨在为消费性多媒体应用程序提供灵活、强大的加速功能，从而显著改善用户体验。它具有 32 个寄存器，64 位宽（双倍视图为 16 个寄存器，128 位宽。）
  目前主流的`arm`芯片`ARM NEON`加速，因此在编写移动端算法时，可利用`NEON`技术进行算法加速，以长度为4的寄存器大小为例，相应的提速倍数约是原始的4倍。在推tennis理引擎的编译过程中，打开`neno`加速计算开关。

#### 2.3.2算法优化

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
// face_detector.csta模型问重量型模型，精度该，可选face_detector_light.csta 轻量模型
ft_setting.append(model_base_dir + "face_detector.csta");
ft_setting.set_device(device);
// morden c++ 智能指针包裹裸指针 
FR = std::make_shared<FaceRecognizer>(fr_setting);
```

流程优化：其中最耗时耗性能的是人脸识别过程，人脸识别过程中需要将目标人脸特征与库中人脸进行逐一对比，但是，为了提升画面的流畅性，可以考虑跳帧识别。此外，在识别过程中存在单个人长时间在画面中的情况，当人脸跟踪相同的人在画面中时，进行识别优化。优化策略目前采用的是，当同一个人脸在画面中时通过`ignore_nums`控制，代码如下：

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

#### 2.3.3算法优化

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

#### 2.3.4解码优化

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

#### 2.3.5其它优化

底层应用采用`c++`编写，并进行高度封装，避免在`python`代码中大量使用`for`循环，在兼具底层高效的同时，使应用速度最大化。其它可能存在的优化部分未一一列出，具体体可参见源码文件（代码不多）

## 3 人脸识别jetson nano 部署

### 3.1 系统安装

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

### 3.2 创建用户

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

### 3.3 基础设置

- 设置交换空间

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

- 更新源和软件

```bash
sudo apt-get update
sudo apt-get upgrade
```

- pip安装及更新，设置国内源

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

- 设置分辨率（可选）

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

- python库安装

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

- 锁屏设置‘从不’，锁定‘关闭’

- 环境变量设置

```bash
sudo vim ~/.bashrc
# 添加以下内容：指定链接库
LD_LIBRARY_PATH=/home/yw/Desktop/face_recognitin_opt_back/build/jetsonface:$LD_LIBRARY_PATH
```

- 设置执行sudo免密码

```bash
sudo vim /etc/sudoers
# 文件最后加入 
yourusername ALL=(ALL) NOPASSWD : ALL
```

### 3.4 进程管理及开机自启

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
command=python3 upload_api_test.py
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

## 4 软件更新

### 4.1 C++后端算法更新

调整源码内容后执行以下命令：

```bash
# 假定当前目录${woorkpath}为./jetsonface_recoognition_opt
cd build
cmake ..
make -j4
```

```bash
# 在build目录下会生成一个so动态库，动态库命名为jetson_xxx_xxx_xx.so
# 将so拷贝至FRAM目录，假设./FRAM与./jetsonface_recoognition_opt在同目录下
cp jetson_xxx_xxx_xx.so ../../FRAM/jetsonface/
```

### 4.2 python部分更新

python部分均为源码，直接修改即可

## 5 运行

```bash
# 按照3节配置好开机自弃及进程管理后执行以下命令
# 切换到root用户输入密码4321
su root
# 开启人脸识别打卡界面程序（pyqt5）
supervisordctl start attend
# 开启后台web服务，提供接口和访问界面
supervisordctl start bakend
# -----------------------------------------------------------
# 也可以执行停止、重启将start改为stop/restart
# 查看运行日志，其中成本本身有运行日志，但是supervisor提供日志勾子，捕获日志
# 日志存放目录
cat /usr/supervisor/supervisor.d/logs/attend(backend)/out.log
```

## 附录

### 接口文档

- 添加人脸

添加人脸照片，其中照片按照5:7的宽高比例，大小不超过300k，并且**必须以"工号\_姓名.jpg"方式命名，例如：HR0878\_艾超.jpg**，因为模型使用opencv库进行图片的加载，opencv库是不支持文件中文命名的，并且皆苦会将图像进行预处理，重命名等操作。

| 项目         | 说明                             |
| ------------ | -------------------------------- |
| 接口名称     | http://ip:port/api/add_face_libs |
| 请求方式     | put                              |
| content-Type | multipart/form-data              |
| 请求体       | 文件对象数组，字段files          |
| 返回         | 每个文件上传那结果               |

- 获取人脸库信息

该接口可以返回所有在人脸库中的信息，包括姓名，工号，人脸注册时间信息。

| 项目         | 说明                                               |
| ------------ | -------------------------------------------------- |
| 接口名称     | http://ip:port/api/get_face_libraries              |
| 请求方式     | get                                                |
| content-Type |                                                    |
| 请求体       |                                                    |
| 返回         | json列表[{name:xx,staff_id:xx,update_time:xx},...] |

- 删除人脸

| 项目         | 说明                           |
| ------------ | ------------------------------ |
| 接口名称     | http://ip:port/api/delete_face |
| 请求方式     | delete                         |
| content-Type | application/json               |
| 请求体       | {"face_d":"xxx"}               |
| 返回         | 成功或失败                     |

- 获取打卡流水

获取指定时间段内的打卡流水（非去重）

| 项目         | 说明                                                         |
| ------------ | ------------------------------------------------------------ |
| 接口名称     | http://ip:port/api/get_attend_nfos                           |
| 请求方式     | post                                                         |
| content-Type | application/json                                             |
| 请求体       | {"start_tme":"xxx","end_time":"xxx"}                         |
| 返回         | 成功返回打卡流水[{"name":"xx","staff_d":"xx","attend_time":"xx"},...{...}] |

- 下载人脸库

指定员工id下载人脸照片

| 项目         | 说明                                |
| ------------ | ----------------------------------- |
| 接口名称     | http://ip:port/api/download_facelib |
| 请求方式     | get                                 |
| content-Type |                                     |
| 查询参数     | ?staff_id="HR0878"                  |
| 返回         | 成功下载人脸图片                    |

- 清除数据

外部定期任务删除打卡流水之用，按照时间段进行删除

| 项目         | 说明                          |
| ------------ | ----------------------------- |
| 接口名称     | http://ip:port/api/clear_data |
| 请求方式     | get                           |
| content-Type |                               |
| 查询参数     | ?start_time=xx&endtime=xx     |
| 返回         | 成功或失败                    |

- 更新系统时间

| 项目         | 说明                                            |
| ------------ | ----------------------------------------------- |
| 接口名称     | http://ip:port/api/update_sys_time              |
| 请求方式     | put                                             |
| content-Type | application/json                                |
| 请求体       | {  "date": "2022-04-18",   "time": "15:56:00" } |
| 返回         | 成功或失败                                      |

- 其它接口废弃或接口测试请访问一下地址：

```http
# 按照swagger-ui接口文档提示使用
http://ip:port/docs
```

