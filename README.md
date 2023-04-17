# Label Video (LabelV) tools
视频标注工具，包含两个功能
- 视频类别标注 (LabelV-CLS)
- 视频时空标注 (LabelV-STL)
  
![](https://github.com/lllcho/LabelV/raw/main/images/demo.gif)
## 安装
要求Python 3.x环境，安装依赖项：
``` shell
pip install -r requirements.txt
```

## 1. 视频类别标注 (LabelV-CLS)
对每个视频标注一个类别标签，可用于视频筛选或分类

### 1.1 数据准备
* Tips：
    > 为了方便视频标注和模型训练，建议提前将所有视频先处理成不超过20秒的短视频，一般10秒比较合适

1. 将待标注视频放在同一个文件夹下，视频需要编码为html5 \<video\>标签所支持的视频编码格式：MP4、WebM、Ogg。
2. (本步骤可省略)生成待标注视频的文件名列表文件 `xxxxx.txt`, 文件内容类似如下：
```
path
video1/a.mp4
video1/b.mp4
video/c.mp4
```
### 1.2 修改配置参数
如果上述第2步省略，则配置文件`configs/example_cls.yaml`中`video_list=''`,此时将自动获取`video_dir`中的视频文件用于标注，否则`video_list='/path/to/xxxxx.txt'`需要完整文件路径。\
根据自己的数据修改配置文件中的其它参数，参数配置完成后运行服务启动命令：
```shell
python labelv_cls.py configs/example_cls.yaml
```
浏览器打开标注URL进行标注: http://0.0.0.0:port/task_name, 远程标注时，将IP替换为服务器的真实IP, port和task_name见配置文件
![](https://github.com/lllcho/LabelV/raw/main/images/cls_ui.jpg)


## 2. 视频时空标注(LabelV-STL)
标注视频中某一事件或行为动作发生的时空位置，包括起始时刻点和每个时刻在视频中的空间位置。
### 2.1 数据准备
* Tips：
    > 为了方便视频标注和模型训练，建议提前将所有视频先处理成不超过20秒的短视频，一般10秒比较合适

1. 将待标注视频放在同一个文件夹下，视频需要编码为html5 \<video\>标签所支持的视频编码格式：MP4、WebM、Ogg。
2. (本步骤可省略)生成待标注视频的文件名列表文件 `xxxxx.txt`, 文件内容类似如下：
```
path
video1/a.mp4
video1/b.mp4
video/c.mp4
```
从第二行开始，每行包含一个相对路径，`video_dir`和该相对路径组成视频的完整路径。
### 2.2 修改配置参数
如果上述第2步省略，则配置文件`configs/example_stl.yaml`中`video_list=''`,此时系统自动获取`video_dir`中的视频文件用于标注， 否则:
 + 填入生成的`/path/to/xxxxx.txt`文件完整路径
 + 直接使用视频类别标注 (LabelV-CLS)生成的csv文件(`configs/example_cls.yaml`中`label_file`变量的值)作为video_list，此时，所有label_id=1的视频将用于标注
根据自己的数据修改配置文件中的其它参数，参数配置完成后运行服务启动命令：

```shell
python labelv_stl.py configs/example_stl.yaml
```
![](https://github.com/lllcho/LabelV/raw/main/images/stl_ui.jpg)

### 2.3 标注说明
- 刷新网页可暂时跳过该视频
- 标注完一个动作后，点击保存，暂存该动作的标注数据；然后重新设定起始帧继续标定下一个动作并保存；直到该视频所有动作并标注完成后点击提交结果
- 系统根据起始结束帧和关键帧间隔自动计算待标注的关键帧，每个关键帧单击后自动变为绿色，表示这个关键帧的框被已被正确标注，双击可取消。首尾关键帧必须被标注为绿色，未标注为绿色的其它帧将根据绿色帧自动插值计算框（差值框用红色显示）。仅标记为绿色的关键帧的框才会被保存。
  
### 2.4 标注结果可视化
验证是否已经安装 ffmpeg, 终端输入命令: `ffmpeg` . 
如果没有安装需要先安装, Anaconda环境下安装命令：`conda install ffmpeg`

修改 `video_visual.py` 中参数：
- `video_dir`: 视频数据所在目录，意义同配置文件中的 `video_dir`参数
- `output_dir`: 可视化标注结果后数据视频的目录
- `label_file`: 标注文件路径，意义同配置文件中的 `label_file` 参数

然后文件路径后运行命令：
``` shell
python video_visual.py
```
浏览器打开URL: http://0.0.0.0:port/task_name 进行标注。
下面是两个视频的标注结果：
```json
[
    {
        "scale": 0.5,
        "name": "coverr-man-and-woman-talking-after-a-tennis-match-1142-1080p.mp4",
        "actions": [
            {
                "start": 16,
                "end": 101,
                "label": "喝水",
                "boxes": {
                    "16": [
                        548,
                        67,
                        786,
                        538
                    ],
                    "37": [
                        557,
                        91,
                        786,
                        538
                    ],
                    "59": [
                        552,
                        124,
                        786,
                        538
                    ],
                    "80": [
                        538,
                        149,
                        786,
                        538
                    ],
                    "101": [
                        525,
                        175,
                        786,
                        538
                    ]
                }
            }
        ],
        "time": "2022-11-30 11:41:33"
    },
    {
        "scale": 0.5,
        "name": "coverr-a-guy-surfing-in-the-sea-8809-1080p.mp4",
        "actions": [
            {
                "start": 217,
                "end": 247,
                "label": "跌倒",
                "boxes": {
                    "217": [
                        190,
                        56,
                        374,
                        355
                    ],
                    "232": [
                        300,
                        138,
                        448,
                        361
                    ],
                    "247": [
                        421,
                        132,
                        566,
                        245
                    ]
                }
            }
        ],
        "time": "2022-11-30 11:51:48"
    }
]
```
其中：
+ `scale`: 视频标注时缩放倍数，在原始视频上boxes的真实值是 boxes/scale
+ `name`: 视频文件名
+ `actions`: 对应视频标注出来的动作或者事件
+ `start`: 动作或者事件的起始帧号，帧号/平均帧率可以换算成起始时间
+ `end`: 动作或者事件的结束帧号，帧号/平均帧率可以换算成结束时间
+ `label`: 对应的类别名称
+ `boxes`: 关键帧的bounding box, 以`{帧号: box}`形式保存
+ `time`: 标注提交时间

