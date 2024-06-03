import random, os, sqlite3, time, datetime
from datetime import timedelta, datetime

def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime = ServerTime + timedelta(days=days)
    ExpireTime_STR = str((ServerTime + timedelta(days=days)).strftime('%Y-%m-%d %H:%M'))
    return ExpireTime_STR

def now():
    return str(datetime.datetime.now()).split(".")[0]

def code_gen(pick):
    code = ""
    for _ in range(pick):
        code += random.choice("QWERTYUIOPASDFGHJKLZXCVBNM1234567890")
    return code
os.system('cls')
os.system("title Culture API Token Gen")

def gen_token():
    day = input("몇 일 짜리 토큰을 생성할까요 (기간 : 숫자로) : ")
    amount = input("몇 개를 생성할까요 (숫자로) : ")
    if day.isdigit():
        if amount.isdigit():
            created_token = []
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            for i in range(int(amount)):
                code = code_gen(10)
                cur.execute("insert into token values (?, ?, ?);", (code, make_expiretime(int(day)), str(day)))
                if os.path.isfile(f"./api_token/{day}일짜리 토큰.txt"):
                    with open(f'./api_token/{day}일짜리 토큰.txt', "a") as q:
                        q.write(f"\n{str(code)}")
                else:
                    with open(f"./api_token/{day}일짜리 토큰.txt", "w") as f:
                        f.write(str(code))
            con.commit()
            con.close()
            print(f"{day}일짜리 토큰.txt 파일에 저장이 완료되었습니다.")
            return "\n".join(created_token)
        else:
            print("숫자로 적어주세요.")
    else:
        print("숫자로 적어주세요.")


def add_t(expiration_date, days_to_add):
    expiration_date_obj = datetime.strptime(expiration_date, "%Y-%m-%d %H:%M")
    new_expiration_date_obj = expiration_date_obj + timedelta(days=days_to_add)
    return new_expiration_date_obj.strftime("%Y-%m-%d %H:%M")

def add_time():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    with open("./add_day/token.txt", "r", encoding='utf-8') as f:
        content = f.read()
        tokens = content.split("\n")

        invalid_tokens = [token for token in tokens if not cur.execute("SELECT * FROM token WHERE token == ?;", (token,)).fetchone()]

        if invalid_tokens:
            print(f"정확한 토큰을 넣고 다시 시작해주세요. 잘못된 토큰: {', '.join(invalid_tokens)}")
            with open("./add_day/invalid_token.txt", "w") as i:
                i.write('\n'.join(invalid_tokens))
            return

        try:
            token_add = int(input("API토큰에 몇일을 추가할까요: "))
            for token in tokens:
                cur.execute("SELECT * FROM token WHERE token == ?;", (token,))
                info = cur.fetchone()

                if info:
                    new_expiration_date = add_t(info[1], token_add)
                    new_days = int(info[2]) + token_add
                    cur.execute("UPDATE token SET expirationDate = ?, days = ? WHERE token == ?;", (new_expiration_date, new_days, token))

            con.commit()
            print(f"add_day/token.txt 에 있는 모든 토큰에 {token_add}일씩 추가 완료되었습니다")
        except Exception as e:
            print(f"오류: {str(e)}")
        finally:
            con.close()

while True:
    menu = int(input("원하시는 메뉴를 골라주세요.\n[1] : API토큰생성 | [2] : API토큰 기간 연장 | [3] : 프로그램 종료 : "))
    os.system('cls')
    if menu == 1:
        gen_token()
        print("4초후 메뉴창으로 돌아갑니다")
        time.sleep(4)
        os.system('cls')
    elif menu == 2:
        add_time() 
        print("10초후 메뉴창으로 돌아갑니다.")
        time.sleep(10)
        os.system('cls')
    elif menu ==3 :
        print("3초후 프로그램을 종료합니다")
        time.sleep(3)
        break