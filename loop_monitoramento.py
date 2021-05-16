import requests
import time

timer = 5

def main():
    while True:
        try:
            r = requests.get('http://localhost:4999/monitoramento')
            print(r.text)
            r.close()
        except Exception as e:
            print(e)
        time.sleep(timer)

main()