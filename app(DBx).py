from flask      import Flask, jsonify, request
from flask.json import JSONEncoder, JSONDecoder
from sqlalchemy import create_engine, text

app          = Flask(__name__)
app.id_count = 1
app.users    = {} # 아주 작은 데이터베이스의 역할을 해준다. 
app.contents = []

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

@app.route("/sign-up", methods=['POST'])
def sign_up():
    new_user                = request.json
    new_user["id"]          = app.id_count
    app.users[app.id_count] = new_user
    app.id_count            = app.id_count + 1

    return jsonify(new_user)

@app.route("/contents", methods=['POST'])
def contents():
    payload                = request.json
    user_id  = int(payload['id'])
    contents = payload['contents']

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다.', 400

    if len(contents) > 300:
        return '300자를 초과했습니다.', 400

    user_id = int(payload['id'])

    app.contents.append({
        'user_id'  : user_id,
        'contents' : contents
    })

    return 'success', 200

@app.route("/follow", methods=['POST'])
def follow():
    payload           = request.json
    user_id           = int(payload['id'])
    user_id_to_follow = int(payload['follow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).add(user_id_to_follow)

    return jsonify(user)

@app.route("/unfollow", methods=['POST'])
def unfollow():
    payload           = request.json
    user_id           = int(payload['id'])
    user_id_to_follow = int(payload['unfollow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_follow) 
    # discard 메소드는 remove와 달리 에러를 반환하지 않으므로 따로 존재여부를 체크하지 않아도 되어 좋다.

    return jsonify(user)

@app.route('/timeline/<int:user_id>', methods=['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400
    
    follow_list = app.users[user_id].get('follow', set()) # 없으면 빈 set을 반환
    follow_list.add(user_id) # 본인 아이디를 넣어주어야 자신의 피드도 볼 수 있음
    timeline = [contents for contents in app.contents if contents['user_id'] in follow_list]
    
    return jsonify({
        'user_id'  : user_id,
        'timeline' : timeline
    })

if __name__ == "__main__":
    app.debug = True
    app.run()

