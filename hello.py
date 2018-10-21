# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired
import re
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)


class resForm(FlaskForm):
    res = SelectField(u'Выберите РЭС', choices=[('aprv', u'Апрелевская РЭС'),('dmdv', u'Домодедовская РЭС'),('chhv', u'Чеховская РЭС'),('klmv', u'Климовская РЭС'),('vrnv', u'Вороновская РЭС'),('pdls', u'Подольская РЭС'),('stlb', u'Столбовая РЭС'),('vdns', u'Видновская РЭС'),('trsk', u'Троицкая РЭС'),('srph', u'Серпуховская РЭС'),('none', u'Другая')], validators=[DataRequired()])
    col = StringField(u'Вставьте из реестра поле с номерами сканирования', validators=[DataRequired()])
    submit = SubmitField(u'Преобразовать')

class resultForm(FlaskForm):
    result = StringField(u'Вставьте отчет', validators=[DataRequired()])
    submit = SubmitField(u'Преобразовать')

class logForm(FlaskForm):
    log = StringField(u'Вставьте лог', validators=[DataRequired()])
    submit = SubmitField(u'Преобразовать')

class reportForm(FlaskForm):
    scan = StringField(u'Номера сканов')
    arch = StringField(u'Архивные номера')
    submit = SubmitField(u'Преобразовать')
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/report', methods=['GET', 'POST'])
def report():
    form3 = reportForm()
    scan = form3.scan.data
    arch = form3.arch.data
    form3.scan.data = ''
    form3.arch.data = ''

    sc = ''
    if unicode(scan).find('select')==-1:
        s = re.sub('\(', '_', unicode(scan)) 
        s = re.sub('\.', '_', s)
        s = re.sub('-', '_', s)
        s = re.sub('[^\W\d]_', '', s)
        s = re.sub('_\d\d?', '', s)
        s = re.findall('\d\d+', s)
        s = [s[i] for i in range(len(s)) if s[i] not in s[:i]]
        length_s = len(s)
        for i in s:
            sc = sc + i + ', '
        sc = sc[:-2]
    else:
        s = re.findall('\'[^\'\']*\' as sFileName', unicode(scan))
        for i in range(len(s)):
            s[i] = s[i].replace('\'', '')
            s[i] = s[i].replace(' as sFileName', '')
            s[i] = re.sub('\D\D\D*_', '', s[i])
            s[i] = re.sub('_.*', '', s[i])

        s = [s[i] for i in range(len(s)) if s[i] not in s[:i]]
        length_s = len(s)
        for i in s:
            sc = sc + i + ', '
        sc = sc[:-2]

    ar = ''
    if unicode(arch).find('select')==-1:
        a = re.sub(u'По реестру', '', unicode(arch))
        a = re.sub(u'По', '', a)
        a = re.sub(u'[Аа]рх\w*\.?', '', unicode(a), flags=re.U)
        a = re.sub(u'№', '', a)
        a = re.sub(',', ' ', a)
        a = re.split(' ', a)
        a = [a[i] for i in range(len(a)) if a[i] not in a[:i] and a[i]!='']
        length_a = len(a)
        for i in a:
            ar = ar + i + ', '
        ar = ar[:-2]
    else:
        a = re.findall('\'[^\'\']*\' as sArchNum', unicode(arch))
        for i in range(len(a)):
            a[i] = a[i].replace('\'', '')
            a[i] = a[i].replace(' as sArchNum', '')
        a = [a[i] for i in range(len(a)) if a[i] not in a[:i]]
        length_a = len(a)
        for i in a:
            ar = ar + i + ', '
        ar = ar[:-2]
    
    return render_template('report.html', form3=form3, arch=arch, scan=scan, sc=sc, ar=ar, length_s=length_s, length_a=length_a)

@app.route('/log', methods=['GET', 'POST'])
def log():
    form2 = logForm()
    log = form2.log.data
    notfound = re.findall(u'\d*_\d*.\w\w\w\w? не найден', unicode(log))
    for i in range(len(notfound)):
        notfound[i] = re.sub(u' не найден', '', notfound[i])
        notfound[i] = re.sub(u'.tif', '', notfound[i])
    form2.log.data = ''
    return render_template('log.html', form2=form2, notfound=notfound, log=log)

@app.route('/result', methods=['GET', 'POST'])
def result():
    form1 = resultForm()
    result = form1.result.data
    text = unicode(result)
    a = re.sub('.*from \(\s+union\s', '', text)
    b = re.sub('.*from \(\s+', '', a)
    c = re.sub('\)\st\s+where.*', '', b)
    d = re.split('union\s+', c);
    itog = []
    for i in range(len(d)):
        quotes = re.findall('\'[^\'\']*\'', d[i])
        value = []
        for q in quotes:
            value.append(q.replace('\'', ''))
        itog.append(value[:2]) 
    df = pd.DataFrame()
    a = bool(len(df))
    if len(itog[0])>=1:
        df = pd.DataFrame(itog, columns = [u'Название файла', u'Адрес'], index = range(1, len(itog)+1))
        for i in range(len(df)):
            df.iloc[i][0] = df.iloc[i][0].replace('.tif', '')
            df.iloc[i][1] = re.sub(u'Исполнительно.*оборудование ', '', df.iloc[i][1])           
            df.iloc[i][1] = re.sub(u'Исполнительно.*давления ', '', df.iloc[i][1])
            df.iloc[i][1] = re.sub(u'Исполнительно.*газопровод ', '', df.iloc[i][1]) 
            a = bool(len(df))
    form1.result.data = ''
    return render_template('result.html', form1=form1, df=df.to_html(classes='table'), a=a)

@app.route('/', methods=['GET', 'POST'])
def index():
    res = None
    form = resForm()
    res = form.res.data
    col = form.col.data
    form.res.data = res
    form.col.data = ''                               
    l = re.sub('\.', '_', unicode(col))
    l = re.sub('\(', '_', l)
    l = re.sub('-', '_', l)
    l = re.findall('\d\d+_?\d*', l)
    if res == 'none':
        for i in range(len(l)):
            if l[i].find('_') == -1:
                l[i] = l[i]+'_1,2'
            else:
                if l[i][l[i].find('_')+1:]=='1':
                    l[i] = l[i].replace('_1', '_1,2')
                elif l[i][l[i].find('_')+1:]=='2':
                    l[i] = l[i].replace('_2', '_1,2')
                else:
                    l[i] = l[i]
    else:
        for i in range(len(l)):
            if l[i].find('_') == -1:
                l[i] = unicode(res)+'_'+l[i]+'_1,2'
            else:
                if l[i][l[i].find('_')+1:]=='1':
                    l[i] = unicode(res)+'_'+l[i].replace('_1', '_1,2')
                elif l[i][l[i].find('_')+1:]=='2':
                    l[i] = unicode(res)+'_'+l[i].replace('_2', '_1,2')
                else:
                    l[i] = unicode(res)+'_'+l[i]
    l = [l[i] for i in range(len(l)) if l[i] not in l[:i]]      
    return render_template('index.html', form=form, l=l, res=res, col=col)


if __name__ == "__main__":
    app.run(debug=True)

