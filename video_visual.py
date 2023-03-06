import os
import decord
import json
import cv2
import os.path as osp
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont
from scipy.interpolate import interp1d

fourcc = cv2.VideoWriter_fourcc(*'mp4v')


def display_chinese(img_OpenCV, text, x, y, color=(255, 0, 0)):
    img_PIL = Image.fromarray(cv2.cvtColor(img_OpenCV, cv2.COLOR_BGR2RGB))  # cv2和PIL中颜色的hex码的储存顺序不同
    color = list(color)
    color.reverse()
    color = tuple(color)
    # PIL图片上打印汉字
    draw = ImageDraw.Draw(img_PIL)  # 图片上打印
    # NotoSansCJK-Bold.ttc  NotoSansCJK-Regular.ttc  NotoSerifCJK-Bold.ttc  NotoSerifCJK-Regular.ttc
    font = ImageFont.truetype('Alibaba-PuHuiTi-Regular.ttf', 40)  # 参数1：字体文件路径，参数2：字体大小
    draw.text((x, y), text, color, font=font)  # 参数1：打印坐标，参数2：文本，参数3：字体颜色，参数4：字体
    # img_PIL.save('02.jpg', 'jpeg')  # 使用PIL中的save方法保存图片到本地

    img = cv2.cvtColor(np.array(img_PIL), cv2.COLOR_RGB2BGR)  # PIL图片转cv2 图片
    return img


def inp_boxes(boxes: dict, start, end):
    idxs = sorted([int(i) for i in boxes.keys()])
    bbox = [boxes[str(i)] for i in idxs]
    new_bboxes = []
    for i in range(4):
        f = interp1d(idxs, [b[i] for b in bbox])
        new_b = f(list(range(start, end + 1)))
        new_bboxes.append(new_b)
    new_bboxes = np.stack(new_bboxes, axis=1)
    return new_bboxes


def video2frames(name):
    v = decord.VideoReader(name)
    imgs = v.get_batch(list(range(len(v)))).asnumpy()
    N, H, W, c = imgs.shape
    frames = imgs[:, :, :, ::-1]
    fps = v.get_avg_fps()
    return frames, fps, H, W


def frames2video(imgs, video_name, fps):
    n, h, w, c = imgs.shape
    tmp_name = video_name.replace('.mp4', '_in.mp4')
    videoWriter = cv2.VideoWriter(tmp_name, fourcc, fps, (w, h), True)
    for img in imgs:
        videoWriter.write(img)
    videoWriter.release()
    os.system(f'ffmpeg -y -loglevel quiet -i {tmp_name} -vcodec libx264 {video_name}')
    os.remove(tmp_name)


def visual_video(anno, in_video_dir, out_video_dir):
    video_name = osp.join(in_video_dir, anno['name'])
    out_name = osp.join(out_video_dir, anno['name'])
    if osp.exists(out_name) or len(anno['actions'])==0:
        return
    else:
        os.makedirs(osp.dirname(out_name), exist_ok=True)
    frames, fps, H, W = video2frames(video_name)
    frames = [img for img in frames]
    scale = anno['scale']
    for action in anno['actions']:
        start, end = action['start'], action['end']
        new_boxes = inp_boxes(action['boxes'], start, end)
        new_boxes = new_boxes / scale
        new_boxes = np.round(new_boxes).astype('int32')
        color = (np.random.randint(50, 255), np.random.randint(50, 255), np.random.randint(50, 255))
        min_len = min(end+1, len(frames))
        for idx in range(start, min_len):
            img = frames[idx].copy()
            img = cv2.rectangle(img, (new_boxes[idx - start, 0], new_boxes[idx - start, 1]), (new_boxes[idx - start, 2], new_boxes[idx - start, 3]), color, thickness=5)
            img = display_chinese(img, action['label'], new_boxes[idx - start, 0], new_boxes[idx - start, 1], color)
            frames[idx] = img
    frames = np.stack(frames, axis=0)
    frames2video(frames, out_name, fps)


if __name__ == '__main__':
    video_dir='static/example_data'
    output_dir='static/example_data_visual'
    label_file='static/example_data/video_stl_1201.json'
    annotations = json.load(open(label_file))
    for anno in tqdm(annotations):
        if len(anno['actions'])>0:
            visual_video(anno,video_dir,output_dir)
