import time
import json


body =  {}
def getHeaders(access_token):
    return {'content-type': 'application/json','Authorization':'Bearer '+access_token};
def get_orders(access_token):   
    r = requests.get(url+'/api/v2/order', data=json.dumps(body), headers=getHeaders(access_token))
    return r.json();
def net_positions(access_token):
    r = requests.get(url+'/api/v2/positions?type=netwise', data=json.dumps(body), headers=getHeaders(access_token))
    return r.json();
def cancel_order(access_token,oid):
    r = requests.delete(url+'/api/v2/order?oms_order_id='+str(oid)+'&order_status=open', data=json.dumps(body), headers=getHeaders(access_token))
    return r.json();
def cancel_cover_order(access_token,oid):
    all_orders=get_orders(access_token);
    data=all_orders['data']
    for key in data:
        for j in data[key]:            
            if int(j['oms_order_id'])==int(oid):
                leg_order_id=j['leg_order_indicator']
                r = requests.delete(url+'/api/v2/coverorder?oms_order_id='+str(oid)+'&leg_order_indicator='+str(leg_order_id), data=json.dumps(body), headers=getHeaders(access_token))
                return r.json();

def market_order(access_token,exchange,i_token,qty,ttype):
    body={  
           "exchange":exchange,
           "order_type":"MARKET",
           "instrument_token":i_token,
           "quantity":qty,
           "disclosed_quantity":0,
           "price":0,
           "transaction_type":ttype,
           "trigger_price":0,
           "validity":"DAY",
           "product":"MIS",
           "source":"web",
           "order_tag": "order1"
        }
    r = requests.post(url+'/api/v2/order', data=json.dumps(body), headers=getHeaders(access_token))
    return (r.text);
    
def dayEnd(access_token):
    all_orders=get_orders(access_token);    
    for c in all_orders['data']['completed_orders']:        
        if c['product']=='CO':
            cancel_cover_order(access_token,int(c['oms_order_id']));
    for p in all_orders['data']['pending_orders']:
        if p['product']=='CO':
            cancel_cover_order(access_token,int(p['oms_order_id']));
        elif p['product'] == "CNC":
            continue;
        else:
            cancel_order(access_token,int(p['oms_order_id']));
    net_pos=net_positions(access_token);
    modified_net_pos={};
  
    for j in net_pos['data']['positions']:
        if j['product'] != 'MIS':
            continue;
        exchange,i_token,qty=j['exchange'],int(j['instrument_token']),int(j['net_quantity'])
     
        if qty>0:
            ttype="SELL";
        elif qty<0:
            ttype="BUY";
        else:
            continue;
        market_order(access_token,exchange,int(i_token),abs(qty),ttype)
        time.sleep(0.05);
    


if __name__=='__main__':
    dayEnd(access_token)