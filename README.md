# sms
simple message service



# test
cd /Users/jeesubkim/Project/sms
python3 -m unittest discover -s src/server/core/tests -t src

# venv
python3 -m venv venv
source venv/bin/activate

pip3 install -e .


# Plan
1) Socket layer. <---> Socket layer

2) Producer <---> Server
2.1) Mode1
2.2) Mode2

3) Consumer <---> Server
3.1) Mode1
3.2) Mode2