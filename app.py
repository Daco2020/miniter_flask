from flask      import Flask, jsonify, request, current_app
from flask.json import JSONEncoder, JSONDecoder
from sqlalchemy import create_engine, text

# app          = Flask(__name__)
# app.id_count = 1
# app.users    = {} # 아주 작은 데이터베이스의 역할을 해준다. 
# app.contents = []

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)

def get_user(user_id):
    user = current_app.database.execute(text("""
        SELECT
            id,
            name,
            email,
            profile
        FROM users
        WHERE id = :user_id
    """), {
        'user_id' : user_id
    }).fetchone()

    return {
        'id'      : user['id'],
        'name'    : user['name'],
        'email'   : user['email'],
        'profile' : user['profile']
    } if user else None

def insert_user(user):
    return current_app.database.execute(text("""
        INSERT INTO users (
            name,
            email,
            profile,
            hashed_password
        ) VALUES (
            :name,
            :email,
            :profile,
            :hashed_password
        )
    """), user).lastrowid # 이건 뭘까?

def insert_content(user_content):
    return current_app.database.execute(text("""
        INSERT INTO contents (
            user_id,
            content
        ) VALUES (
            :id,
            :content
        )
    """), user_content).rowcount

def insert_follow(user_follow):
    return current_app.database.execute(text("""
        INSERT INTO users_follow_list (
            user_id,
            follow_user_id
        ) VALUES (
            :id,
            :follow
        )
    """), user_follow).rowcount

def insert_unfollow(user_unfollow):
    return current_app.database.execute(text("""
        DELETE FROM users_follow_list
        WHERE user_id = :id
        AND follow_user_id = :unfollow
    """), user_unfollow).rowcount

def get_timeline(user_id):
    timeline = current_app.database.execute(text("""
        SELECT
            t.user_id,
            t.content
        FROM contents t
        LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
        WHERE t.user_id = :user_id
        OR t.user_id = ufl.follow_user_id
    """), {
        'user_id' : user_id
    }).fetchall() # 이건 뭘까?

    return [{
        'user_id' : content['user_id'],
        'content' : content['content']
    } for content in timeline]

def create_app(test_config = None):
    app = Flask(__name__)

    app.json_encoder = CustomJSONEncoder

    # if test_config in None: # text_config가 None이 아니라면 text_config설정을 적용한다.
    app.config.from_pyfile("config.py") # config.py를 가져온다.
    # else:
    #     app.config.update(test_config) 

    database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0) # create_engine 으로 데이터베이스 객체를 생성한다.
    app.database = database # 외부에서도 데이터베이스를 사용할 수 있는 app 을 생성한다.

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user    = request.json
        new_user_id = insert_user(new_user)
        new_user    = get_user(new_user_id)
        
        return jsonify(new_user)

    @app.route("/content", methods=['POST'])
    def content():
        user_content = request.json
        content      = user_content['content']

        if len(content) > 300:
            return '300자를 초과했습니다.', 400

        insert_content(user_content)

        return '성공', 200
    
    @app.route("/follow", methods=['POST'])
    def follow():
        payload = request.json
        insert_follow(payload)

        return '성공', 200

    @app.route("/unfollow", methods=['POST'])
    def unfollow():
        payload = request.json
        insert_unfollow(payload)
        
        return '성공', 200

    @app.route('/timeline/<int:user_id>', methods=['GET'])
    def timeline(user_id):
        return jsonify({
            'user_id'  : user_id,
            'timeline' : get_timeline(user_id)
        })

    return app   


# 명령어 : FLASK_APP=app.py FLASK_DEBUG=1 flask run 

# if __name__ == "__main__":
#     app.debug = True
#     app.run()

