from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db

auth = Blueprint('auth',__name__)

@auth.route('/sign-in',method=['GET','POST'])
def sign_in():
    return render_template('sign-in.html')


@auth.route('/sign-up',method=['GET','POST'])
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
            new_user  = User(email=email, pw=generate_password_hash(pw, method='sha256'), name=name)
            db.session.add(new_user)
            db.session.commit()
            flash("회원가입 완료.",category="success")
            return redirect(url_for('login'))
    return render_template("sign_up.html")
