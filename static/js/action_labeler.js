var bar = document.getElementById('progress_bar');
bar.onchange = bar_change;
bar.oninput = bar_change;

var canvas_box = document.getElementById('c1');
var ctx_box = canvas_box.getContext("2d");
var video = document.getElementsByTagName("video")[0];

var op = 0; //0 无操作， 1画框 2左上移动 3右下移动 4整体移动 5左下 6右上
var dx = 0, dy = 0, ux = 0, uy = 0, mx = 0, my = 0;
var box = new Vue({
    data: {x1: 0, y1: 0, x2: 0, y2: 0},
    computed: {
        width: function () {
            return this.x2 - this.x1;
        },
        height: function () {
            return this.y2 - this.y1;
        },
        centerx: function () {
            return (this.x2 + this.x1) / 2;
        },
        centery: function () {
            return (this.y2 + this.y1) / 2;
        },
        str: function () {
            return [box.x1, box.y1, box.x2, box.y2].join(',')
        }
    }
})

function closeLeftTop(x, y, th = 20) {
    return Math.abs(x - box.x1) < th && Math.abs(y - box.y1) < th;
}

function closeLeftBottom(x, y, th = 20) {
    return Math.abs(x - box.x1) < th && Math.abs(y - box.y2) < th;
}

function closeRightBottom(x, y, th = 20) {
    return Math.abs(x - box.x2) < th && Math.abs(y - box.y2) < th;
}

function closeRightTop(x, y, th = 20) {
    return Math.abs(x - box.x2) < th && Math.abs(y - box.y1) < th;
}

function closeCenter(x, y, split = 8) {
    return Math.abs(x - box.centerx) < box.width / split && Math.abs(y - box.centery) < box.height / split
}

function mdown(e) {
    var rect = canvas_box.getBoundingClientRect();
    dx = Math.max(e.clientX - rect.left.toFixed(),0);
    dy = Math.max(e.clientY - rect.top.toFixed(),0);
    if (closeRightTop(dx,dy)){
        op=6;
    } else if (closeLeftBottom(dx,dy)){
        op=5;
    }else if (closeCenter(dx, dy)) {
        op = 4;
    } else if (closeLeftTop(dx, dy)) {
        op = 2; //左上移动
    } else if (closeRightBottom(dx, dy)) {
        op = 3;//右下移动
    } else {
        op = 1;//画框
    }
}

function mmv(e) {
    e = e || event;
    var rect = canvas_box.getBoundingClientRect();
    mx = e.clientX - rect.left.toFixed();
    my = e.clientY - rect.top.toFixed();
    if (op === 0) {
        if (closeCenter(mx, my)) {
            canvas_box.style.cursor = "move";
        } else if (closeLeftTop(mx, my)) {
            canvas_box.style.cursor = "nw-resize";
        } else if (closeRightBottom(mx, my)) {
            canvas_box.style.cursor = "se-resize";
        } else if (closeLeftBottom(mx, my)){
            canvas_box.style.cursor = "sw-resize";
        } else if (closeRightTop(mx, my)){
            canvas_box.style.cursor = "ne-resize";
        }
        else {
            canvas_box.style.cursor = "default";
        }
        return;
    }
    if (op === 1) {
        if (mx <= dx || my <= dy) {
            return
        }
        box.x1 = dx;
        box.y1 = dy;
        box.x2 = mx;
        box.y2 = my;
        drawRect();
    }
    if (op === 2) {
        if (mx >= box.x2 || my >= box.y2) {
            return
        }
        box.x1 = mx;
        box.y1 = my;
    }
    if (op === 3) {
        if (mx <= box.x1 || my <= box.y1) {
            return
        }
        box.x2 = mx;
        box.y2 = my;
    }
    if (op === 4) {
        let h = box.height;
        let w = box.width;
        box.x1 = Math.round(mx - w / 2);
        box.x2 = box.x1 + w;
        box.y1 = Math.round(my - h / 2);
        box.y2 = box.y1 + h;
    }
    if (op===5){
        if (mx>=box.x2 || my<=box.y1){
            return
        }
        box.x1=mx;
        box.y2=my;
    }
    if (op===6){
        if(mx<=box.x1 || my>=box.y2){
            return
        }
        box.x2=mx;
        box.y1=my;
    }
    drawRect();
}

function mup(e) {
    e = e || event;
    var rect = canvas_box.getBoundingClientRect();
    ux = e.clientX - rect.left.toFixed();
    uy = e.clientY - rect.top.toFixed();
    if (op === 1) {
        if (ux <= box.x1 || uy <= box.y1) {
            return
        }
        box.x2 = ux;
        box.y2 = uy;
        drawRect();
        for (let pair of actionLabel.boxes){
            if (pair[1][0]==0 && pair[1][1]==0 && pair[1][2]==0 && pair[1][3]==0){
                actionLabel.boxes.set(pair[0],[box.x1, box.y1, box.x2, box.y2])
            }
        }
    }
    if (op === 4) {
        box.x1 = Math.max(0, box.x1);
        box.x2 = Math.min(canvas_box.width, box.x2);
        box.y1 = Math.max(0, box.y1);
        box.y2 = Math.min(canvas_box.height, box.y2);
    }
    op = 0;
    if (actionLabel.boxes.has(parseInt(bar.value))) {
        actionLabel.addkeyFrame(parseInt(bar.value), [box.x1, box.y1, box.x2, box.y2])
    }
}

function drawRect(color = "#0f0") {
    canvas_box.height = canvas_box.height;
    ctx_box.strokeStyle = color;
    ctx_box.lineWidth = 2;
    ctx_box.strokeRect(box.x1, box.y1, box.width, box.height);
}

canvas_box.onmousedown = mdown;
canvas_box.onmousemove = mmv;
canvas_box.onmouseup = mup;

var jindu = new Vue({
    el: '#current_frame',
    data: {
        cur_frame: 1
    }
})

video.addEventListener('timeupdate',function(){
    var presentT = this.currentTime;
    bar.value = Math.round(presentT * actionLabel.fps)
    jindu.cur_frame = bar.value
    box_update();
    if (parseInt(jindu.cur_frame) > parseInt(bar.max)){
        bar.value = 0
        jindu.cur_frame = 0
        video.currentTime = 0
        video.play()
    }
})

function box_update(){
    // update_current_frame_box
    //1. 还没有关键帧，无需更新box
    //2. 设置了>=2个关键帧，当前帧不在关键帧范围内的设为0
        // 2.1 当前帧是插值依据，直接返回关键帧的box
        // 2.2 当前帧不是插值依据，则需要插值，首尾关键帧和绿色帧作为插值依据
    let color = "#f00"
    let current_frame_index=parseInt(bar.value)
    if (actionLabel.boxes.size>=2){
        let key_index=new Array() //插值依据帧
        let boxes = Array.from(actionLabel.boxes);
        for (let i=0; i<boxes.length; i++){
            k=boxes[i][0]
            var dom_id = "frame__" + k;
            // 首尾关键帧和绿色帧作为插值依据
            if (String(document.getElementById(dom_id).getAttribute("style")).indexOf("lightgreen") >= 0 || i==0 || i==boxes.length-1) {
                key_index[key_index.length]=k
            }
        }

        if (key_index.includes(current_frame_index)){
            box.x1=actionLabel.boxes.get(current_frame_index)[0]
            box.y1=actionLabel.boxes.get(current_frame_index)[1]
            box.x2=actionLabel.boxes.get(current_frame_index)[2]
            box.y2=actionLabel.boxes.get(current_frame_index)[3]
            color = "#0f0"
        }
        else if (current_frame_index< key_index[0] || current_frame_index>key_index[key_index.length-1]){
            box.x1 = 0
            box.y1 = 0
            box.x2 = 0
            box.y2 = 0
        }
        else {
            let min_key_index, max_key_index
            for (const k of key_index){ //寻找最近的两个插值依据
                if (k<current_frame_index){
                    min_key_index=k
                }
                if (k>current_frame_index){
                    max_key_index=k
                    break;
                }
            }
            let ra = (current_frame_index - min_key_index) / (max_key_index - min_key_index)
            box.x1 = parseInt(actionLabel.boxes.get(min_key_index)[0] + (actionLabel.boxes.get(max_key_index)[0] - actionLabel.boxes.get(min_key_index)[0]) * ra);
            box.y1 = parseInt(actionLabel.boxes.get(min_key_index)[1] + (actionLabel.boxes.get(max_key_index)[1] - actionLabel.boxes.get(min_key_index)[1]) * ra);
            box.x2 = parseInt(actionLabel.boxes.get(min_key_index)[2] + (actionLabel.boxes.get(max_key_index)[2] - actionLabel.boxes.get(min_key_index)[2]) * ra);
            box.y2 = parseInt(actionLabel.boxes.get(min_key_index)[3] + (actionLabel.boxes.get(max_key_index)[3] - actionLabel.boxes.get(min_key_index)[3]) * ra);
            if (actionLabel.boxes.has(current_frame_index)){
                actionLabel.addkeyFrame(current_frame_index, [box.x1, box.y1, box.x2, box.y2])
            }
        }
    }
    drawRect(color)
}

function bar_change() {
    jindu.cur_frame = bar.value
    video.currentTime=jindu.cur_frame/actionLabel.fps
    box_update()
}

document.onkeydown = function (event) {
    event = event || window.event;
    if (event.keyCode === 65) { //a 起始帧
        actionLabel.start = parseInt(bar.value)
        actionLabel.calcKeyFrame()
    }
    if (event.keyCode === 68) { //d 结束帧
        actionLabel.end = parseInt(bar.value)
        actionLabel.calcKeyFrame()
    }
    if (event.keyCode === 70) { //f 前进一帧
        var cur = parseInt(bar.value)
        if (cur === parseInt(bar.max)) {
            bar.value = 0;
        } else {
            bar.value = cur + 1;
        }
        bar.onchange()
    }
    if (event.keyCode === 66) { //b 后退一帧
        var cur = parseInt(bar.value)
        if (cur === 0) {
            bar.value = 0;
        } else {
            bar.value = cur - 1;
        }
        bar.onchange()
    }
    if (event.keyCode === 32) { //backspace 暂停/播放
        if (video.paused) {
            video.play();
            } 
        else {
            video.pause();
        }
    }
}

Vue.component('key-frame', {
    template: '\
    <span v-on:click="green(idx)" v-on:dblclick="nogreen(idx)">\
    <button :id="\'frame__\' + idx" v-on:click="$emit(\'view\')" v-on:focus="$emit(\'view\')">{{ idx }}</button>\
    </span>\
  ',
    props: ['idx', 'box'],
    data() {
        return {
            clicked: "",
        }
    },
    methods: {
        green: function (idx) {
            document.getElementById("frame__"+idx).style.background="lightgreen"
            document.getElementById("frame__"+idx).blur();
        },
        nogreen: function (idx) {
            document.getElementById("frame__"+idx).style.background=""
        }
    },
})
Vue.component('action-labels', {
    template: '\
    <li>\
    <button v-on:click="$emit(\'delete\')">删除</button>{{action_label}}\
    </li>\
  ',
    props: ["action_label"]
})

var actionLabel = new Vue({
    el: "#action-label",
    data: {
        fps: parseFloat(document.getElementById('fps').value),
        start: "",
        end: "",
        label: "",
        boxes: new Map(),
        action_labels: [],
        key_frame_interval: 1
    },
    methods: {
        addkeyFrame: function (idx, box) {
            this.boxes.set(idx, box);
            var arrayObj = Array.from(this.boxes);
            arrayObj.sort(function (a, b) {
                return a[0] - b[0];
            });
            this.boxes = new Map(arrayObj.map(i => [i[0], i[1]]));
        },
        calcKeyFrame: function () {
            this.boxes = new Map();
            if (this.start === '' || this.end === '' || this.end <= this.start) {
            } else {
                let n = Math.ceil((this.end - this.start+1) / (this.fps*this.key_frame_interval));
                let step = (this.end - this.start) / n;
                let idx = this.start;
                while (Math.round(idx) <= this.end) {
                    if (document.getElementById("frame__"+Math.round(idx))) {
                        document.getElementById("frame__"+Math.round(idx)).style.background = "";
                    }
                    this.addkeyFrame(Math.round(idx), [box.x1, box.y1, box.x2, box.y2]);
                    idx += step;
                }
            }
        },
        moveTo: function (idx) {
            bar.value = idx
            box.x1 = this.boxes.get(idx)[0]
            box.y1 = this.boxes.get(idx)[1]
            box.x2 = this.boxes.get(idx)[2]
            box.y2 = this.boxes.get(idx)[3]
            bar.onchange()
            video.pause()
        },
        to_json: function () {
            obj = {'start': this.start, 'end': this.end, 'label': this.label};
            boxes = {};
            for (let [k, v] of this.boxes) {
                var dom_id = "frame__" + k;
                if (String(document.getElementById(dom_id).getAttribute("style")).indexOf("lightgreen") >= 0) {
                    boxes[k] = v;
                }
            }
            obj['boxes'] = boxes;
            return JSON.stringify(obj);
        },
        saveLabel: function () {
            this.$el.children.save_action_button.blur();
            if (this.end<=this.start){return;}
            if (this.label===""){
                alert("请选择类别")
                return
            }
            // 判断第一个和最后一个关键帧是否被选中
            var start_f_lab = String(document.getElementById("frame__"+this.start).getAttribute("style")).indexOf("lightgreen")>=0;
            var end_f_lab = String(document.getElementById("frame__"+this.end).getAttribute("style")).indexOf("lightgreen")>=0;
            if (!(start_f_lab && end_f_lab)) {
                alert("首尾帧必须标记为绿色")
                return
            }
            this.action_labels.push(this.to_json());
        },
        results: function () {
            return "[" + this.action_labels.join(",") + "]"
        }
    }
})

function checkRes() {
    return confirm("已标注"+actionLabel.action_labels.length+"个行为，确定提交吗？")
}
