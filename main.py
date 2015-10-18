#coding=utf-8

import traceback
import json
from flask import Flask, render_template, redirect, url_for, request
import model

app = Flask('scrum')


@app.route('/')
def index():
    return  redirect(url_for('my_taskboard'))

@app.route('/taskboard/')
def my_taskboard():
    '我的任务板'
    data = {'project': model.get_project(),
            'userstory': model.get_userstory(with_frame=True),
            'backlog': model.get_backlog(with_frame=True)}
    return render_template('taskboard.html', data=data)

@app.route('/taskboard/update/', methods=['POST'])
def ajax_task_update():
    '更新任务'
    try:
        data = {'name': request.form['name'],
                'status': request.form['status'],
                'priority': request.form['priority'],
                'project_id': request.form['project_id']}
        subtask = json.loads(request.form['subtask'])
        usid = request.form['id']
        rows = model.update_userstory(usid, data, subtask)
        if not rows:
            raise Exception(u'用户故事（id=%s）不存在！' % usid)
        return json.dumps({'code': 0})

    except Exception as e:
        traceback.print_exc()
        return json.dumps({'code': 1, 'message': e.message})


@app.route('/ajax/taskboard/progress/save/', methods=['POST'])
def ajax_task_updateprogress():
    '更新子任务进度'
    try:
        data = {'progress': request.form['progress']}
        subtask_id = request.form['subtask_id']
        rows = model.update_subtask(subtask_id, data)
        if not rows:
            raise Exception(u'子任务（id=%s）不存在！' % subtask_id)
        return json.dumps({'code': 0})

    except Exception as e:
        traceback.print_exc()
        return json.dumps({'code': 1, 'message': e.message})

@app.route('/review/')
def daily_review():
    '每日Review'
    data = {'review_list': model.get_review_list(),
            'today': model.get_today()}
    return render_template('review.html', data=data)

@app.route('/ajax/review/update/', methods=['POST'])
def ajax_review_update():
    try:
        data = json.loads(request.form['reviewdata'])
        model.update_review(data)
        return json.dumps({'code': 0})

    except Exception as e:
        traceback.print_exc()
        return json.dumps({'code': 1, 'message': e.message})

@app.route('/ajax/review/generate_workdone/', methods=['POST'])
def ajax_generate_workdone():
    '自动生成今日工作内容'
    try:
        today = request.form['today']
        res = model.review_generate_workdone(today)
        return json.dumps({'code': 0, 'workdone': res})

    except Exception as e:
        traceback.print_exc()
        return json.dumps({'code': 1, 'message': e.message})




##################
# 下面代码作废
##################
@app.route('/userstory/delete/', methods=['POST'])
def ajax_delete_us():
    try:
        usid = request.form['usid']
        rows = model.delete_userstory(usid)
        if not rows:
            raise Exception(u'用户故事（id=%s）不存在！' % usid)
        return json.dumps({'code': 0})

    except Exception as e:
        traceback.print_exc()
        return json.dumps({'code': 1, 'message': e.message})

@app.route('/backlog/delete/', methods=['POST'])
def ajax_delete_backlog():
    try:
        blid = request.form['blid']
        rows = model.delete_backlog(blid)
        if not rows:
            raise Exception(u'Backlog（id=%s）不存在！' % blid)
        return json.dumps({'code': 0})

    except Exception as e:
        traceback.print_exc()
        return json.dumps({'code': 1, 'message': e.message})

if __name__ == '__main__':
    app.run(debug=True)
