import os
import sys
import copy
import yaml
import pandas as pd
import os.path as osp
from datetime import timedelta
from flask import Flask, request, url_for, redirect, abort, send_from_directory
from wsgiref.simple_server import make_server
app = Flask(__name__)


def make_action_option(label_ids, label_desc):
    text = ""
    for id_, desc in zip(label_ids, label_desc):
        text = text + f"""<label for="{id_}"> <input id="{id_}" type="radio" name="videolabel" value="{id_}">{desc}</label>\n"""
    return text


def make_html(video_url, labeled, total, name):
    action_option = make_action_option(cfg['label_id'], cfg['label_desc'])
    html = f"""<!DOCTYPE HTML>
<html lang="zh-CN">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,minimum-scale=1.0,user-scalable=no">
<title>LabelV-CLS</title>
<body>
<div align="center">
    <video id="video" src={video_url} height="50%" controls="controls" autoplay="autoplay" loop="loop">
    </video>
    <script>
        var video = document.getElementById("video")
        video.playbackRate = {cfg['playback_rate']}
        let h=video.getBoundingClientRect().height
        let w=video.getBoundingClientRect().width
        var scale=960/Math.max(h,w)
        video.height=h*scale
        video.muted=true
    </script>
    <form action="/{cfg['task_name']}" method="post">{action_option}
        <br/>
        <input type="submit" value="提交结果"/>
        标注进度：{labeled}/{total}
        <input type="hidden" name="name" value={name}>
        <br/>
    </form>
    <br/>
    刷新网页或不标注直接提交可暂时跳过该视频
    <br/>
</div>
</body>
</html>
"""
    return html


def get_status():
    if cfg['video_list']!='':
        df=pd.read_csv(cfg['video_list'])
        video_names = df.iloc[:, 0].tolist()
    else:
        video_names=os.listdir(cfg['video_dir'])
        video_names=[v for v in video_names if any ([ v.lower().endswith(end) for end in ['.mp4','.ogg','.mov','webm',]])]
    if osp.exists(cfg['label_file']):
        video_labels = pd.read_csv(cfg['label_file'])
    else:
        os.makedirs(osp.dirname(cfg['label_file']), exist_ok=True)
        video_labels = pd.DataFrame(data=[], columns=['path', 'label_id'])
    labeled_names = video_labels['path'].tolist()
    unlabeled_names = list(set(video_names)-set(labeled_names))
    return video_labels, unlabeled_names


def save_labels():
    video_labels_ = copy.deepcopy(video_labels)
    video_labels_.to_csv(cfg['label_file'], index=False)


@app.route('/')
def hello_world():
    return 'LabelV-CLS'


@app.route('/<task_name>', methods=("GET", "POST"))
def video(task_name):
    global video_labels
    if task_name != cfg['task_name']:
        abort(404)
    if request.method == 'GET':
        if len(unlabeled_names) == 0:
            return f'标注任务已完成, 共标注视频{len(video_labels)}个'
        name = unlabeled_names.pop(0)
        unlabeled_names.append(name)
        video_url=f'videos/{name}'
        html = make_html(video_url, labeled=len(video_labels), total=total_videos, name=name)
        return html

    if request.method == 'POST':
        t: dict = request.form.to_dict()
        if 'videolabel' in t:
            video_labels = video_labels.append({'path': t['name'], 'label_id': t['videolabel']}, ignore_index=True)
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
    print(f"\033[5;31;40mLabel-CLS URL: http://0.0.0.0:{cfg['port']}/{cfg['task_name']}\033[0m")
    http_server = make_server('0.0.0.0', cfg['port'], app)
    http_server.serve_forever()
