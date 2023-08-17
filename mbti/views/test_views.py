from datetime import datetime
from flask import Blueprint, render_template, request, url_for, session
from mbti.forms import Question_1_Form, Question_2_Form
from werkzeug.utils import redirect
from keras.preprocessing.sequence import pad_sequences
from mbti.models import E_I_answer, S_N_answer

import torch
from pytorch_transformers import BertTokenizer, BertForSequenceClassification

# MBTI test 진행
bp = Blueprint('test', __name__, url_prefix='/test') 

# Mbti_pred ={}

# Models
##########################################################################

device = torch.device("cpu")

# S & N 추론을 위한 model
tokenizer_2 = BertTokenizer.from_pretrained("bert-base-multilingual-cased", do_lower_case=False)
model_2 = BertForSequenceClassification.from_pretrained('bert-base-multilingual-cased')
model_2.to(device)
model_2.load_state_dict(torch.load('best_model_0.7540_second_comment.pth'))
model_2.eval()

# E & I
##########################################################################
@bp.route('/question_1')
def E_I_question():
    session.clear() # 웹브라우저 방문(사용자마다) session 초기화
    return render_template('test.html')

# E & I 추론 작업
@bp.route('/question_1', methods=['GET','POST'])
def E_I_predict():
    data_1 = request.form['comment_1'] # test.html의 form key 값을 받아옴
    print(data_1)
    session['E&I'] = 'E'
    return render_template('test_2.html') # test_2.html에 추론 결과 전달

# S & N
###########################################################################
# S & N 추론 작업
@bp.route('/question_2', methods=['GET','POST'])
def S_N_predict():
    data_2 = request.form['comment_2']
    
    ########################## predict ##########################
    class_name=['N', 'S']
    MAX_LEN = 87

    token_text = tokenizer_2.tokenize(data_2)
    input_ids = [[tokenizer_2.convert_tokens_to_ids(tokens) for tokens in token_text]]
    input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")
    input_ids = torch.tensor(input_ids)
    
    input_ids = input_ids.to(device)

    with torch.no_grad():
        output = model_2(input_ids)

    output = output[0]
    pred_2 = torch.argmax(output, 1)
    
    predict_2 = class_name[pred_2]

    session['S&N'] = predict_2 # 추론 결과를 session에 value값으로 저장함
    # Mbti_pred['S&N'] = predict_2
    print(session)
    return render_template('test_3.html')

# T & F
###########################################################################
# T & F 추론 작업
@bp.route('/question_3', methods=['GET','POST'])
def T_F_predict():
    session['T&F'] = 'T'
    return render_template('test_4.html')


# P & J
###########################################################################
# P & J 추론 작업
@bp.route('/question_4', methods=['GET','POST'])
def P_J_predict():
    session['P&J'] = 'J'
    return render_template('result.html')
    # result.html에서 session 값을 통해 사용자의 mbti 검사 결과를 출력함