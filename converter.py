import os
import datetime
import sys
import re

if len(sys.argv) < 7:
    print('Usage: <process_count> <pcap_dir> <flows_output_dir> <csv_output_dir> <YYYY/MM/DD> <YYYY/MM/DD> --process --convert --bidirectional')
    exit(-1)
elif len(sys.argv) > 7 and sys.argv[7] != '--process' and sys.argv[7] != '--convert' and sys.argv[7] != '--bidirectional':
    print("Error! Wrong argument: " + str(sys.argv[7]))
    exit(-1)
elif len(sys.argv) > 8 and sys.argv[8] != '--process' and sys.argv[8] != '--convert' and sys.argv[8] != '--bidirectional':
    print("Error! Wrong argument: " + str(sys.argv[8]))
    exit(-1)
elif len(sys.argv) > 9 and sys.argv[9] != '--process' and sys.argv[9] != '--convert' and sys.argv[9] != '--bidirectional':
    print("Error! Wrong argument: " + str(sys.argv[9]))
    exit(-1)
elif len(sys.argv) > 10:
    print("Error! Too much arguments!")
    exit(-1)

process_cnt = str(sys.argv[1])
pcap_dir = str(sys.argv[2])
flows_output_dir = str(sys.argv[3])
csv_output_dir = str(sys.argv[4])

temp = re.findall(r'\d+', sys.argv[5])
res = list(map(int, temp))


begin_date = datetime.date(res[0], res[1], res[2])

temp = re.findall(r'\d+', sys.argv[6])
res = list(map(int, temp))

end_date =  datetime.date(res[0], res[1], res[2])

os.system("mkdir -p " + csv_output_dir)
os.system("mkdir -p " + flows_output_dir)

if (len(sys.argv) > 7 and sys.argv[7] == '--process') or (len(sys.argv) > 8 and sys.argv[8] == '--process') or (len(sys.argv) > 9 and sys.argv[9] == '--process'):
    os.system('rm -f ' + flows_output_dir + '*')
    left = begin_date - datetime.timedelta(days=1)
    right = end_date + datetime.timedelta(days=2)

    left_str = left.strftime("'%Y-%m-%d %H:%M'")
    right_str = right.strftime("'%Y-%m-%d %H:%M'")

    first_part = "sudo TZ=Europe/Moscow find " + pcap_dir + " -type f -newermt " + left_str + " ! -newermt " + right_str
    second_part = "xargs -d'\n' -P" + str(process_cnt) + " -I% nfpcapd -e 120,30 -z -t 60s -T +10,+11 -r % -B 10000000 -l " + flows_output_dir

    os.system(first_part + " | " + second_part)

if (len(sys.argv) > 7 and sys.argv[7] == '--bidirectional') or (len(sys.argv) > 8 and sys.argv[8] == '--bidirectional') or (len(sys.argv) > 9 and sys.argv[9] == '--bidirectional'):
    is_bidirectional = True
else:
    is_bidirectional = False

if (len(sys.argv) > 7 and sys.argv[7] == '--convert') or (len(sys.argv) > 8 and sys.argv[8] == '--convert') or (len(sys.argv) > 9 and sys.argv[9] == '--convert'):
    cur_time = begin_date

    while True:
        cur_date = cur_time.strftime("%Y/%m/%d")
        cur_date_filename = cur_time.strftime("%Y-%m-%d")

        os.system('echo "tstart,tsstart,tend,tsend,duration,prot,sip,sport,dip,dport,flags,pkts,bytes,flows,bps,pps,bpp,dir" > ' + csv_output_dir + cur_date_filename + '.csv')
        os.system('nfdump -R ' + flows_output_dir + ' -q ' + ('-B' if is_bidirectional else '') + ' -N -t ' + cur_date + '.00:00:00-' + cur_date + '.23:59:59 -o csv -O tend -o fmt:%ts,%tsr,%te,%ter,%td,%pr,%sa,%sp,%da,%dp,%flg,%pkt,%byt,%fl,%bps,%pps,%bpp,%dir >> ' + csv_output_dir + cur_date_filename + '.csv')

        if cur_time == end_date:
            break
        else:
            cur_time = cur_time + datetime.timedelta(days=1)