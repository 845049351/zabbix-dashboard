#-*- coding: utf-8 -*-
#encoding:utf-8
#!/usr/local/python
###############################
# data:2015-03-02
# writer:shanks
# �����Ϲ���dns�����ã�Ȼ���뵽tea.internetdns��
###############################
import MySQLdb,commands
import sys,os

#�����Լ���tea��
teadb_host='devopdb.idc5';
teadb_user='tea';
teadb_password='teaniubi123';
teadb_name='tea';
teadb_port=3306;

#�Ȱ�slave.dangdang.com.zone��10.4.2.43��ק������
def get_zonefile():
    get_zone=commands.getoutput('/usr/bin/rsync -av root@10.4.2.43:/var/named/chroot/etc/slave.dangdang.com.zone /usr/local/src/10.4.2.43_slave.dangdang.com.zone')
    #���zone�ļ��Ƿ����سɹ�
    if os.path.exists('/usr/local/src/10.4.2.43_slave.dangdang.com.zone'):
        print 'zone file get success'
    else:
        print '/usr/local/src/10.4.2.43_slave.dangdang.com.zone not found!'
        sys.exit(1)

#��zonefile��������֮�����
def fenxizonefile():
    #�Ƚ�Ĭ�ϵ�zone�����ļ���ʽ����ת�������µ��ļ�
    redo_zoneconf=commands.getoutput('/bin/egrep -v \';|NS|SOA|\)|TXT|MX\' /usr/local/src/10.4.2.43_slave.dangdang.com.zone|awk \'BEGIN{a=".";OFS="\t"}/\$ORIGIN/{a=$2}{if (a != "." && $3 != ""){$1=$1"."a;print $0;b=$1} else if (a != "." && $1 !~ "\$ORIGIN" ) {print b,$1,$2,$3} else {print $0}}\'|grep -v \'\$ORIGIN\' > /usr/local/src/internet_dns_zone.txt')
    #�Ҳ������Ų���д�������ø����������������ļ�������һ����������insert��sql
    mk_sqlfile=commands.getoutput('/bin/awk \'{print "insert into internetdns_records value(\\"\\",\\""$1"\\",\\""$2"\\",\\""$3"\\");"}\' /usr/local/src/internet_dns_zone.txt > /usr/local/src/internet_dns.sql')

def truncate_internetdns_records():
    #����ǰ�����
    teadbconn = MySQLdb.connect(host=teadb_host,user=teadb_user,db=teadb_name,passwd=teadb_password,port=teadb_port,charset="utf8")
    teacursor = teadbconn.cursor()
    tea_truncate_sql="truncate internetdns_records";
    try:
        teacursor.execute(tea_truncate_sql)
        teadbconn.commit()
    except:
        teadbconn.rollback()
    teadbconn.close()

#�ļ���Ū���ˣ����ڸø��µ�tea.internetdns_records��
def insert_tea():
    #teadbconn = MySQLdb.connect(host=teadb_host,user=teadb_user,db=teadb_name,passwd=teadb_password,port=teadb_port,charset="utf8")
    #teacursor = teadbconn.cursor()
    #tea_insert_sql="source /usr/local/src/internet_dns.sql";
    #try:
    #    teacursor.execute(tea_insert_sql)
    #    teadbconn.commit()
    #except MySQLdb.Error,e:
    #    print 'Mysql Error %d: %s' % (e.args[0], e.args[1])
    #teadbconn.close()
    source_sql=commands.getoutput('/usr/bin/mysql -u'+teadb_user+' -p'+teadb_password+' -h'+teadb_host+' '+teadb_name+' -e "source /usr/local/src/internet_dns.sql"')
	
def _main_():
    get_zonefile()
    fenxizonefile()
    #����ǰ�����
    truncate_internetdns_records()
    insert_tea()
    #ɾ�������ļ�
    commands.getoutput('/bin/rm -rf /usr/local/src/internet_dns.sql /usr/local/src/internet_dns_zone.txt /usr/local/src/10.4.2.43_slave.dangdang.com.zone')

_main_()