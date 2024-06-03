import random, os, sqlite3, time, datetime
from datetime import timedelta


TOKEN_LENGTH = 20
TOKEN_FILE_DIR = "./api_token/"
ADD_DAY_DIR = "./add_day/"
DB_PATH = "database.db"


def make_expiretime(days):
    expire_time = datetime.datetime.now() + timedelta(days=days)
    return expire_time.strftime('%Y-%m-%d %H:%M')

def now():
    return str(datetime.datetime.now()).split(".")[0]

def code_gen(length):
    return ''.join(random.choice("QWERTYUIOPASDFGHJKLZXCVBNM1234567890") for _ in range(length))

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_db_connection():
    try:
        con = sqlite3.connect(DB_PATH)
        return con
    except sqlite3.Error as e:
        print(f"데이터베이스 연결 오류: {e}")
        return None

def gen_token():
    day = input("몇 일 짜리 토큰을 생성할까요 (기간 : 숫자로) : ")
    amount = input("몇 개를 생성할까요 (숫자로) : ")

    if day.isdigit() and amount.isdigit():
        day = int(day)
        amount = int(amount)
        created_token = []
        
        con = get_db_connection()
        if con is None:
            return

        cur = con.cursor()
        ensure_dir(TOKEN_FILE_DIR)

        for _ in range(amount):
            code = code_gen(TOKEN_LENGTH)
            cur.execute("INSERT INTO token VALUES (?, ?, ?);", (code, make_expiretime(day), str(day)))
            created_token.append(code)
            with open(f"{TOKEN_FILE_DIR}{day}일짜리 토큰.txt", "a") as f:
                f.write(f"{code}\n")

        con.commit()
        con.close()
        print(f"{day}일짜리 토큰.txt 파일에 저장이 완료되었습니다.")
        return "\n".join(created_token)
    else:
        print("숫자로 적어주세요.")

def add_t(expiration_date, days_to_add):
    expiration_date_obj = datetime.datetime.strptime(expiration_date, "%Y-%m-%d %H:%M")
    new_expiration_date_obj = expiration_date_obj + timedelta(days=days_to_add)
    return new_expiration_date_obj.strftime("%Y-%m-%d %H:%M")

def add_time():
    con = get_db_connection()
    if con is None:
        return

    cur = con.cursor()
    ensure_dir(ADD_DAY_DIR)
    
    try:
        with open(f"{ADD_DAY_DIR}token.txt", "r", encoding='utf-8') as f:
            tokens = f.read().splitlines()

        invalid_tokens = [token for token in tokens if not cur.execute("SELECT * FROM token WHERE token == ?;", (token,)).fetchone()]

        if invalid_tokens:
            print(f"정확한 토큰을 넣고 다시 시작해주세요. 잘못된 토큰: {', '.join(invalid_tokens)}")
            with open(f"{ADD_DAY_DIR}invalid_token.txt", "w") as i:
                i.write('\n'.join(invalid_tokens))
            return

        token_add = int(input("API토큰에 몇일을 추가할까요: "))

        for token in tokens:
            cur.execute("SELECT * FROM token WHERE token == ?;", (token,))
            info = cur.fetchone()
            if info:
                new_expiration_date = add_t(info[1], token_add)
                new_days = int(info[2]) + token_add
                cur.execute("UPDATE token SET expirationDate = ?, days = ? WHERE token == ?;", (new_expiration_date, new_days, token))

        con.commit()
        print(f"{ADD_DAY_DIR}token.txt 에 있는 모든 토큰에 {token_add}일씩 추가 완료되었습니다")
    except Exception as e:
        print(f"오류: {str(e)}")
    finally:
        con.close()

def check_token():
    token = input("확인할 토큰을 입력하세요: ")
    
    con = get_db_connection()
    if con is None:
        return

    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM token WHERE token == ?;", (token,))
        info = cur.fetchone()
        
        if info:
            print(f"토큰: {info[0]}\n만료일: {info[1]}\n유효기간(일): {info[2]}")
        else:
            print("해당 토큰은 존재하지 않습니다.")
    except Exception as e:
        print(f"오류: {str(e)}")
    finally:
        con.close()

def main():
    os.system('cls')
    os.system("title Culture API Token Gen")

    while True:
        try:
            menu = int(input("원하시는 메뉴를 골라주세요.\n[1] : API토큰생성 | [2] : API토큰 기간 연장 | [3] : 토큰 정보 확인 | [4] : 프로그램 종료 : "))
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
            elif menu == 3:
                check_token()
                print("10초후 메뉴창으로 돌아갑니다.")
                time.sleep(10)
                os.system('cls')
            elif menu == 4:
                print("3초후 프로그램을 종료합니다")
                time.sleep(3)
                break
            else:
                print("잘못된 입력입니다. 다시 시도해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")

if __name__ == "__main__":
    main()
