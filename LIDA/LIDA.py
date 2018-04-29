# -*- coding: utf-8 -*-
import re, os, random, codecs, platform, subprocess, string
from collections import Counter, defaultdict
      
def sent_convertor(sent,homograph):
    '''Tokenizace vety'''
    sent_orig = sent.replace('\n','')
    sent_orig = sent_orig.replace('\r','')
    sent_orig = sent_orig.replace('|','')
    sent_orig = sent_orig.rstrip().lstrip()
    h_string = re.sub('[\-]',' ',sent)
    h_string = re.sub('\<.*'+homograph+'.*\>','-homograph-',h_string.lower())

    if "'" in sent: sent_apos_index = True
    else: sent_apos_index = False

    sent_conv = re.sub('[…\.\,\*\<\>\%\!\?\:\-\(\)\{\}\[\]\=\/\+\`\”\“\„\“\"0123456789;´\…\×\|\»\«\■\►\“]', ' ', sent)
    h_string = re.sub('[\.\,\*\<\>\%\!\?\:\(\)\{\}\[\]\/\=\+\`\”\“\„\“\"0123456789;´\…\×\|\»\«\■\►\“]', ' ', h_string)

    allupper_list = []
    firstupper_list = []
    words_temp = sent_conv.split()
    
    for word in words_temp:
        allupper_list.append(word.isupper())
        firstupper_list.append(word.istitle())

    h_string = h_string.lower().split()
    sent_conv = sent_conv.lower()
    words = sent_conv.split()

    return words, sent_orig, h_string, allupper_list, firstupper_list, sent_apos_index

def analysis(input_text,languages,settings,h_mode,h_text,colls_text,colls_range):
    file_download = ''
    h_recognized = []                                                                                                                                                                                                                                                                   
    row_number = 0
    sent_index, mwe_index, colls_index, savefile_index, hlist_index = False, False, False, False, False
    records = []

    if settings[0] == '1':sent_index=True
    if settings[1] == '1':mwe_index=True
    if settings[2] == '1':colls_index=True
    if settings[3] == '1':savefile_index=True
    if settings[4] == '1':hlist_index=True
    
    if savefile_index == True:
        '''Vygenerovani nazvu souboru ke stazeni'''
        file_download = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(6))
        file_download = file_download+'.txt'
        file_writeable = codecs.open(os.path.dirname(os.path.abspath(__file__))+'\\temp\\'+file_download, 'w+', encoding='utf-8', errors='ignore')
        
    else:file_writeable = ''

    if h_mode[0] == '1':homograph=h_conc_recog(input_text)       
    else:homograph = '-'
        
    for sent in input_text:
        words, sent_orig, h_string, allupper_list, firstupper_list, sent_apos_index = sent_convertor(sent,homograph)    
        print row_number                  
                                           
        if words != []:
            row_number = row_number+1
            record,h_recognized = sent_analyzer(words,sent_index,mwe_index,colls_index,h_string,homograph,sent_orig,languages,h_mode,row_number,h_text,colls_text,colls_range,h_recognized,allupper_list,firstupper_list,sent_apos_index)     
            records.append(record)
    
    lastrow = '-STAT- Languages: '
    for language in languages:
        lastrow = lastrow+str(language)+' '
       
    records.append(lastrow)
    if savefile_index == True:
        for line in records:
            file_writeable.write(line)
            file_writeable.write('\n')
            
        if hlist_index == True:
            file_writeable.write('List of found homographs:\n') 
            for line in list(set(h_recognized)):
                file_writeable.write(line)
                file_writeable.write('\n')
                
        file_writeable.close()
            
    return records,file_download
        
def sent_analyzer(words,sent_index,mwe_index,colls_index,h_string,homograph,sent_orig,languages,h_mode,row_number,h_text,colls_text,colls_range,h_recognized,allupper_list,firstupper_list,sent_apos_index):
    hom_strings=[]
    methods=[]
    lang_str=[]
    homographs=[]
    sent_lang='X'
    b_list=[]
    h_temp=list(words)
    
    if h_mode[0]=='1':h_conc_position=h_positions_recognizer(words,homograph,h_string)
    h_positions=homographs
        
    i=0
    for word in words:
        recognized=wordlang_recognizer(word,sent_index,homograph,languages,h_mode,h_text,sent_apos_index)

        if (recognized=='' or recognized==[]) and sent_apos_index==True:
            if word.startswith('\'') or word.endswith('\''):
                word_en=re.sub("[\']","",word)
                if len(word)>1:
                    recognized = majka_init(word_en,languages,h_mode)
                    
                else:recgnized=[]

                b_list.append('2')
            
            else:
                word_fr=word.split('\'')
                if len(word_fr)>1:
                    for word_f in word_fr:
                        recognized_fr=majka_init(word_f,languages,h_mode)
                        if recognized_fr!=[]:
                            recognized=recognized_fr
                b_list.append('1')
                
        else:b_list.append('0')
            
        if len(recognized)==0:lang_str.append('None')

        elif len(recognized)==1:lang_str.append(recognized[0].strip("'[]"))
        else:
            hom_temp='HOM('+str(recognized)+')'
            hom_temp=hom_temp.strip(' ')
            lang_str.append(hom_temp)
            homographs.append(h_temp.index(word))
            h_temp.remove(word)
            h_temp.insert(0,'X')
            h_recognized.append(word+''+str(recognized))

        i=i+1        
           
    if words!='':
        if sent_apos_index == True:
            words_temp=[]
            for i in range(len(words)):
                if b_list[i]=='2':
                    word=re.sub("[\']","",words[i])
                    words_temp.append(word)
                else:words_temp.append(words[i])
            
            words=list(words_temp)
            
        lang_count=0
        sent_lang='X'
        for i in range(len(languages)):
            if lang_str.count(languages[i])>lang_count:
                sent_lang=languages[i].strip("'[]")
                lang_count=lang_str.count(languages[i])
      
    langs_score=[]
    kontr=0
    
    for i in range(len(languages)):
        kontr=kontr+lang_str.count(languages[i])
        langs_score.append(lang_str.count(languages[i]))
        
    kontr=len(lang_str)-kontr
    langs_score.append(kontr-lang_str.count('None'))
    langs_score.append(len(lang_str))

    if h_mode[0]=='1':h_conc_positions=h_positions_recognizer(words,homograph,h_string)   
    h_positions=homographs

    methods.append('False')

    if mwe_index==True:
        lang_str,indilang=mwe_recognizer(words,lang_str,h_positions,languages,allupper_list,firstupper_list)
        methods.append(indilang)
        
    else: methods.append('False')
    
    if colls_index==True:
        lang_str,indes=colls_recognizer(words,lang_str,h_positions,languages,colls_text,colls_range)

        if indes==1:
            methods.append('True')
        else:methods.append('False')
    else:methods.append('False')

    forindex=list(langs_score)
    forindex.pop()
    forindex.pop()
    m = max(forindex)
    indexx=[i for i, j in enumerate(forindex) if j == m]
    if len(indexx)>1:sent_lang='X'

    if sent_lang != 'X' and sent_index == True:
        lang_str=by_sentlang_recognizer(lang_str,h_positions,languages,sent_lang,langs_score)

    record=str(row_number)+' | '+str(langs_score)+' - '+str(sent_lang)+' | '

    position_mark=1
    for position in lang_str:
        index=0
        if 'HOM' in position:
            for language in languages:
                h_lang=position.split('{')
                h_lang.pop(0)
                if language in str(h_lang):
                    index=index+1
                    lang_mark=language

            if index>1:
                colls_index=0
                for language in languages:
                    if language+'/COLLS' in position:
                        colls_index=colls_index+1
                        lang_mark=language
                if colls_index>1:
                    hom_str=str(position_mark)+':M'

                else:hom_str=str(position_mark)+':'+lang_mark
                    
            elif index==0:
                hom_str=str(position_mark)+':X'
            elif index==1:
                hom_str=str(position_mark)+':'+lang_mark

            if h_mode[0]=='1':
                if position_mark!=int(h_conc_position[0]+1):
                    hom_str=''

            hom_strings.append(hom_str)
            
        position_mark=position_mark+1
        
    for hom_str in hom_strings:
        record=record+str(hom_str)+' '
    record=record+' | '

    record=record+sent_orig+' | '
    for word in words:
        record=record+word+' '

    record=record+' | '

    for position in lang_str:
        record=record+str(position)+' '
    
    record=record+' | '
    for method in methods:
        record=record+str(method)+' '
    
    return record,h_recognized

def wordlang_recognizer(word,sent_index,homograph,languages,h_mode,h_text,sent_apos_index):
    '''Konecna filtrace slov k rozeznavani'''
    recognized = majka_init(word,languages,h_mode)

    if h_mode[0] == '2':
        if word not in h_text and len(recognized)>1:recognized = ''
            
    if h_mode[1] == '1':
        if word+'/b' in h_text and len(recognized)>1:recognized = ''
       
    if h_mode[2] == '1' and len(recognized)>1 and len(word) == 1:
        recognized = ''

    return recognized
        
def colls_recognizer(words,lang_str,h_positions,languages,colls_text,colls_range):
    '''Rozezavani kolokaci'''
    colls_homographs = colls_text.split('\n')
    for i in range(len(colls_homographs)):
        colls_homographs[i] = colls_homographs[i].strip('\r\n')
        
    index = 0
    for h_position in h_positions:
        if '['+words[h_position]+']' in colls_homographs:
            for i in range(colls_homographs.index('['+words[h_position]+']'),len(colls_homographs)):
                collocation = colls_homographs[i].split()
                if  collocation!=[]:
                    if colls_homographs[i][0] == '[' and i!=colls_homographs.index('['+words[h_position]+']'):break
                    
                    if len(collocation) == 2:
                        for x in range(1,colls_range+1):
                            try:
                                if collocation[1] == words[h_position-x]: 
                                    lang_str[h_position] = lang_str[h_position][:-2]+", '{"+str(collocation[0])+'/COLLS-'+str(x)+'}\'])'
                                    index = 1
                                   
                                if collocation[1] == words[h_position+x]:
                                    lang_str[h_position] = lang_str[h_position][:-2]+", '{"+str(collocation[0])+'/COLLS+'+str(x)+'}\'])'
                                    index = 1
                            except IndexError:
                                nic = 0
                            
                    elif len(collocation)>2:
                        lang = collocation[0]
                        collocation.pop(0)
                        ngram = ' '.join(collocation)
                        recovered = ' '.join(words)
                        if ngram in recovered:
                            lang_str[h_position] = lang_str[h_position][:-2]+", '{"+str(lang)+'/NGRAM}\'])'
                            index = 1
  
    return lang_str, index    
                        
def mwe_recognizer(words,lang_str,h_positions,languages,allupper_list,firstupper_list):
    '''Rozeznavani MWE - cela metoda se kvli moznemu zretezeni rozeznanych hom. opakuej vicekrat.'''
    lang_str_editable = list(lang_str)
    lang_str_temp = []
    indilang = 'False'
        
    for cycle in range(5):
        for h_position in h_positions:
            indexes = []
            limits = []
               
            for language in languages:                    
                index = 0
                if lang_str_temp == []:lang_str_temp = list(lang_str_editable)

                if lang_str_editable[h_position].find(language+'/MWE') != -1:
                        lang_str_temp[h_position] = language
                        
                lang_list = []
                pos_count = 0

                index, pos_count = mwe_recognizer_stage(h_position, language, lang_str_temp, allupper_list, firstupper_list, index, pos_count, -3, 0.25)
                index, pos_count = mwe_recognizer_stage(h_position, language, lang_str_temp, allupper_list, firstupper_list, index, pos_count, -2, 0.5)
                index, pos_count = mwe_recognizer_stage(h_position, language, lang_str_temp, allupper_list, firstupper_list, index, pos_count, -1, 1)
                index, pos_count = mwe_recognizer_stage(h_position, language, lang_str_temp, allupper_list, firstupper_list, index, pos_count, 1, 1)
                index, pos_count = mwe_recognizer_stage(h_position, language, lang_str_temp, allupper_list, firstupper_list, index, pos_count, 2, 0.5)
                index, pos_count = mwe_recognizer_stage(h_position, language, lang_str_temp, allupper_list, firstupper_list, index, pos_count, 3, 0.25)
                            

                if pos_count == 6:limit = 2
                elif pos_count == 5:limit = 1.75
                elif pos_count == 4:limit = 1.5
                elif pos_count == 3:limit = 1.25
                else:limit = 10
   
                if index >= limit:
                    limits.append(limit)
                    indexes.append(index)
                           
                else:
                    indexes.append(0)
                    limits.append(10)
         
            D = defaultdict(list)
            for i,item in enumerate(indexes):
                D[item].append(i)
            D = {k:v for k,v in D.items() if len(v)>1}
            
            for index in indexes:
                if index >= limits[indexes.index(index)] and lang_str_editable[h_position].find(languages[indexes.index(index)]) != -1 and (D=={} or str(D)[1] == '0') and indexes.index(max(indexes)) == indexes.index(index):
                    lang_str_editable[h_position] = lang_str[h_position][:-2]+", '{"+str(languages[indexes.index(index)])+'/MWE}\'])'
                    indilang = 'True'
                                                  
    return lang_str_editable,indilang

def mwe_recognizer_stage(h_position, language, temphom, allupper_list, firstupper_list, index, pos_count, position_relative, weight):
    '''Vypocet skore pro MWE dle pridelenych vah'''
    try:
        if h_position+position_relative > -1:
            if language == temphom[h_position+position_relative]:
                index = index+weight
                if len(set(allupper_list)) != 1 and allupper_list[h_position] == True and allupper_list[h_position+position_relative] == True: index = index+weight+weight
                else:
                    if len(set(firstupper_list)) !=1 and firstupper_list[h_position] == True and firstupper_list[h_position+position_relative] == True: index = index+weight+weight
            else:
                if len(set(allupper_list))!=1 and allupper_list[h_position] == True and allupper_list[h_position+position_relative] == True and temphom[h_position] == None: index = index+weight
                else:
                    if len(set(firstupper_list)) != 1 and firstupper_list[h_position] == True and firstupper_list[h_position+position_relative] == True and temphom[h_position] == None: index = index+weight
            pos_count = pos_count+1
  
    except IndexError: index_err = True
    except ValueError: index_err = True
    
    return index, pos_count

def by_sentlang_recognizer(lang_str,h_positions,languages,sent_lang,index):
    for h_position in h_positions:
        if lang_str[h_position].find('/MWE')==-1 and lang_str[h_position].find('/COLLS')==-1 and lang_str[h_position].find('/NGRAM')==-1:          
            if lang_str[h_position].find(sent_lang) != -1 :lang_str[h_position]=lang_str[h_position][:-2]+", '{"+str(sent_lang)+'/SNT}\'])'
            
    return lang_str

def h_positions_recognizer(words,homograph,h_string):
    '''Urcovani pozic homograf ve vete'''
    h_found=[]
    bracket_count=0
    for word in h_string:
        if '-homograph-' in word:
            bracket_count=bracket_count+1
    
    if bracket_count>1:
        bracket_replaced=0
        for i in range(words):
            if words[i-bracket_replaced]==homograph and (i-bracket_replaced)==h_string.index('-homograph-'):
                h_found.append(h_string.index('-homograph-'))
                return h_found

            elif words[i-bracket_replaced]==homograph and (i-bracket_replaced)!=h_string.index('-homograph-'):
                h_string.remove('-homograph-')
                bracket_replaced=bracket_replaced+1                          

    elif bracket_count==1:
        for word in h_string:
            if '-homograph-' in word:
                h_found.append(h_string.index(word))
        return h_found

    else:
        h_found.append(0)
        return h_found

def h_conc_recog(input_text):
    '''Urcovani analyzovaneho homografa v konkordancich souborech'''
    homographs=[]
    for x in range(0,len(input_text)):
        homograph = re.findall('\<.*\>',input_text[x])
        if homograph != []:
            homograph_orig=re.sub('[\<\/\>]',' ',homograph[0])
            homograph_splitted=homograph_orig.split()
            homograph_conv=homograph_splitted[0].strip()
            homographs.append(homograph_conv)

    homographs_counted = Counter(homographs)
    return homographs_counted.most_common(1)[0][0].lower()

'''Posledni tri metody se staraji o inicializaci analyzatoru Majka z prilozenych spustitelnych souboru a slovniku
V tomto bode se bude implementace nastroje na webu FI MUNI castecne lisit'''

def majka_init(word,languages,h_mode):
    mark=platform.system()
    if mark == 'Windows':path=os.path.join(os.path.dirname(__file__),'majka.exe -f ')
    elif mark == 'Linux':path=os.path.join(os.path.dirname(__file__),'majka32 -f ')
    word_enc=''
    if mark == 'Windows':
        try:word_enc=unicode(word).encode('cp1250')
        except UnicodeEncodeError:word_enc=unicode(word).encode('utf-8')
        
    elif mark == 'Linux':                                    
        try:word_enc=unicode(word).encode('utf-8')
        except UnicodeEncodeError:word_enc=unicode(word).encode('cp1250')
    
    recognized = []    
    if word_enc[:3] != 'naj':
        for language in languages:
            recognized = majka_setup(word_enc,language,recognized,path)
        
    return recognized

def majka_setup(word_enc,language,recognized,path):
    if language == 'CZ':filename = os.path.join(os.path.dirname(__file__),'majka.w-lt')
    else:filename = filename = os.path.join(os.path.dirname(__file__),'w-lt.'+language.lower()+'.fsa')
    wlt_dict = path+filename
    language_det = majka_call(word_enc,wlt_dict)
    if language_det != '': recognized.append(str(language))
    return recognized

def majka_call(word_enc,wlt_dict):
    init = subprocess.Popen(wlt_dict,stdin=subprocess.PIPE, stdout=subprocess.PIPE,shell=True)
    answer = init.communicate(input=word_enc)[0]
    return answer
