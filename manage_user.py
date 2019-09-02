# manage_user.py
import sys

from clcrypto import generate_salt, check_password
from models import User, make_connection
import argparse


def configure_parser():
    new_parser = argparse.ArgumentParser(prog='python manage_user.py')
    new_parser.add_argument('-u', '--username')
    new_parser.add_argument('-p', '--password')
    new_parser.add_argument('-n', '--new-pass')
    new_parser.add_argument('-l', '--list', action='store_true', help='żądanie wylistowania wszystkich użytkowników')
    new_parser.add_argument('-d', '--delete', action='store_true', help='usunięcie konta')
    new_parser.add_argument('-e', '--edit', action='store_true', help='zmiana hasła')
    return new_parser


def add_new_user(args, cursor):
    new_user = User.find_by_email(cursor, args.username)
    if not new_user:
        new_user = User()
        new_user.email = args.username
        new_user.username = args.username
        new_user.set_password(args.password, generate_salt())
        new_user.save_to_db(cursor)
    else:
        raise Exception('User exists')


def change_user_password(args, cursor):
    user_to_edit = User.find_by_email(cursor, args.username)
    if user_to_edit and check_password(args.password, user_to_edit.hashed_password):
        user_to_edit.set_password(args.new_pass, generate_salt())
        user_to_edit.save_to_db(cursor)
    else:
        raise Exception('Złe hasło lub użyszkodnik nie istnieje')


def delete_me(args, cursor):
    user_to_delete = User.find_by_email(cursor, args.username)
    if user_to_delete and check_password(args.password, user_to_delete.hashed_password):
        user_to_delete.delete(cursor)
    else:
        raise Exception('Zły login lub hasło')


def print_all_users(cursor):
    users = User.find_all(cursor)
    print('Lista użyszkodników')
    for user in users:
        print(user.email)


if __name__ == '__main__':
    parser = configure_parser()
    args = parser.parse_args(sys.argv[1:])
    cnx = make_connection()
    cursor = cnx.cursor()
    try:
        if args.username and args.password and not args.edit and not args.delete:
            '''
            Jeśli użytkownik wprowadził parametry -u oraz -p, ale nie wprowadził parametru -e ani –d, sprawdzamy, czy 
            użytkownik o takim emailu istnieje, a jeśli nie, to zakładamy użytkownika i nadajemy mu hasło. Jeśli 
            użytkownik istnieje, zgłaszamy błąd.
            '''
            add_new_user(args, cursor)
        elif args.username and args.password and args.edit and args.new_pass:
            '''
            Jeśli użytkownik wprowadził parametry -u oraz -p, ale wprowadził -e, sprawdzamy poprawność hasła. Jeśli jest 
            poprawne, to nadajemy mu nowe hasło, które pobieramy z parametru -n (oczywiście sprawdzając długość hasła).
            '''
            change_user_password(args, cursor)
        elif args.username and args.password and args.delete:
            '''
            Jeśli użytkownik wprowadził parametry -u oraz -p, ale wprowadził -d, sprawdzamy poprawność hasła. Jeśli 
            jest poprawne, usuwamy użytkownika z bazy.
            '''
            delete_me(args, cursor)
        elif args.list:
            '''
            Jeśli użytkownik podał parametr -l, wyświetlamy wszystkich zarejestrowanych użytkowników (nie pokazujemy
            haseł).
            '''
            print_all_users(cursor)
        else:
            '''
            Jeśli użytkownik wprowadził parametry w konfiguracji innej niż podane na slajdach, ma mu się wyświetlić
            komunikaty pomocy.
            '''
            parser.print_help()
    finally:
        cursor.close()
        cnx.close()
