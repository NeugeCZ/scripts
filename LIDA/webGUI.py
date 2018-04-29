# -*- coding: utf-8 -*-
import os, time, unicodedata, re, codecs
from LIDA import analysis
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename

'''
Pro spusteni nastroje LIDA spustte tento soubor a pres prohlizec se pripojte na adresu http://127.0.0.1:5000
For initiation of LIDA annotator tool run this file and access http://127.0.0.1:5000 through your web browser
'''

UPLOAD_FOLDER =  os.path.dirname(os.path.abspath(__file__))+'\\temp\\'
ALLOWED_EXTENSIONS = set(['txt'])

def source_interpreter(record_raw):
    '''Prevod hrubych vystupu analyzy do zpracovatlne podoby'''
    record_interpreted = []
    if '-STAT-' in record_raw:
        record_interpreted = record_raw

    else:
        try:
            record_raw_cutted = record_raw.split('|')
            row_number = record_raw_cutted[0]
            temp = record_raw_cutted[1].split('- ')
            sent_orig = record_raw_cutted[2]
            sent_conv = record_raw_cutted[3]
            sent_lang = record_raw_cutted[4]
            methods = record_raw_cutted[5]
            hom_str = record_raw_cutted[6]
            index = temp[0]
            language = temp[1]
                
            record_interpreted.append(int(row_number))
            record_interpreted.append(index)
            record_interpreted.append(language)
            record_interpreted.append(sent_orig)
            record_interpreted.append(sent_conv)
            record_interpreted.append(sent_lang)
            record_interpreted.append(methods)
            record_interpreted.append(hom_str)

        except IndexError:
            record_interpreted.append('chybny zaznam')
            
        except UnboundLocalError:
            record_interpreted.append('chybny zaznam')
                    
    return record_interpreted

def auto_escape(string):
    return (string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\'', '&#39;').replace('\'', '&quot;'))

def table_converter(records):
    '''Prevod zkonvertovanych radku do paralelnich seznamu'''
    row_number, index, sent_lang, sent_orig, sent_conv, lang_str, methods, hom_str, languages = ([] for i in range(9))
    
    for record in records:
        if '-STAT-' in record:
            row_number.append('')
            index.append('')
            sent_lang.append('')
            sent_orig.append('')
            sent_conv.append('')
            lang_str.append('')
            methods.append('')
            hom_str.append('')
            stat_row = record.split()
            
            if 'Languages:' in stat_row:
                languages = stat_row
                languages.pop(0)
                languages.pop(0)
            
        else:
            if record[0] != 'chybny zaznam':
                row_number.append(record[0])
                index.append(record[1])
                sent_lang.append(record[2])
                hom_str.append(record[3])
                sent_orig.append(record[4])
                sent_conv.append(record[5])
                lang_str.append(record[6])
                methods.append(record[7])
                languages.append('')
            
    return row_number, index, sent_lang, sent_orig, sent_conv, lang_str, methods, hom_str, languages

def row_maker(row_number, index, sent_lang, sent_orig, sent_conv, lang_str, methods, hom_str, languages):
    '''Prevod vysledku do tabulkovych zaznamu + opatreni html tagy'''
    t1 = '<td>'
    t2 = '</td>'
    t3 = '<tr>'
    t4 = '</tr>'
    records_html = ''

    for i in range(0,len(row_number)-1):
        sent_orig_button = '<button type=\'button\' onclick=\'alert(\"'+auto_escape(sent_orig[i])+'\")\'>View</button>'
        method = methods[i].split()
        
        if method[1] == 'True':mwe_mark='&#x2714;'
        else:mwe_mark = '&#x2718'
        
        if method[2] == 'True':colls_mark='&#x2714;'
        else:colls_mark = '&#x2718'
        
        hom_str_conv = str(hom_str[i].strip('[\[\]\'\,un\\]'))
        ilhom_mark = '&#x2718'
        
        for lang in languages:
            if lang in hom_str_conv and (lang not in sent_lang[i] or 'M' in hom_str_conv):
                ilhom_mark = '&#x2714;'            
            
        sent_html = sentence_maker(sent_conv[i],lang_str[i],sent_lang,hom_str_conv)
        index_full,index_single = index_maker(index[i],sent_lang[i],languages)
        
        row_html = t3+t1+str(row_number[i])+t2+t1+'<font color=\'green\'><a href=\'#\' bubbletooltip=\''+str(index_full+'['+hom_str_conv+']')+'\'>'+str(index_single)+'</a></font>'+t2+t1+sent_lang[i]+t2+t1+sent_html+t2+t1+sent_orig_button+t2+t1+ilhom_mark+t2+t1+colls_mark+t2+t1+mwe_mark+t2+t4
        records_html = records_html+row_html
        
    return records_html

def index_maker(index,sent_lang,languages):
    '''Vypocet indexu a vygenerovani retezce do bublinoveho zaznamu'''
    index_full = ''
    index_conv = lang_str_converter(index)
    index_single = 0
    
    for i in range(len(languages)):
        if index_conv != []:
            if languages[i].strip() == sent_lang.strip():
                index_single = int(index_single)+int(index_conv[i])
            else:index_single = int(index_single)-int(index_conv[i])
            
            index_full = index_full+'['+str(index_conv[i])+' '+languages[i]+'] '
            
    if index_conv != []:
        index_full = index_full+'['+index_conv[len(languages)]+' HOM] ['+index_conv[len(languages)+1]+' ALL] '
        index_single = round(float(index_single)/float(index_conv[len(languages)+1]),4)
    
    return index_full,index_single
    
def sentence_maker(sent_conv,lang_str,sent_lang,hom_str_conv):
    '''Opatreni kadeho homografa ve vete tagem pro bublinovou napovedu'''
    words = sent_conv.split()
    hom_pos_list=[]
    sent_html = ''
    lang_str = lang_str_converter(lang_str)
    cuts = [q for q,x in enumerate(lang_str) if x == ')']
    homographs = [q for q,x in enumerate(lang_str) if x == 'HOM']
    hom_str_conv=hom_str_conv.split()
    for position in hom_str_conv:
        position=position.split(':')
        hom_pos_list.append(int(position[0]))
    lenghts = []

    for x in range(len(homographs)):
        lenghts.append(cuts[x]-homographs[x]-1)
    lang_rec_str,lang_str = cuts_recog(lang_str,homographs,lenghts,cuts)

    for i in range(len(words)):
        word = words[i]
        if 'HOM' in lang_str[i]:
            if i+1 in hom_pos_list:
                word = '<b><a href=\'#\' bubbletooltip=\''+lang_rec_str[0]+'\'>'+word+'</a></b>'
            else:
                word = '<abbr title=\''+lang_rec_str[0]+'\'>'+word+'</abbr>'
            lang_rec_str.pop(0)
            
        else:
            word = '<abbr title=\''+lang_str[i]+'\'>'+word+'</abbr>'
            
        sent_html = sent_html+word+' '
                       
    return sent_html

def cuts_recog(lang_str,homographs,lenghts,cuts):
    '''Rozpoznavani html/xml tagu ve zdrojovych vetach a jejich pripade escapovani pro zamezeni kontaminace html kodu'''
    index = 0
    lang_rec_str = []
    for i in range(len(lang_str)):
        if i in cuts:
            lang_str.pop(i-index)
            index = index+1
    homographs = [q for q,x in enumerate(lang_str) if x == 'HOM']            
    index = 0
    
    for homograph in homographs:
        languages = ''
        homograph_start = homographs.index(homograph)
        for i in range(lenghts[homograph_start]):
            languages = languages+lang_str[homograph+i-index+1]+' '
            lang_str.pop(homograph+i-index+1)
            index = index+1
        lang_rec_str.append(languages)
        
    return lang_rec_str,lang_str
        
def lang_str_converter(lang_str):
    lang_str = re.sub('[\[\]\(\,\']', ' ', lang_str)
    return lang_str.split()

def settings_maker(sent_index,mwe_index,colls_index,savefile_index,hlist_index,context):
    '''Vygenerovani kodu analyzy pro soubor LIDA dle parametru z formularu stranky'''
    if sent_index != []:
        settings = '1'
        context['slang_check']='checked'
    else:settings = '0'
    if mwe_index != []:
        settings = settings+'1'
        context['mwe_check']='checked'
    else:settings = settings+'0'
    if colls_index !=[] :
        settings = settings+'1'
        context['colls_check']='checked'
    else:settings = settings+'0'
    if savefile_index != []:
        settings = settings+'1'
        context['output_check']='checked'
    else:settings = settings+'0'
    if hlist_index != []:
        settings = settings+'1'
        context['homdict_check']='checked'
    else:settings = settings+'0'
    
    return settings,context


app = Flask(__name__, static_url_path = '')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
@app.route('/', methods=['POST', 'GET'])

def default():
    context={
        'slang_check':'checked',
        'mwe_check':'checked',
        'homset_all_check':'checked',
        'homfield_text':'placeholder=\'homograph blacklisted_hom/b\'',
        'colls_text':'placeholder=\'[homograph] \nLANG coll\\ngram\'',
        'colls_range_text':'placeholder=\'Set range\''}

    rendered_page = render_template('index.html',context=context)
    return rendered_page

def allowed_file(filename): 
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/submit', methods=['POST'])    

def submit_post():
    clear_temp()
    context={}
    input_method = 0
    settings_html=request.form

    analyze_file = request.files['file']
    analyzed_file = request.files['file2']
    hom_file = request.files['file3']
    colls_file = request.files['file4']
    
    if analyze_file.filename == '' and analyzed_file.filename == '':
        input_text = request.form['input'].split('\n')
        input_method = 1
        
    elif (analyze_file or analyzed_file) and (allowed_file(analyze_file.filename) or allowed_file(analyzed_file.filename)):
        input_method = 2
        
        if analyze_file.filename != '':
            filename = secure_filename(analyze_file.filename)
            analyze_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        elif analyzed_file.filename != '':
            filename = secure_filename(analyzed_file.filename)
            analyzed_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        file_uploaded = codecs.open(UPLOAD_FOLDER+filename,'r', encoding='utf-8', errors='ignore')
        
        input_text = file_uploaded.readlines()
        file_uploaded.close()
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'])+filename)
        
    h_mode = request.form['homset']
    h_text = request.form['homfield']
    
    if hom_file.filename == '' and h_text!=[]:h_text=h_text.split()
    elif hom_file.filename != '':
        filename = secure_filename(hom_file.filename)
        hom_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_uploaded = codecs.open(UPLOAD_FOLDER+filename,'r', encoding='utf-8', errors='ignore')
        h_text = file_uploaded.read()
        file_uploaded.close()
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'])+filename)
         
    if h_mode == 'all':
        h_mode = '0'
        context['homset_all_check']='checked'
        
    if h_mode == 'conc':
        h_mode = '1'
        context['homset_conc_check']='checked'
        
    if h_mode == 'spec':
        h_mode = '2'
        context['homset_spec_check']='checked'
    
    h_negative=settings_html.getlist('homblack')

    if h_negative != []:
        h_mode=h_mode+'1'
        context['blacklist_check']='checked'
    else:h_mode = h_mode+'0'
        
    if settings_html.getlist('1poshom')!=[]:
        h_mode=h_mode+'1'
        context['poshom_check']='checked'
    else: h_mode = h_mode+'0'
    
    if settings_html.getlist('colls') != []:
        if colls_file.filename != '':
            filename = secure_filename(colls_file.filename)
            colls_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_uploaded = codecs.open(UPLOAD_FOLDER+filename,'r', encoding='utf-8', errors='ignore')
            colls_text = file_uploaded.read()
            file_uploaded.close()
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'])+filename)
            
        else:
            colls_text = request.form['speccolls']
            context['colls_text_alt']='checked'
            
        colls_range = int(request.form['range'])
        context['colls_range']=colls_range
        
    else:
        colls_text = '-'
        colls_range = 0
    
    settings, context = settings_maker(settings_html.getlist('slang'),settings_html.getlist('mwe'),settings_html.getlist('colls'),settings_html.getlist('output'),settings_html.getlist('homdict'),context)
    languages = settings_html.getlist('lang')
    if analyze_file.filename != '' or input_method==1:
        records_raw,file_download=analysis(input_text,languages,settings,h_mode,h_text,colls_text,colls_range)

    else:
        records_raw=input_text
        file_download = filename
    
    records_interpreted = []
    
    for record_raw in records_raw:
        record_interpreted = source_interpreter(record_raw)
        records_interpreted.append(record_interpreted)

    context=set_settings(languages,context)
    
    if len(h_text)>0 and hom_file.filename == '':
        text=''
        for word in h_text:
            text=text+word+' '
        context['homfield_text_alt']=text
        
    else:context['homfield_text']='placeholder=\'homograph blacklisted_hom/b\''
    
    if len(colls_text)>0 and colls_text != '-' and colls_file.filename == '':
        context['colls_text_alt'] = colls_text
        context['colls_range_text_alt'] = colls_range
    else:
        context['colls_range_text'] = 'placeholder=\'Set range\''
        context['colls_text'] = 'placeholder=\'[homograph] \nLANG coll\\ngram\''
        
    row_number,index,sent_lang,sent_orig,sent_conv,lang_str,methods,hom_str,languages = table_converter(records_interpreted)
    rows_html = row_maker(row_number,index,sent_lang,sent_orig,sent_conv,lang_str,methods,hom_str,languages)  
    rendered_page = render_template('index.html', colls=rows_html, filename=file_download,context=context)
    
    return rendered_page

def clear_temp():
    '''Promazani slozky temp, kam se nahravaji soubory k analyze a ke stazeni, mazou se soubory starsi jednoho dne'''
    time_current = time.time()
    for doc in os.listdir(UPLOAD_FOLDER):
        doc = os.path.join(UPLOAD_FOLDER, doc)
        if os.path.getmtime(doc) < time_current - 84600:
            os.remove(doc)

def set_settings(languages,context):
    '''Zjistovani zvolenych rozeznavacich jazyku'''
    context['cz_check'] = set_lang('CZ',languages)
    context['sk_check'] = set_lang('SK',languages)
    context['pl_check'] = set_lang('PL',languages)
    context['ger_check'] = set_lang('GER',languages)
    context['en_check'] = set_lang('EN',languages)
    context['fr_check'] = set_lang('FR',languages)
    context['es_check'] = set_lang('ES',languages)
    context['cit_check'] = set_lang('IT',languages)
    context['pt_check'] = set_lang('PT',languages)
    context['ru_check'] = set_lang('RU',languages)
    context['swe_check'] = set_lang('SWE',languages)

    return context

def set_lang(lang, languages):
    if lang in languages:return 'checked'
    else: return ''

@app.route('/temp/<filename>', methods=['POST', 'GET'])

def download_file(filename):
    return send_from_directory('temp', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True)
