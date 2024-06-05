import random
import os
import sqlite3
import time
import datetime
from datetime import timedelta
from getpass import getpass
from os import system
import os

TOKEN_LENGTH = 10
TOKEN_FILE_DIR = "./api_token/"
ADD_DAY_DIR = "./add_day/"
DEL_TOKEN_DIR = "./del_token/"
DB_PATH = "database.db"
ADMIN_USERNAME = "관리자 아이디"
ADMIN_PASSWORD = "관리자 비번"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
        print(f"{bcolors.FAIL}데이터베이스 연결 오류: {e}{bcolors.ENDC}")
        return None

def clear_database():
    username = input(f"{bcolors.OKCYAN}관리자 아이디를 입력하세요: {bcolors.ENDC}")
    password = input(f"{bcolors.OKCYAN}관리자 비밀번호를 입력하세요: {bcolors.ENDC}")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        try:
            con = get_db_connection()
            if con is None:
                return

            cur = con.cursor()
            cur.execute("DELETE FROM token;")
            con.commit()
            print(f"{bcolors.OKGREEN}데이터베이스의 모든 내용이 삭제되었습니다.{bcolors.ENDC}")
            for filename in os.listdir(TOKEN_FILE_DIR):
                file_path = os.path.join(TOKEN_FILE_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"{bcolors.OKGREEN}토큰 파일 '{filename}'이 삭제되었습니다.{bcolors.ENDC}")

        except Exception as e:
            print(f"{bcolors.FAIL}오류: {str(e)}{bcolors.ENDC}")
        finally:
            con.close()
    else:
        print(f"{bcolors.FAIL}잘못된 관리자 아이디 또는 비밀번호입니다.{bcolors.ENDC}")

def show_all_tokens():
    con = get_db_connection()
    if con is None:
        return

    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM token;")
        tokens = cur.fetchall()

        if tokens:
            print(f"{bcolors.OKGREEN}전체 토큰 목록:{bcolors.ENDC}")
            for token in tokens:
                print(f"토큰: {token[0]}, 만료일: {token[1]}, 유효기간(일): {token[2]}")
        else:
            print(f"{bcolors.WARNING}등록된 토큰이 없습니다.{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}오류: {str(e)}{bcolors.ENDC}")
    finally:
        con.close()


def gen_token():
    day = input(f"{bcolors.OKCYAN}몇 일 짜리 토큰을 생성할까요 (기간 : 숫자로) : {bcolors.ENDC}")
    amount = input(f"{bcolors.OKCYAN}몇 개를 생성할까요 (숫자로) : {bcolors.ENDC}")

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
        print(f"{bcolors.OKGREEN}{day}일짜리 토큰.txt 파일에 저장이 완료되었습니다.{bcolors.ENDC}")
        return "\n".join(created_token)
    else:
        print(f"{bcolors.WARNING}숫자로 적어주세요.{bcolors.ENDC}")

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

        if not tokens:
            print(f"{bcolors.WARNING}아무 정보도 없습니다.{bcolors.ENDC}")
            return

        invalid_tokens = [token for token in tokens if not cur.execute("SELECT * FROM token WHERE token == ?;", (token,)).fetchone()]

        if invalid_tokens:
            print(f"{bcolors.FAIL}정확한 토큰을 넣고 다시 시작해주세요. 잘못된 토큰: {', '.join(invalid_tokens)}{bcolors.ENDC}")
            with open(f"{ADD_DAY_DIR}invalid_token.txt", "w") as i:
                i.write('\n'.join(invalid_tokens))
            return

        token_add = int(input(f"{bcolors.OKCYAN}API토큰에 몇일을 추가할까요: {bcolors.ENDC}"))

        for token in tokens:
            cur.execute("SELECT * FROM token WHERE token == ?;", (token,))
            info = cur.fetchone()
            if info:
                new_expiration_date = add_t(info[1], token_add)
                new_days = int(info[2]) + token_add
                cur.execute("UPDATE token SET expirationDate = ?, days = ? WHERE token == ?;", (new_expiration_date, new_days, token))

        con.commit()
        print(f"{bcolors.OKGREEN}{ADD_DAY_DIR}token.txt 에 있는 모든 토큰에 {token_add}일씩 추가 완료되었습니다{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}오류: {str(e)}{bcolors.ENDC}")
    finally:
        con.close()

def check_token():
    token = input(f"{bcolors.OKCYAN}확인할 토큰을 입력하세요: {bcolors.ENDC}")
    
    con = get_db_connection()
    if con is None:
        return

    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM token WHERE token == ?;", (token,))
        info = cur.fetchone()
        
        if info:
            print(f"{bcolors.OKGREEN}토큰: {info[0]}\n만료일: {info[1]}\n유효기간(일): {info[2]}{bcolors.ENDC}")
        else:
            print(f"{bcolors.WARNING}해당 토큰은 존재하지 않습니다.{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}오류: {str(e)}{bcolors.ENDC}")
    finally:
        con.close()

def delete_token():
    con = get_db_connection()
    if con is None:
        return

    cur = con.cursor()
    ensure_dir(DEL_TOKEN_DIR)
    
    try:
        with open(f"{DEL_TOKEN_DIR}tokens.txt", "r", encoding='utf-8') as f:
            tokens = f.read().splitlines()

        if not tokens:
            print(f"{bcolors.WARNING}아무 정보도 없습니다.{bcolors.ENDC}")
            return

        invalid_tokens = [token for token in tokens if not cur.execute("SELECT * FROM token WHERE token == ?;", (token,)).fetchone()]

        if invalid_tokens:
            print(f"{bcolors.FAIL}정확한 토큰을 넣고 다시 시작해주세요. 잘못된 토큰: {', '.join(invalid_tokens)}{bcolors.ENDC}")
            with open(f"{DEL_TOKEN_DIR}invalid_token.txt", "w") as i:
                i.write('\n'.join(invalid_tokens))
            return

        for token in tokens:
            cur.execute("DELETE FROM token WHERE token == ?;", (token,))

        con.commit()
        print(f"{bcolors.OKGREEN}{DEL_TOKEN_DIR}tokens.txt 에 있는 모든 토큰이 삭제 완료되었습니다{bcolors.ENDC}")
    except Exception as e:
        print(f"{bcolors.FAIL}오류: {str(e)}{bcolors.ENDC}")
    finally:
        con.close()
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system("title Culture API Token Gen" if os.name == 'nt' else "")

    while True:
        try:
            menu = int(input(f"{bcolors.OKBLUE}원하시는 메뉴를 골라주세요.\n"
                             "[1] : API토큰생성\n"
                             "[2] : API토큰 기간 연장\n"
                             "[3] : 토큰 정보 확인\n"
                             "[4] : API토큰 삭제\n"
                             "[5] : 데이터 베이스 올 클리어\n"
                             "[6] : 모든 토큰 보기\n"
                             "[7] : 프로그램 종료\n원하시는 메뉴 : "))
            os.system('cls' if os.name == 'nt' else 'clear')
            if menu == 1:
                gen_token()
                print(f"{bcolors.OKCYAN}4초후 메뉴창으로 돌아갑니다{bcolors.ENDC}")
                time.sleep(4)
                os.system('cls' if os.name == 'nt' else 'clear')
            elif menu == 2:
                add_time()
                print(f"{bcolors.OKCYAN}10초후 메뉴창으로 돌아갑니다.{bcolors.ENDC}")
                time.sleep(10)
                os.system('cls' if os.name == 'nt' else 'clear')
            elif menu == 3:
                check_token()
                print(f"{bcolors.OKCYAN}4초후 메뉴창으로 돌아갑니다.{bcolors.ENDC}")
                time.sleep(4)
                os.system('cls' if os.name == 'nt' else 'clear')
            elif menu == 4:
                delete_token()
                print(f"{bcolors.OKCYAN}4초후 메뉴창으로 돌아갑니다.{bcolors.ENDC}")
                time.sleep(4)
                os.system('cls' if os.name == 'nt' else 'clear')
            elif menu == 5:
                clear_database()
                print(f"{bcolors.OKCYAN}4초후 메뉴창으로 돌아갑니다.{bcolors.ENDC}")
                time.sleep(4)
                os.system('cls' if os.name == 'nt' else 'clear')

            elif menu == 6:
                show_all_tokens()
                print(f"{bcolors.OKCYAN}10초후 메뉴창으로 돌아갑니다.{bcolors.ENDC}")
                time.sleep(10)
                os.system('cls')

            elif menu == 7:
                print(f"{bcolors.OKCYAN}3초후 프로그램을 종료합니다{bcolors.ENDC}")
                time.sleep(3)
                break
        except ValueError:
            print(f"{bcolors.WARNING}잘못된 입력입니다.{bcolors.ENDC}")


if __name__ == "__main__":
    main()
