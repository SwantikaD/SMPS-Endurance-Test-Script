import pyvisa
import time
import csv
from datetime import datetime
import msvcrt
import sys

def datalog(logFile,time_on_off):

	for i in range(int(time_on_off)):

		try:
			volt = float(inst1.query('MEAS:VOLT?', delay = 0.1)) #0.1s delay between query write and read
		except Exception as e:
			print(e)
			print(datetime.now(),'Resend Vout query...')
			try:
				volt = float(inst1.query('MEAS?', delay = 0.1)) #0.1s delay between query write and read
			except Exception as e:
				print(e)
				print(datetime.now(),'Still no response from PSU...')
				volt = -1.0

		time.sleep(0.05)

		try:
			curr = float(inst1.query('MEAS:CURR?', delay = 0.1)) #0.1s delay between query write and read
		except Exception as e:
			print(e)
			print(datetime.now(),'Resend Iout query...')
			try:
				curr = float(inst1.query('MEAS:CURR?', delay = 0.1)) #0.1s delay between query write and read
			except Exception as e:
				print(e)
				print(datetime.now(),'Still no response from PSU...')
				curr = -1.0

		time.sleep(0.05)

		ts = datetime.now()
		ts_trunc = ts.replace(microsecond=0)
		#sno = i+1

		#Print to console
		#print(ts_trunc, volt, curr)

		#write to csv file
		info = {'Timestamp': ts_trunc , 'Voltage': volt, 'Current': curr}
		with open('C:\\Data\\'+logFile, 'a', newline='') as csv_file:
			csv_writer = csv.DictWriter(csv_file, fieldnames)
			csv_writer.writerow(info)

		#wait 0.7 sec
		time.sleep(0.7)


def query_400V():

    try:
        reply = int(inst1.query('OUTP?'))
    except Exception as e:
        print(e)
        print(datetime.now(), 'Resend query to 400V PSU...')
        try:
            reply = int(inst1.query('OUTP?'))
        except Exception as e:
            print(e)
            print(datetime.now(), 'Still no response from 400V PSU...')
            reply = -1
    finally:
        if reply == 1:
            print('400V is on...')
        elif reply == 0:
            print('400V is off...')
        else:
            print('400V PSU reply to query is: ' + str(reply))
        
    return reply    
                              

def query_34970A(ch_list):
    reply = []

    # three retries
    for attempt in range(3):
        try:
            answer = inst2.query(':ROUTe:OPEN? (%s)' % ch_list)
            reply = list(answer.split(","))
            print(reply)
        except Exception as e:
            print(e)
            if attempt == 2:
                print(datetime.now(), '34970A not responding...')
            else:
                print(datetime.now(), 'Resend query to 34970A...')
                time.sleep(2)
                continue
        else:
            ch_start = int(ch_list[3])
            ch_end = int(ch_list[7])

            if ch_list[4] == ':':
                for i in range (len(reply)):
                    if reply[i] == '1':
                        print('Channel ' + str(ch_start + i) + ' open...')
                    elif reply[i] == '0':
                        print('Channel ' + str(ch_start + i) + ' close...')
                    else:
                        reply[i] = 'x'
                        print('Channel ' + str(ch_start + i) + ' assigned value: ' + reply[i])

            if ch_list[4] == ',':
                for i in range (2):
                    if i == 0:
                        if reply[i] == '1':
                            print('Channel ' + str(ch_start) + ' open...')
                        elif reply[i] == '0':
                            print('Channel ' + str(ch_start) + ' close...')
                        else:
                            reply[i] = 'x'
                            print('34970A reply to channel ' + str(ch_start)+ ' assigned value: ' + reply[i])
                    else:
                        if reply[i] == '1':
                            print('Channel ' + str(ch_end) + ' open...')
                        elif reply[i] == '0':
                            print('Channel ' + str(ch_end) + ' close...')
                        else:
                            reply[i] = 'x'
                            print('34970A reply to channel ' + str(ch_end)+ ' assigned value: ' + reply[i])

            break
    
    return reply


#Generate csv filename
now = datetime.now()
now_str = now.strftime('%Y-%m-%d_%H-%M-%S')
csv_filename = 'SorensonPSU-{}.csv'.format(now_str)
print(csv_filename)

#Create data log file with headers
fieldnames = ['Timestamp','Voltage','Current']
with open('C:\\Data\\' + csv_filename, 'w', newline='') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames)
    csv_writer.writeheader()

print('Data log file created....\n')

#Get user inputs: V_set, I_set, t_on, t_off
v_set = input('Enter voltage setting in volts: ')
i_set = input('Enter current setting in amps: ')
t_on = input('Enter 400V on time in sec: ')
t_off = input('Enter 400V off time in sec: ')

#List visa resources
print('\nConnecting to instrument....')
rm = pyvisa.ResourceManager()
print('List of visa resources')
print(rm.list_resources())
inst1 = rm.open_resource('ASRL4::INSTR')
inst2 = rm.open_resource('GPIB0::10::INSTR')

#configure measurement instrument
inst1.read_termination = '\r'
inst1.write_termination = '\r'
inst1.timeout = 5000

inst2.read_termination = '\n'
inst2.write_termination = '\n'
inst2.timeout = 5000 

hvStatus = 0

#check communication with both instruments        
try:
    string = inst1.query('*IDN?')
    print(string)
except Exception as e:
    print(e)
    print("Couldn't connect to instrument. Run program again...")
    #exit program
    sys.exit(1)
else:
    print ('400V PSU connection successful....\n')

    #Turn off power supply at start
    inst1_status = query_400V()
    if inst1_status == '1':
        inst1.write('OUTP OFF')
        time.sleep(0.1)
        print('Instrument output was on. Now turned: ' + query_400V())
    elif inst1_status == '0':
        print('400V PSU is off.')

    #Write settings input by user
    print('Writing voltage and current settings to the instrument...')
    inst1.write('VSET ' + v_set)
    time.sleep(0.1)
    inst1.write('ISET ' + i_set)
    time.sleep(0.1)
    print('Voltage setting readback: ' + inst1.query('VSET?'))
    print('Current setting readback: ' + inst1.query('ISET?'))
    print('400V PSU is ready...\n')
                    
try:
    string = inst2.query('*IDN?')
    print(string)
except Exception as e:
    print(e)
    print("Couldn't connect to instrument. Run program again...")
    sys.exit(1)
else:
    print ('34970A connection successful....\n')
    
    inst2.write(':ROUTe:OPEN (%s)' % '@101:106')
    chStatus = query_34970A('@101:106')
    time.sleep(0.1)

    #check if all channels have status 1
    if (all(element == '1' for element in chStatus)): 
        print('34970A is ready...')
    else:
        #exit program
        sys.exit(1)
    
print('\nTest sequence started. Press ctrl+C to stop....')
                                
try:
    while True:
        #Turn on 400V
        inst1.write('OUTP ON')
        time.sleep(0.1)
        hvStatus = query_400V()
        if hvStatus != 1:
             raise Exception('400V did not turn on')
        print('FC charging...\n')
        time.sleep(1)

        #Turn on pri and sec loads
        inst2.write(':ROUTe:CLOSe (%s)' % '@101,104') 
        chStatus = query_34970A('@101,104')
        time.sleep(0.1)
        if len(chStatus) == 0:
            print('No response from 34970A...')
        if len(chStatus) == 2:
            if chStatus[0] != '0':
                 raise Exception('channel 101 did not close')
            if chStatus[1] != '0':
                 raise Exception('channel 104 did not close')

        time.sleep(1)

        inst2.write(':ROUTe:CLOSe (%s)' % '@102,105') 
        chStatus = query_34970A('@102,105')
        time.sleep(0.1)
        if len(chStatus) == 0:
            print('No response from 34970A...')
        if len(chStatus) == 2:
            if chStatus[0] != '0':
                 raise Exception('channel 102 did not close')
            if chStatus[1] != '0':
                 raise Exception('channel 105 did not close')

        #log data
        datalog(csv_filename, t_on)

        #Turn off pri and sec loads and turn on FC load
        inst2.write(':ROUTe:CLOSe (%s)' % '@102,105') 
        chStatus = query_34970A('@102,105')
        time.sleep(0.1)
        if len(chStatus) == 0:
            print('No response from 34970A...')
        if len(chStatus) == 2:
            if chStatus[0] != '1':
                 raise Exception('channel 102 did not open')
            if chStatus[1] != '1':
                 raise Exception('channel 105 did not open')

        time.sleep(1)

        inst2.write(':ROUTe:CLOSe (%s)' % '@101,104') 
        chStatus = query_34970A('@101,104')
        time.sleep(0.1)
        if len(chStatus) == 0:
            print('No response from 34970A...')
        if len(chStatus) == 2:
            if chStatus[0] != '1':
                 raise Exception('channel 101 did not open')
            if chStatus[1] != '1':
                 raise Exception('channel 104 did not open')

        time.sleep(1)

        #Turn on FC load
        inst2.write(':ROUTe:CLOSe (%s)' % '@103,106') 
        chStatus = query_34970A('@103,106')
        time.sleep(0.1)
        if len(chStatus) == 0:
            print('No response from 34970A...')
        if len(chStatus) == 2:
            if chStatus[0] != '0':
                 raise Exception('channel 103 did not close')
            if chStatus[1] != '0':
                 raise Exception('channel 106 did not close')

        time.sleep(1)

        #Turn off 400V
        inst1.write('OUTP OFF')
        time.sleep(0.1)
        hvStatus = query_400V()
        if hvStatus != 0:
            raise Exception('400V did not turn off')
        print('FC discharging...\n')

        #log data
        datalog(csv_filename, t_off)

        #Turn off FC load
        inst2.write(':ROUTe:CLOSe (%s)' % '@103,106') 
        chStatus = query_34970A('@103,106')
        time.sleep(0.1)
        if len(chStatus) == 0:
            print('No response from 34970A...')
        if len(chStatus) == 2:
            if chStatus[0] != '1':
                 raise Exception('channel 103 did not open')
            if chStatus[1] != '1':
                 raise Exception('channel 106 did not open')

        time.sleep(1)
                            
except (KeyboardInterrupt, Exception) as e:
    print(e)
    inst2.write(':ROUTe:OPEN (%s)' % '@101:106')
    time.sleep(0.1)
    inst1.write('OUTP OFF')
    time.sleep(0.1)
    inst1.close()
    inst2.close()
    rm.close()
    print('Program complete....')
    k = input('Press any key to close the console window...')
    
# except Exception as e:
#     print(e)
#     inst2.write(':ROUTe:OPEN (%s)' % '@101:103')
#     inst1.close()
#     inst2.close()
#     rm.close()
#     print('Program complete....')
#     k = input('Press any key to close the console window...')

