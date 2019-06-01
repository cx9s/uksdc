# -*-coding:utf-8-*-
from flask import jsonify, request, url_for, json, redirect, abort, flash, get_flashed_messages
from . import api
from script.models.mongodb import Player, Fee
import re
import functools
from script.models.mail import sendMail
from bson.son import SON
from flask_login import current_user

'''
# restful api
#define @requires_auth for api
def check_auth(username, password):
    return username == 'admin' and password == 'admin'

def authenticate():
    message = {'API': "Basic Auth."}
    resp = jsonify(message)
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp

def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

#players
@api.route('/players', methods = ['GET'])
def get_players():
    if request.method == 'GET':
        player = Player()
        res_list = player.getAndSort({},'num')
        return jsonify({'players':res_list}), 200


@api.route('/players', methods=['POST'])
@requires_auth
def add_player():
    if not request.json or not 'name' in request.json:
        abort(400)
    player = Player()
    insExp = {
            "name": request.json['name'],
            "num": int(request.json['num']),
            "dob": request.json['dob'],
            "position": request.json['position'],
            "phone": int(request.json['phone']),
            "addr": request.json['addr']
#            "addr": request.json.get('addr', "")
        }
    data = player.insertOne(insExp)
    return jsonify(data), 201


@api.route('/players/<string:pName>', methods=['GET'])
def get_player(pName):
    player = Player()
    res_list = player.get({'name':pName})
    if len(res_list) == 0:
        abort(404)
    return jsonify({'player':res_list[0]}), 200


@api.route('/players/<string:pName>', methods=['PUT'])
@requires_auth
def update_player(pName):
    player = Player()
    res_list = player.get({'name':pName})
    if len(res_list) == 0:
        abort(404)
    p = res_list[0]

    if not request.json:
        abort(400)
    if 'name' not in request.json or type(request.json['name']) != str:
        abort(400)
    if 'num' not in request.json or type(request.json['num']) != int:
        abort(400)
    if 'dob' not in request.json or type(request.json['dob']) != str:
        abort(400)
    if 'position' not in request.json or type(request.json['position']) != list:
        abort(400)
    if 'phone' not in request.json or type(request.json['phone']) != int:
        abort(400)
    if 'addr' not in request.json or type(request.json['addr']) != str:
        abort(400)

    p['name'] = request.json['name']
    p['num'] = request.json['num']
    p['dob'] = request.json['dob']
    p['position'] = request.json['position']
    p['phone'] = request.json['phone']
    p['addr'] = request.json['addr']
    player.update({'name': p['name']}, p)
    return jsonify({'player':p}), 200


@api.route('/players/<string:pName>', methods=['DELETE'])
@requires_auth
def del_player(pName):
    player = Player()
    res_list = player.get({'name':pName})
    if len(res_list) == 0:
        abort(404)
    player.delete({'name':pName})
    return jsonify(success=True), 204


#fees
@api.route('/fees/<string:name>', methods = ['GET'])
def get_fees_by_name(name):
    fee = Fee()
    res_list = fee.getAndSort({"name":name}, [('date', -1)])
    for row in res_list:
        row['amount'] = int(row['amount'])
    return jsonify({'fees':res_list}), 200


@api.route('/fees/<string:name>/<string:date>', methods = ['GET'])
def get_fees_by_name_and_date(name,date):
    fee = Fee()
    res_list = fee.getAndSort({"name":name,"date":date}, '_id')
    for row in res_list:
        row['amount'] = int(row['amount'])
    return jsonify({'fees':res_list}), 200


@api.route('/fees', methods=['POST'])
@requires_auth
def add_fee():
    if not request.json:
        abort(400)
    if 'name' not in request.json or type(request.json['name']) != str:
        abort(400)
    if 'date' not in request.json or type(request.json['date']) != str:
        abort(400)
    if 'loc' not in request.json or type(request.json['loc']) != str:
        abort(400)
    if 'amount' not in request.json or type(request.json['amount']) != int:
        abort(400)
    fee = Fee()
    insExp = [{
            "name": request.json['name'],
            "date": request.json['date'],
            "loc": request.json['loc'],
            "amount": int(request.json['amount'])
        }]
    data = fee.insert(insExp)
    return jsonify(data[0]), 201


@api.route('/fees/<string:name>/<string:date>', methods=['PUT'])
@requires_auth
def update_fee(name, date):
    loc = request.args.get('loc')
    amount = request.args.get('amount')
    queryExp = {"name":name,"date":date,"loc":loc,"amount":int(amount)}
    fee = Fee()
    res_list = fee.getAndSort(queryExp, '_id')
    if len(res_list) == 0:
        abort(404)
    f = res_list[0]

    if not request.json:
        abort(400)
    if 'name' not in request.json or type(request.json['name']) != str:
        abort(400)
    if 'date' not in request.json or type(request.json['date']) != str:
        abort(400)
    if 'loc' not in request.json or type(request.json['loc']) != str:
        abort(400)
    if 'amount' not in request.json or type(request.json['amount']) != int:
        abort(400)

    f['name'] = request.json['name']
    f['date'] = request.json['date']
    f['loc'] = request.json['loc']
    f['amount'] = request.json['amount']
    fee.update(queryExp, f)
    return jsonify({'fee':f}), 200


@api.route('/fees/<string:name>/<string:date>', methods=['DELETE'])
@requires_auth
def del_fee(name, date):
    loc = request.args.get('loc')
    amount = request.args.get('amount')
    queryExp = {"name": name, "date": date, "loc": loc, "amount": int(amount)}
    fee = Fee()
    res_list = fee.getAndSort(queryExp, '_id')
    if len(res_list) == 0:
        abort(404)
    fee.delete(queryExp)
    return jsonify(success=True), 204

# restful api end

@api.route('/get_name_num_list')
def get_name_num_list():
    player = Player()
    queryExp = {'num':{'$gt':0}}
    itemsExp = {"name":1, "num":1, "_id":0}
    res_list = player.getItems(queryExp, itemsExp, 'num')
    return jsonify(res_list)

#all players including whose num is 0
@api.route('/get_name_num_all_list')
def get_name_num_all_list():
    player = Player()
    queryExp = {}
    itemsExp = {"name":1, "num":1, "_id":0}
    res_list = player.getItems(queryExp, itemsExp, 'num')
    return jsonify(res_list)


@api.route('/get_player_by_name')
def get_player_by_name():
    name = request.args.get('n')
    player = Player()
    res_list = player.getAndSort({'name':re.compile(name),'num':{'$gt':0}}, 'num')
    return jsonify(res_list)


@api.route('/get_feeList_by_name')
def get_feeList_by_name():
    name = request.args.get('n')
    fee = Fee()
    res_list = fee.getAndSort({"name":name}, [('date', -1)])
    return jsonify(res_list)


@api.route('/check_num_exist')
def check_num_exist():
    num = int(request.args.get('n'))
    player = Player()
    res_list = player.get({"num":num})
    print(res_list)
    if len(res_list) == 0:
        return jsonify({'valid':True})
    else:
        return jsonify({'valid':False})


@api.route('/add_player', methods=['POST'])
def add_newplayer():
    if current_user.is_authenticated:
        request_json = {key: dict(request.form)[key][0] for key in dict(request.form)}
        query_json = {
            "name":"",
            "num":0,
            "dob":"",
            "position":[],
            "phone":0,
            "email":"",
            "addr":""
        }
        name = request_json['name']
        query_json['name'] = name
        query_json['num'] = int(request_json['num'])
        query_json['dob'] = request_json['dob']

        posList = request.form.getlist('position')
        for index, item in enumerate(posList):
            query_json['position'].append(item)

        query_json['phone'] = int(request_json['phone'])
        query_json['email'] = request_json['email']
        query_json['addr'] = request_json['addr']

        player = Player()
        player.insertOne(query_json)
        flash('新增 ' +name+' 成功！', 'success')
        return redirect("/addplayer")
    else:
        return redirect("/auth/login")


@api.route('/edit_player', methods=['POST'])
def edit_player():
    if current_user.is_authenticated:
        request_json = {key: dict(request.form)[key][0] for key in dict(request.form)}
        query_json = {
            "name":"",
            "num":0,
            "dob":"",
            "position":[],
            "phone":0,
            "email":"",
            "addr":""
        }
        name = request_json['name']
        query_json['name'] = name
        query_json['num'] = int(request_json['num'])
        query_json['dob'] = request_json['dob']

        posList = request.form.getlist('position')
        for index, item in enumerate(posList):
            query_json['position'].append(item)

        query_json['phone'] = int(request_json['phone'])
        query_json['email'] = request_json['email']
        query_json['addr'] = request_json['addr']

        player = Player()
        player.update({'name': name}, query_json)
        flash(name+' 信息修改成功！', 'success')
        return redirect("/editplayer")
    else:
        return redirect("/auth/login")


@api.route('/edit_fee', methods=['POST'])
def edit_fee():
    if current_user.is_authenticated:
        query_json = {key: dict(request.form)[key][0] for key in dict(request.form)}
        date = query_json['date']
        loc = query_json['loc']
        totalAmount = float(query_json['totalAmount'])
        playerList=request.form.getlist('playerList')

        i = len(playerList)
        amount = round(totalAmount/i)
        insExp = []
        for index, item in enumerate(playerList):
            fee = {"name":item, "date":date, "loc":loc, "amount":amount}
            insExp.append(fee)

        fee = Fee()
        fee.insert(insExp)
        get_flashed_messages();
        flashExp = '成功更新 '+str(i)+' 名队员费用，日期 ' + date+ ' ，地点 ' + loc + ' ，共计 '+str(totalAmount)+' 元！'
        flash(flashExp, 'success')

        #send topup notice emails
        nameFeeList = fee.getNameAndTotalUndue();
        if len(nameFeeList) != 0:
            msgExp = []
            player = Player()
            for item in nameFeeList:
                email = player.getItems({'name': item['_id'], 'email': {'$gt': ''}}, {'email': 1, '_id': 0}, '_id')
                if len(email) == 0:
                    fExp = item['_id'] + ' 余额为 ' + str(item['total']) + ' 元，未发送缴费提醒邮件。'
                    flash(fExp, 'danger')
                else:
                    e = email[0]['email']
                    msgExp.append({
                        "subject": "【绿动北京】队费通知",
                        "addr": e,
                        "msgHTML": "<h3>亲爱的 " + item['_id'] + "，</h3><p>绿动北京提醒您，</p><p>截至目前，您的队费余额为 " + str(
                            item['total']) + "元，该交费了哦。</p>"
                    })
                    fExp = item['_id'] + ' 余额为 ' + str(item['total']) + ' 元，已发送提醒邮件至 ' + e +' 。'
                    flash(fExp, 'warning')

            if len(msgExp) != 0:
                sendMail(msgExp)

        elif len(nameFeeList) == 0:
            flash('没有队员欠费，未发送缴费提醒邮件。', 'info')

        return redirect("/editfee")
    else:
        return redirect("/auth/login")


#test sendMail()
@api.route("/testmail")
@requires_auth
def testmail():
    msgExp=[
        {
            "subject": "队费提醒",
            "addr": "12730529@qq.com",
            "msgHTML": "<h3>亲爱的 李涛，</h3><p>你的队费还有 -169元，该交费了哦。</p>"
        },
            {
                "subject":"队费提醒",
                "addr":"12730529@qq.com",
                "msgHTML":"<h3>亲爱的 李涛，</h3><p>你的队费还有 -169元，该交费了哦。</p>"
            }
        ]
    sendMail(msgExp)
    return 'success'


#statistics
@api.route("/attend")
def attend():
    dateStart = request.args.get('dateStart')
    dateEnd = request.args.get('dateEnd')
    match = {'$and':[{'date':{'$gte': dateStart,'$lt': dateEnd}}, {'amount':{'$lt': 0}}]}
    group = {'_id': "$%s" % 'name','total': {'$sum': 1}}
    sort = SON([('total', -1), ('name', 1)])
    groupTotal = {'_id': "$%s" % 'date','total': {'$sum': 1}}
    sortTotal = SON([('_id', 1)])
    fee = Fee()
    res_list = fee.getAggregate(match, group, sort)
    total = fee.getAggregate(match, groupTotal, sortTotal)
    for item in res_list:
        item['percent'] = format(round(item['total']/len(total), 3), '.0%')
    return jsonify(res_list)
'''