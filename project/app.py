from flask import Flask, jsonify, render_template, request, make_response, redirect, url_for,flash
import os
import json

import datetime as dt
from sqlalchemy import or_, and_
from flask_login import LoginManager,login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask.cli import FlaskGroup
from flask_migrate import Migrate




app = Flask(__name__)
app.static_folder='static'

base_dir = os.path.abspath(os.path.dirname(__file__))   #현재 파일의 절대경로를 "base_dir" 변수에 저장
db_file = os.path.join(base_dir, 'db.sqlite') #현재 파일의 경로+'db.sqlite' 해서 "db_file" 변수에 저장

#아래 3줄을 app의 config를 설정  : sqlalchemy 사용을 위한 기초설정을 하는 과정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+db_file  # db uri 설정
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True   # teardown 시 commit을 하겠다(teardown : 사이트에서 요청 수신 및 정보 제공 성공시 나오는것)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # false로 해야 warning message 가 안나옴
app.config['X_CONTENT_TYPE_OPTIONS']='nosniff'

from project.models import db, Diary, User
db.init_app(app)  #일단 지금 __init__() got an unexpected keyword argument 'method' 이 에러가 발생했는데, 여기 app이랑 밑에 app.route(,method=) 여기가 문제인듯?
db.app = app
with app.app_context(): #context오류 해결을 위함
    db.create_all() #db를 초기화 하여 생성하는데 이게 내 프로젝트에 필요할 지는 일단 미지수.
migrate = Migrate(app, db, render_as_batch=True)



app.config['SECRET_KEY'] = 'lsy0328'
login_manager = LoginManager(app)  #flask-login의 핵심 '클래스' 객체를 만든다.
login_manager.login_view= 'login'  #'login'이라는 view함수의 이름을 설정한다

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  #아직 모름

@app.route('/',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('pw')
        
				# 일치하는 user 뽑아주고,
        user = User.query.filter_by(name=name).first()  #filter_by  는 조금 더 간단하지만 and로만 가능        
				# 있으면, 로그인하고, dashboard(나는 인덱스로 넘어가긴 할듯 최종적으로) 넘기기
        if user: 
            if check_password_hash(user.pw, password):
                login_user(user)
                return redirect(url_for('dashboard'))
				# 일치하는 게 없으면, 로그인 실패, return render_template 
        else:
            flash('로그인 실패. 사용자 정보를 확인하세요','danger')
    return render_template('login.html')


@app.route('/dashboard')  # route에선 메소드를 지정하지 않으면 기본적으로 GET.
@login_required
def dashboard():
    id=current_user.id
    diaries = Diary.query.filter_by(user_id=id)
    return render_template('dashboard.html',name=current_user.name, id=id, diaries=diaries) 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃 되었습니다.','success')
    return redirect(url_for('login'))

@app.route('/sign-in',methods=['GET','POST'])
def sign_in():
    return render_template('sign-in.html')


@app.route('/sign-up',methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        pw = request.form.get('pw')
        #유효성 검사
        if len(email) < 5 : 
            flash("이메일은 5자 이상입니다",category="error")
        elif len(name) <2 :
            flash("이름은 2자 이상입니다",category="error")
        elif len(pw) < 7 :
            flash("비밀번호는 7자 이상입니다",category="error")    
        else:
            new_user  = User(email=email, pw=generate_password_hash(pw, method='pbkdf2:sha256'), name=name)
            db.session.add(new_user)
            db.session.commit()
            flash("회원가입 완료.",category="success")
            return redirect(url_for('login'))
        
    return render_template("sign-in.html")

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/entries')
@login_required
def entries():
    user_id=current_user.id
    diaries=Diary.query.filter_by(user_id=user_id)
    anchor= request.args.get('anchor')
    return render_template('entries.html',diaries=diaries,anchor=anchor)

@app.route('/diary',methods=['POST'])
@login_required
def create_diary():
    inputemotion = request.form.get('emotiontext','')
    inputcontent = request.form.get('content','')
    emotionimage_path = request.form.get('emotionimage_path','')
    inputdate = dt.datetime.now().strftime("%Y-%m-%d")
    music=request.form.get('music','')
    user_id=current_user.id
    diary = Diary(emotiontext=inputemotion, content=inputcontent,date=inputdate,user_id=user_id, emotionimage_path = emotionimage_path,music=music)
    db.session.add(diary)
    db.session.commit()
    return redirect(url_for('dashboard'))
    

@app.route('/search_diary', methods=['POST','GET'])
@login_required 
def search_diary():
    if request.method == 'POST': #일기 검색하기 SUBMIT=>POST로 옴
        searchkey = request.form.get('searchkey','')
        user_id = current_user.id
        selectdiary = Diary.query.filter((Diary.user_id == user_id)&(or_(Diary.content.like(f"%{searchkey}%"),Diary.emotiontext.like(f"%{searchkey}%")))).all()

        return render_template('diarysearch.html',selectdiary=selectdiary, searchkey=searchkey)


@app.route('/update_diary/<int:id>',methods=['POST','GET'])
@login_required
def update_diary_by_id(id):
    diary = Diary.query.get_or_404(id)
    
    if request.method=="POST":      
        inputemotion = request.form.get('emotiontext','입력값 없음')
        inputcontent = request.form.get('content','입력값 없음')
        diary.emotiontext = inputemotion
        diary.content = inputcontent
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('update.html',diary=diary)

@app.route('/delete_diary/<int:id>',methods=['POST'])
@login_required
def delete_diary_by_id(id):
    diary = Diary.query.get_or_404(id)
    db.session.delete(diary)
    db.session.commit()
    return jsonify({'message' : 'Success'})

@app.route('/recommend_music',methods=['POST','GET'])
@login_required
def recommend_music():
    #음악 추천 로직 추가하기! 
    #기반 데이터 : (그 감정에 해당하는 사용자가 이전에 들었던 음악들 + 현재 일기장에 적혀있는 내용을 분석한 키워드들)
    #바탕으로 리스트들을 쫙 뽑아주고, 선택 OR 본인이 직접 작성(작성 툴을 만들어야 할 지는 유튜브 링크랑 연결하는 거로 확인)
    #해당 플레이리스트 칸을 클릭하면 유튜브 링크로 연결하기. 
    return render_template("dashboard.html")

@app.route('/music')
def song_search():
    return render_template('song-search.html')
    
if __name__=="__main__":
    app.run(debug=True)




    