# PD To RDM

Forwards Pogodroid Raw Data to RDM. 
Limits Requests Types To Only What RDM Can Handle. (Massive RDM Performance Improvement)
Formats the Droid Data To RDM. (Tags Account As Lv 30 For IVs, And Passes Device Name As UDID And Username)
Adds RDM Header Token.

<strong>The contents of this repo is a proof of concept and is for educational use only!</strong>

## PD To RDM Config

- Enable Send Raw Data In Pogodroid
- Point Pogodroid Raw To Connector Address
- Add RDM Endpoint In PDToRDM.py: RDM_URL = "http://youserver:5000/raw"
- Add RDM Token to PDToRDM.py: AUTH_TOKEN = 'YOURRDMTOKEN'
- Startup.... python pdtordm.py (python3)
