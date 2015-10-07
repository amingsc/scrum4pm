#coding=utf-8

import traceback
import json
from flask import Flask, render_template, redirect, url_for, request
import model

app = Flask('scrum')


@app.route('/')
def index():
    return  redirect(url_for('list_userstory'))


@app.route('/userstory/list/')
def list_userstory():
    data = {'project': model.get_project(),
            'userstory': model.get_userstory(with_frame=True),
            'backlog': model.get_backlog(with_frame=True)}
    return render_template('userstory.html', data=data)

@app.route('/userstory/add/', methods=['POST'])
def ajax_edit_us():
    try:
        data = {'name': request.form['name'],
                'status': request.form['status'],
                'priority': request.form['priority'],
                'project_id': request.form['project_id']}
        usid = request.form['userstory_id']
        if usid:    # when update
            rows = model.update_userstory(usid, data)
            if not rows:
                raise Exception(u'用户故事（id=%s）不存在！' % usid)
            return json.dumps({'code': 0})
        else:   # when insert
            rowid = model.insert_userstory(data)
            return json.dumps({'code': 0, 'rowid': rowid})

    except Exception as e:
        traceback.print_exc()
        return json.dumps({'code': 1, 'message': e.message})

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
