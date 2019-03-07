#!/usr/bin/env python

# file     : nagiosTelegram.py
# purpose  : send nagion notifications via Telegram bot
#
# author   : harald van der laan
# date     : 2017/04/01
# version  : v1.0.1
#
# changelog:
# - v1.0.1      added nagios command
# - v1.0.0      initial commit                                          (harald)

''' nagiosTelegram.py - small python script for sending nagion messages via a telegram
    bot. Please see BotFather for more info about telegram bots 
    
    https://core.telegram.org/bots
    
    Open telegram -> search for contacts: @BotFather
    send the following message to BotFather
    /newbot -> and answer the questions of BotFather
    
    # getting your telegram or group id
    1) send a message to you bot and surf to:
       https://api.telegram.org/bot<token>/getStatus
    2) download telegram-cli and send a message to the bot
    
    usage:
    # host event
    ./nagiosTelegram.py --token <bot toke> --contact <contact|group id> \ 
        --notificationtype 'host' --hoststate <UP|DOWN|UNREACHABLE> \ 
        --hostname <hostname> --hostaddress <ipaddress> \ 
        --output <event message>
    
    # service event
    ./nagiosTelegram.py --token <bot token> --contact <contact|group_id> \ 
        --notificationtype 'service' --servicestate <'OK|WARNING|CRITICAL"UNKOWN> \ 
        --servicedesc <service descriptoin> --hostname <hostname> \ 
        --output <event message>
    
    # nagios configuration
    define command {
        command_name    notify-host-by-telegram
        command_line    /usr/local/bin/nagiosTelegram.py --token <token> \ 
            --notificationtype host --contact "$CONTACTPAGER$" --notificationtype "$NOTIFICATIONTYPE$" \ 
            --hoststate "$HOSTSTATE$" --hostname "$HOSTNAME$" --hostaddress "$HOSTADDRESS$" --output "$HOSTOUTPUT$"
    }
    
    define command {
        command_name    notify-service-by-telegram
        command_line    /usr/local/bin/nagiosTelegram.py --token <token> \
            --notificationtype service --contact "$CONTACTPAGER$" --notificationtype "$NOTIFICATIONTYPE$" \ 
            --servicestate "$SERVICESTATE$" --hostname "$HOSTNAME$" --servicedesc "$SERVICEDESC$" --output "$SERVICEOUTPUT$"
    
    define contact {
        contact_name                    nagios telegram bot
        pager                           -<contact|group_id>
        service_notification_commands   notify-service-by-telegram
        host_notification_commands      notify-host-by-telegram
    }'''

from __future__ import print_function
import sys
import argparse
import json
import requests

token="276049022:AAFse4JMCYmwfRYh9Pr45Z6SvzSe12_2mlc"
contact="-201690907"

def parse_args():
    ''' function for parsing arguments '''
    parser = argparse.ArgumentParser(description='Nagios notification via Telegram')
    parser.add_argument('-o', '--object_type', nargs='?', required=True)
    #parser.add_argument('--contact', nargs='?', required=True)
    parser.add_argument('--notificationtype', nargs='?')
    parser.add_argument('--hoststate', nargs='?')
    parser.add_argument('--hostname', nargs='?')
    parser.add_argument('--hostaddress', nargs='?')
    parser.add_argument('--servicestate', nargs='?')
    parser.add_argument('--servicedesc', nargs='?')
    parser.add_argument('--output', nargs='?')
    args = parser.parse_args()

    return args

def send_notification(token, user_id, message):
    ''' function for sending notification via Telegram bot '''
    url = 'https://api.telegram.org/bot' + token + '/sendMessage'
    payload = {'chat_id': user_id, 'text': message}
    #print ("https://api.telegram.org/bot" + token + "/sendMessage?chat_id="+contact+"&text="+message)

    return requests.post(url, data=payload)

def host_notification(args):
    ''' creating host notification message '''
    state = ''
    if args.hoststate == 'UP':
        state = u'\U00002705 '
    elif args.hoststate == 'DOWN':
        state = u'\U0001F525 '
    elif args.hoststate == 'UNREACHABLE':
        state = u'\U00002753 '

    return '{}{} ({}): {}' .format(state.encode('utf-8'), args.hostname,
                                   args.hostaddress, args.output)

def service_notification(args):
    ''' creating service notification message '''
    state = ''
    if args.servicestate == 'OK':
        state = u'\U00002705 '
    elif args.servicestate == 'WARNING':
        state = u'\U000026A0 '
    elif args.servicestate == 'CRITICAL':
        state = u'\U0001F525 '
    elif args.servicestate == 'UNKNOWN':
        state = u'\U00002753 '

    return '{}{}/{}: {}' .format(state.encode('utf-8'), args.hostname,
                                 args.servicedesc, args.output)

def main():
	''' main function '''
	args = parse_args()
	user_id = int(contact)
	if args.object_type == 'host':
		message = host_notification(args)
	elif args.object_type == 'service':
		message = service_notification(args)

	response = send_notification(token, user_id, message)

	# if you want output, uncomment these lines.
	if json.loads(response.text)['ok']:
		#got status 200
		#print('[+] {}: message was send to bot' .format(__FILE__))
		print ("OK")
	else:
		#got status !200
		#print('[-] error: {} - {}' .format(json.loads(response.text)['error_code'],json.loads(response.text)['description']))
		print ("ERROR")
		sys.exit(1)

if __name__ == "__main__":
    main()
    sys.exit(0)
