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
            'userstory': model.get_userstory()}
    return render_template('userstory.html', data=data)

@app.route('/userstory/add/', methods=['POST'])
def ajax_add_new_us():
    try:
        data = {'name': request.form['name'],
                'status': request.form['status'],
                'priority': request.form['priority'],
                'project_id': request.form['project_id']}
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


if __name__ == '__main__':
    app.run(debug=True)
