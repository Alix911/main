import datetime
import time
from types import NoneType
import requests
from flask import abort, flash, redirect, url_for
from werkzeug.security import check_password_hash
from models import AllowedTime, AllowedTries, BannedBrowsers, BannedCountries, BannedIPAddress, Logs, Rules,Alerts,db,User,Counter

class Checks():
    def __init__(self,user,password,ip,user_agent):
        self.user = user
        self.password = password
        self.ip = ip
        self.user_agent = user_agent
        self.code = ''
        if isinstance(db.session.query(Counter).filter_by(user_id=self.user.id).first(), NoneType):
            counter = Counter(user_id=self.user.id,banned_browser_count=1,suspicious_ip_count=2,banned_country_count=3,allowed_tries_break_count=5,allowed_time_break_count=4)
            db.session.add(counter)
            db.session.commit()
        # self.checkTries()
        # self.check_time()
        # self.checkIP()
        # self.checkCountry()
        # self.checkBrowser()

        
    def check_block(self,rule_id):
        msg = f"{self.user.name} was blocked due to {db.session.query(Rules).filter_by(rule_id=rule_id).first().rule}"
        alert = Alerts(user_id=self.user.id, message=msg, time=datetime.datetime.now())
        if isinstance(db.session.query(Logs).filter_by(user_id=self.user.id).first(), NoneType):
            log = Logs(user_id=self.user.id,time=datetime.datetime.now(),priority='Low',color='primary')
            db.session.add(log)
            db.session.commit()
        
        self.user.blocks+=1
        db.session.commit()
        db.session.add(alert)
        db.session.commit()
        self.checkUserBlocks()
        
   
        
    def checkUserTries(self,tries,rule_id):
        count = db.session.query(Counter).filter_by(user_id=self.user.id).one()
        if tries.tries == 0:
            count.allowed_tries_break_count+=1
            db.session.commit()
            self.check_block(rule_id)
            abort(403,"YOU HAVE BEEN BLOCKED FOR FAILING TO LOGIN")
        else:
            return True
        
    def checkUserBlocks(self):
        logs = Logs.query.filter().all()
        for log in logs:
            
            user = db.session.query(User).filter_by(id=log.user_id).first()
            if isinstance(user,NoneType):
                continue
            
            if user.blocks in range(7):
                log.priority = 'Low'
                log.color = 'primary'
                
            elif user.blocks in range(7,12):
                log.priority ='Medium'
                log.color = 'secondary'
                
            elif user.blocks in range(12,15):
                log.priority ='High'
                log.color = 'danger'
                
            elif user.blocks in range(15,100):
                log.priority = 'Critical'
                log.color = 'success'

            db.session.commit()
            

                

    def checkIP(self):
        url = 'https://api.abuseipdb.com/api/v2/check'

        querystring = {
            'ipAddress': self.ip,
            'maxAgeInDays': '1'
        }

        headers = {
            'Accept': 'application/json',
            'Key': 'd14fa19a32cece48c4a61f1afb44e2ab3e9063fd1b948fd6469fba2017365950fe024f0892835f7f'
        }
        try:
            response = requests.request(method='GET', url=url, headers=headers, params=querystring)
            data = response.json()
            self.code = data["data"]['countryCode']
            whitelisted = data["data"]["isWhitelisted"]
            bannedIPAddresses = db.session.query(BannedIPAddress).filter().all()

            if bannedIPAddresses == []:
                return True
            else:
                bannedIPs = [ip.ip_address for ip in bannedIPAddresses]
                rule_id = bannedIPAddresses[0].rule_id
                count = db.session.query(Counter).filter_by(user_id=self.user.id).one()
                if whitelisted or self.ip not in bannedIPs:
                    return True
                else:
                    count.suspicious_ip_count+=1
                    db.session.commit()
                    self.check_block(rule_id)
                    abort(403,"YOU HAVE BEEN BLOCKED FOR USING A SUSPICIOUS IP")
        except:
            print("FAILD to check IP address due to using localhost ip address to access this site")
            
    def check_time(self):
        allowedTime = db.session.query(AllowedTime).filter().first()
        
        if allowedTime is None:
            return True
        else:
            print(allowedTime.start_datetime.time())
            print(allowedTime.end_datetime.time())
            start_time = allowedTime.start_datetime
            end_time = allowedTime.end_datetime
            current_time = datetime.datetime.now()
            
            rule_id = allowedTime.rule_id
            count = db.session.query(Counter).filter_by(user_id=self.user.id).one()
            # difference = start_time - end_time
            # if difference.days == 0: 
            #     data = [start_time + datetime.timedelta(days=x) for x in range(res.days+1)]
            if current_time < end_time and current_time >= start_time:
                print("condition was true")
                return True
            else:
                count.allowed_time_break_count+=1
                db.session.commit()
                self.check_block(rule_id)
                abort(403,"YOU HAVE BEEN BLOCKED FOR LOGGING IN OUTSIDE THE SPECIFIED TIME")

        
    def checkCountry(self):
        try:
            country = requests.get(f"https://restcountries.com/v3.1/alpha/{self.code}").json()[0]['name']['common']
            # print(country)
            countries = db.session.query(BannedCountries).filter().all()
            if countries == []:
                return True
            else:
                rule_id = countries[0].rule_id
                count = db.session.query(Counter).filter_by(user_id=self.user.id).one()
                countries = [cd.country for cd in countries]

                if country in countries:
                    count.banned_country_count+=1
                    db.session.commit()
                    self.check_block(rule_id)
                    abort(403,"YOU HAVE BEEN BLOCKED FOR LOGGING IN FORM A BANNED COUNTRY")
                else:
                    return True
        except:
            print("FAILD to check country due to using localhost ip address to access this site")
        

    def checkBrowser(self):

        client_browser = self.user_agent.__str__()
        browsers = db.session.query(BannedBrowsers).filter().all()
        if browsers == []:
            return True
        else:
            rule_id = browsers[0].rule_id
            browsers = [b.browser for b in browsers]
            count = db.session.query(Counter).filter_by(user_id=self.user.id).one()
            for b in browsers:
                if b in client_browser:
                    count.banned_browser_count+=1
                    db.session.commit()
                    self.check_block(rule_id)
                    abort(403,"YOU HAVE BEEN BLOCKED FOR USING PROHIBITED BROWSER")
                else:
                    continue
        
    def checkTries(self):
         # Fetch the AllowedTries record for the user, or create one if it doesn't exist
         self.tries = db.session.query(AllowedTries).filter_by(user_id=self.user.id).first()
      
         if self.tries is None:
             # Create a default AllowedTries record for the user
             self.tries = AllowedTries(user_id=self.user.id, rule_id=5, tries=5)  # Replace default_rule_id with actual rule ID
             db.session.add(self.tries)
             db.session.commit()

         # Check if the user has exceeded their allowed tries
         if self.tries.tries <= 0:
             return "Too many attempts"

         # Check the user password here (assuming self.password is the input password)
         if not check_password_hash(self.user.password, self.password):
            # Decrement the tries and save
            self.tries.tries -= 1
            db.session.commit()
            return "Invalid Password"

         # If the password is correct, reset the tries count to default
         self.tries.tries = 5
         db.session.commit()
         return True
        
        
        
        
        # if check_password_hash(self.user.password, self.password) == False:
        #     print(check_password_hash(self.user.password, self.password))
        #     if self.checkUserTries(self.tries,rule_id) == True:
        #         print(self.checkUserTries(self.tries,rule_id))
        #         self.tries.tries-=1
        #         db.session.commit()
        #         return "Invalid Password"
        
        # else:
        #     return True
        

