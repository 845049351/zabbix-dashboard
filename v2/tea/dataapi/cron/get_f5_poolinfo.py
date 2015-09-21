#-*- coding: utf-8 -*-
#encoding:utf-8
#!/usr/local/python
###############################
# data:2015-2-28
# writer:shanks
# ץȡF5-pool����Ϣ��¼��tea.f5poolinfo��
###############################
import commands,os,sys,MySQLdb

#����url
poolurl='http://10.64.4.141:8000/vsinfo/ttpp.txt'
snaturl='http://10.64.4.141:8000/vsinfo/tts.txt'
vsurl='http://10.64.4.141:8000/vsinfo/ttv.txt'
#�����Լ���tea��
teadb_host='devopdb.idc5';
teadb_user='tea';
teadb_password='teaniubi123';
teadb_name='tea';
teadb_port=3306;

def _geturlfile_():
    #������url�ļ����ص�����
    get_poolurl=commands.getoutput('/usr/bin/wget -q -O /usr/local/src/ttpp.txt '+poolurl)
    get_snaturl=commands.getoutput('/usr/bin/wget -q -O /usr/local/src/tts.txt '+snaturl)
    get_vsurl=commands.getoutput('/usr/bin/wget -q -O /usr/local/src/ttv.txt '+vsurl)
    #�ж������ļ��Ƿ����سɹ�
    if os.path.exists('/usr/local/src/ttpp.txt'):
        if os.path.exists('/usr/local/src/tts.txt'):
            if os.path.exists('/usr/local/src/ttv.txt'):
                print 'three urlfile wget success.'
            else:
                print '/usr/local/src/ttv.txt not found!'
                sys.exit(1)
        else:
            print '/usr/local/src/tts.txt not found!'
            sys.exit(1)
    else:
        print '/usr/local/src/ttpp.txt not found!'
        sys.exit(1)

def truncate_f5poolinfo():
#���tea.f5poolinfo��
    teadbconn = MySQLdb.connect(host=teadb_host,user=teadb_user,db=teadb_name,passwd=teadb_password,port=teadb_port,charset="utf8")
    teacursor = teadbconn.cursor()
    tea_truncate_sql="truncate f5poolinfo";
    try:
        teacursor.execute(tea_truncate_sql)
        teadbconn.commit()
    except:
        teadbconn.rollback()
    teadbconn.close()
		
#�����ļ������뵽tea.f5poolinfo��		
def _fenxifile_():
    #����ǰ�����
    truncate_f5poolinfo()
    #�ȸ���ttv.txt����������ÿ��F5�����࣬Ȼ���õ�pool�����ֺ�vip:vport
    f5_list=commands.getoutput('awk \'{ if (!seen[$1]++ && $1!="") { printf $1","; } }\' /usr/local/src/ttv.txt|sed \'s/,$//g\'')
    for f5 in f5_list.split(','):
        ttv_info=commands.getoutput('awk -vf5='+f5+' \'{if ($1==f5) {printf $4" "$6" "$8" "$11","}}\' /usr/local/src/ttv.txt |sed \'s/,$//g\'')
        for ttv in ttv_info.split(','):
            pool_name=commands.getoutput('echo '+ttv+'|awk \'{print $1}\'')
            pool_vipvport=commands.getoutput('echo '+ttv+'|awk \'{print $2}\'')
            pool_vs_name=commands.getoutput('echo '+ttv+'|awk \'{print $3}\'')
            #����pool_vs_name��ȥttpp.txt��ȡvs�б�
            pool_vs_list=commands.getoutput('awk -vf5='+f5+' -vpoolvsname='+pool_vs_name+' \'{if ($1==f5 && $4==poolvsname) {print $5}}\' /usr/local/src/ttpp.txt')
            pool_snat_name=commands.getoutput('echo '+ttv+'|awk \'{print $4}\'')
            #����pool_snat_name��ȥtts.txt��ȡsnat�б�
            pool_snat_list=commands.getoutput('awk -vf5='+f5+' -vpoolsnatname='+pool_snat_name+' \'{if ($1==f5 && $4==poolsnatname) {print $5}}\' /usr/local/src/tts.txt')
            #��f5��pool_name��pool_vipvport��pool_vs_list��pool_snat_list insert��tea.f5poolinfo��
            teadbconn = MySQLdb.connect(host=teadb_host,user=teadb_user,db=teadb_name,passwd=teadb_password,port=teadb_port,charset="utf8")
            teacursor = teadbconn.cursor()
            tea_insert_sql="insert into f5poolinfo value ('"+f5+"','"+pool_name+"','"+pool_vipvport+"','"+pool_vs_list.replace(',','<br>')+"','"+pool_snat_list.replace(',','<br>')+"','')"
            try:
                teacursor.execute(tea_insert_sql)
                teadbconn.commit()
            except:
                teadbconn.rollback()
            teadbconn.close()
		
def _main_():		
    _geturlfile_()
    _fenxifile_()
    #ɾ������url�ļ�
    rm_urlfile=commands.getoutput('/bin/rm -rf /usr/local/src/ttpp.txt /usr/local/src/tts.txt /usr/local/src/ttv.txt')
	
_main_()