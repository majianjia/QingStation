import paho.mqtt.client as mqtt
import threading
from multiprocessing import Queue
import numpy as np
import hashlib
import argparse
from datetime import datetime


INITIAL_PACK= bytes([1]) # stupid python conversion
DATA_PACK   = bytes([2])
ACK_PACK    = bytes([3])
CLOSE_PACK  = bytes([4])

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("ota_upstream")
    # send initial message
    data = bytearray(INITIAL_PACK)
    data2 = bytearray("101,{},256,".format(len(fw_bin)).encode("ascii"))
    data3 = bytearray(m.hexdigest().encode("ascii"))
    client.publish("ota_downstream", data+data2+data3, 2)

def on_message(client, userdata, msg):
    #print(msg.topic + " " + str(msg.payload))
    ack_msg = msg.payload.decode("ascii")
    recv_msg_queue.put(ack_msg)

parser = argparse.ArgumentParser(description="send fw to qing station")
parser.add_argument('--bin', type=str, help='binary file path', default="rtthread.bin")
parser.add_argument('--uri', type=str, default='qbe26b46.en.emqx.cloud', help='uri of the mqtt broker')
parser.add_argument('--port', type=int, default=11523, help='port of the mqtt')
parser.add_argument('--username', type=str, default='ota', help='username of mqtt broker')
parser.add_argument('--password', type=str, default='123', help='password of mqtt broker')
args = parser.parse_args()

file = args.bin
uri = args.uri
port = args.port
usr = args.username
pwd = args.password

f_fw = open(file, 'rb')
fw_bin = f_fw.read()
m = hashlib.md5()
m.update(fw_bin)
print("firmware size:", len(fw_bin), "MD5:", m.hexdigest())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(usr, pwd)
client.connect(uri, port, 60)

recv_msg_queue = Queue(1)
def recv_message():
    fw_bin_idx = -256
    t_start = datetime.now()
    byte_sent = 0
    while True:
        ack_msg = recv_msg_queue.get()
        ack = ack_msg.split(',')
        if(len(ack) != 2):
            continue
        if(ack[1] in 'true'):
            fw_bin_idx += 256
            if (fw_bin_idx >= len(fw_bin)):
                break
        else:
            print("\n Package %s validation fail, resending".format(ack[0]))

        if(fw_bin_idx <0):
            continue
        size = 256 if fw_bin_idx + 256 < len(fw_bin) else len(fw_bin) - fw_bin_idx
        block = fw_bin[fw_bin_idx:fw_bin_idx+ size]
        id = int(fw_bin_idx / 256)

        packtype = bytearray(DATA_PACK)
        packid = bytearray(2)
        packid[0] = int(id % 256)
        packid[1] = int(id / 256)
        sz = bytearray(2)
        sz[0] = int(size % 256)
        sz[1] = int(size / 256)

        pack = packtype + packid + sz + block
        def checksum(data):
            sum = np.zeros(1).astype(np.uint16)
            for i in range(len(data)):
                sum += data[i]
            return sum
        sum = checksum(pack)
        cs = bytearray(2)
        cs[0] = int(sum % 256)
        cs[1] = int(sum / 256)

        client.publish("ota_downstream", pack + cs, 2)
        byte_sent += size
        speed = round(byte_sent/(datetime.now()-t_start).total_seconds())
        print("\rsending update,", fw_bin_idx, "of", len(fw_bin),"bytes finished,",
              str(speed), "Bytes/sec",
              str(np.round(fw_bin_idx*100/len(fw_bin),1))+"% done", end='', flush=True)

    packtype = bytearray(CLOSE_PACK)
    client.publish("ota_downstream", packtype, 2)
    print("\nFirmware upload finished, device rebooting")
    client.disconnect()


t = threading.Thread(target=recv_message)
t.start()
client.loop_forever()
