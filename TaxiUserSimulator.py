import datetime
import json
import random
import math
import time
import boto3
import sched

taxis = json.load(open('config/taxis.json'))
users = json.load(open('config/users.json'))

# Time Interval of taxis and users in seconds
TAXIS_TIME_INTERVAL = 1
USERS_TIME_INTERVAL = 5

######################
#KINESIS RESOURCE INFO
######################

KINESIS_DATA_STREAM = "locationingestionstream"

kinesis_handle =boto3.client('kinesis', region_name="us-east-1")


################

# Determine the co-ordinates of the user/taxi for the next time instant based on
# random angle with x-axis(direction) and distance
def getNextCoOrdinates(x,y,location_of):
    global angle
    global distance
    while True:
        if(location_of=="Taxi"):
            angle = random.uniform(0, math.pi / 2)
            distance = random.uniform(12,30)
        if(location_of=="user"):
            angle = random.uniform(0, 2*math.pi)
            distance = random.uniform(0,6)
        distance_x = distance*math.cos(angle)
        distance_y = distance*math.sin(angle)
        new_x = x + distance_x
        new_y = y + distance_y
        if(new_x in range(50,350) and new_y in range(50,250)):
            return (new_x, new_y)

def publishNextTaxiLocation(loopCount1):
    # message = {}
    # timestamp = str(datetime.datetime.now())
    # message['timestamp'] = timestamp
    # message['locationof'] =
    taxi_count = 0

    while(taxi_count<=len(taxis)):
        taxi_coordinates = getNextCoOrdinates(taxis[taxi_count]['location'][0], taxis[taxi_count]['location'][1], 'Taxi')
        message_taxi = {
            'name' : taxis[taxi_count]['name'],
            'number': taxis[taxi_count]['number'],
            'type' : taxis[taxi_count]['type'],
            'location_x' : taxi_coordinates[0],
            'location_y' : taxi_coordinates[1],
            'locationof' : 'Taxi',
            'timestamp' : str(datetime.datetime.now())
        }
        message_taxi_json = json.dumps(message_taxi)

        response = kinesis_handle.put_record(SreamName = KINESIS_DATA_STREAM,
                                             Data = message_taxi_json,
                                             PartitiionKey = message_taxi['locationof'])
        print("Taxi Response\n",response)
        taxi_count+=1
def publishNextUserLocation(loopCount2):
    user_count = 0
    while(user_count<=len(users)):
        user_coordinates = getNextCoOrdinates(users[user_count]['location'][0],users[user_count]['location'][1],'user')

        message_user = {
                    'name': users[user_count]['name'],
                    'email': users[user_count]['email'],
                    'location_x': user_coordinates[0],
                    'location_y' : user_coordinates[1],
                    'locationof' : 'user',
                    'timestamp' : str(datetime.datetime.now())
                }

        message_user_json = json.dumps(message_user)

        response = kinesis_handle.put_record(StreamName = KINESIS_DATA_STREAM,
                                                     Data = message_user_json,
                                                     PartitionKey = message_user['locationof'])
        print("User Response\n",response)
        user_count+=1

print("Kinesis stream data push started ..")
now = time.time()

scheduler = sched.scheduler(time.time,time.sleep)
loopCount1 = 0
loopCount2=0
while True:
    try:
        scheduler.enterabs(now+loopCount1,1,publishNextTaxiLocation,(loopCount1,))
        loopCount1+=TAXIS_TIME_INTERVAL
        scheduler.enterabs(now+loopCount2,2,publishNextUserLocation,(loopCount2,))
        loopCount2+=USERS_TIME_INTERVAL
        scheduler.run()
    except KeyboardInterrupt:
        break

print("Data push to kinesis stream stopped!")



