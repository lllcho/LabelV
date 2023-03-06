import os
import sys
import copy
import cv2
import yaml
import json
import pandas as pd
import os.path as osp
from datetime import timedelta, datetime
from flask import Flask, request, url_for, redirect, abort, send_from_directory
from wsgiref.simple_server import make_server
app = Flask(__name__)


def make_action_option(actions):
    text = "<option value=""></option>\n"
    for action in actions:
        text = text + f"""         <option value="{action}">{action}</option>\n"""
    return text


def make_html(video_url, total_frame, video_height, video_width,
              fps, labeled, total, name, scale):
    action_option = make_action_option(cfg['class_name'])
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>LabelV-STL</title>
    <style>
        .base{{
            margin: 0 auto;
            width: {max(video_width,960)}px;
        }}
        .div-base {{
            position: relative;
            width: {video_width}px;
            height: {video_height}px;
        }}

        .div0 {{
            position: absolute;
            left: 0px;
            top: 0px;
            z-index: 10;
        }}

        .div1 {{
            position: relative;
            left: 0px;
            top: 0px;
            z-index: 50;
        }}

        .div2 {{
            position: relative;
            white-space: nowrap;
        }}

        .progress_bar {{
            width: 93%;
            vertical-align: middle;
            display: inline-block;
        }}

        .current_frame {{
            display: inline-block;
        }}
    </style>
    
</head>
<div class="base">
<body>
<script src="https://cdn.jsdelivr.net/npm/vue@2.7.13"></script>

<div calss="player">
    <div class="div-base" id="c">
        <div class="div0">
        <video preload="auto" src={video_url} width="{video_width}px" height="{video_height}px" muted="true"></video>
        </div>
        <div class="div1">
            <canvas id="c1" width="{video_width}px" height="{video_height}px"></canvas>
        </div>
        <div class="div2">
            <label><input id="progress_bar" class="progress_bar" type="range" min="0" max="{total_frame-1}" value="0"></label>
            <div class="current_frame" id="current_frame" style="text-align:right">{{{{cur_frame}}}}/{total_frame-1}</div>
        </div>
    </div>
</div>
<br/>
<br/>

<div id="action-label">
    <label>开始帧：<input id="start_frame" type="text" v-model="start" readonly="readonly" style="outline:none;border:none;width: 4em"></label>&nbsp;
    <label>结束帧：<input id="end_frame" type="text" v-model="end" readonly="readonly" style="outline:none;border:none;width: 4em"></label>&nbsp;
    <label>FPS:<input id="fps" value={fps} readonly="readonly" style="outline:none;border:none;width: 4em"></label>&nbsp;
    关键帧间隔(秒):
    <select id="key_frame_interval" v-model="key_frame_interval" v-on:change="calcKeyFrame">
        <option value=0.25>0.25</option>
        <option value=0.5>0.5</option>
        <option value=1>1</option>
        <option value=2>2</option>
        <option value=4>4</option>
    </select>&nbsp;
    类别：
    <select id="action_option" v-model="label">{action_option}</select>&nbsp;
    <button id="save_action_button" type="button" v-on:click="saveLabel">保存</button>&nbsp;&nbsp;
    <form action="/{cfg['task_name']}" method="post" onsubmit="return checkRes()" style="display: inline">
        <input name="labels" id="results" type="hidden" v-model="results()"/>
        <input name="scale" type="hidden" value={scale}>
        <input name="name" type="hidden" value={name}>
        <input type="submit" value="提交结果"/>
    </form>
    <br/>关键帧：
    <key-frame v-for="(box, index) in boxes" :key="box[0]" v-bind:idx="box[0]" v-bind:box="box[1]" v-on:view="moveTo(box[0])"></key-frame>
    <br/>
    <action-labels v-for="(action_label, index) in action_labels" :key="index" v-bind:action_label="action_label" v-on:delete="action_labels.splice(index, 1)"></action-labels>
    
</div>

<div class="status">
    标注进度：{labeled}/{total}
</div>
<script type="text/javascript" src="static/js/action_labeler.js"></script>
<br/>
快捷键：设为起始帧(a)、设为结束帧(d)、前进一帧(f)、后退一帧(b)、播放暂停视频(空格)
<br/>
标注框：按住鼠标左键拖动画框，矩形框4个角按住调整，中心位置可按住移动
<br/>
标注流程：1）设定起始结束帧. 2）调整每个关键帧的框.  3）保存当前标注的行为.  4）回到第一步继续标注下一个行为. 5）当前视频全部被标注完成后提交结果，自动进入下一个视频
</body>
</div>
</html>
"""
    return html


def videoinfo(video_name):
    cap = cv2.VideoCapture(video_name)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return total_frame, fps, H, W


def get_status():
    if cfg['video_list']!='':
        df = pd.read_csv(cfg['video_list'])
        if df.shape[1]>1:
            df = df[df.iloc[:, 1] == 1]
        video_names = df.iloc[:, 0].tolist()
    else:
        video_names=os.listdir(cfg['video_dir'])
        video_names=[v for v in video_names if any([v.lower().endswith(end) for end in ['.mp4','.ogg','.mov','webm']])]

    if osp.exists(cfg['label_file']):
        with open(cfg['label_file']) as f:
            video_labels = json.load(f)
    else:
        os.makedirs(osp.dirname(cfg['label_file']), exist_ok=True)
        video_labels = []
    labeled_names = [l['name'] for l in video_labels]
    unlabeled_names = list(set(video_names)-set(labeled_names))
    return video_labels, unlabeled_names


def save_labels():
    video_labels_ = copy.deepcopy(video_labels)
    with open(cfg['label_file'], 'w') as f:
        json.dump(video_labels_, f, ensure_ascii=False)


@app.route('/')
def hello_world():
    return 'LabelV-STL'


@app.route('/<task_name>', methods=("GET", "POST"))
def video(task_name):
    if task_name != cfg['task_name']:
        abort(404)
    if request.method == 'GET':
        if len(unlabeled_names) == 0:
            return f'标注任务已完成, 共标注视频{len(video_labels)}个'
        name = unlabeled_names.pop(0)
        unlabeled_names.append(name)
        video_name = osp.join(cfg['video_dir'], name)
        total_frame, fps, H, W = videoinfo(video_name)
        scale = cfg['max_size'] / max(H, W)
        h, w = round(H * scale), round(W * scale)
        video_url=f'videos/{name}'
        html = make_html(video_url, total_frame, h, w, fps=round(fps, 4), labeled=len(video_labels),
                         total=total_videos, name=name, scale=scale)
        return html

    if request.method == 'POST':
        t: dict = request.form.to_dict()
        t['actions'], t['scale'] = json.loads(t.pop('labels')), float(t['scale'])
        t['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        video_labels.append(t)
        unlabeled_names.remove(t['name'])
        save_labels()
        return redirect(url_for('video', task_name=task_name), code=301)

@app.route('/videos/<path>')
def custom_static(path):
    return send_from_directory(cfg['video_dir'], path)

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    video_labels, unlabeled_names = get_status()
    total_videos = len(video_labels)+len(unlabeled_names)
    app.config['SECRET_KEY'] = '123456'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
    app.jinja_env.auto_reload = True
    print(f"\033[5;31;40mLabelV-STL URL: http://0.0.0.0:{cfg['port']}/{cfg['task_name']}\033[0m")
    http_server = make_server('0.0.0.0', cfg['port'], app)
    http_server.serve_forever()
