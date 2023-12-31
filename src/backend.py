import datetime
import sqlite3
import argparse
from prettytable import PrettyTable

con = sqlite3.connect("to-do.db")

cur = con.cursor()


# cur.execute("CREATE TABLE todos(Task, Startdate, Duedate, Enddate)")
#cur.execute("DROP TABLE kvakk")


HEADERS = ["ID", "Task", "Start date", "Due date", "End date"]


def create_table(cur: sqlite3.Cursor) -> None:
    cur.execute(
        """
                CREATE TABLE todos( 
                    ID INTEGER PRIMARY KEY AUTOINCREMENT, 
                    task text NOT NULL, 
                    start_date date NOT NULL, 
                    due_date text, 
                    end_date text
                )"""
    )


#create_table(cur)
res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchall())


def select_all(cur: sqlite3.Cursor) -> list:
    cur.execute(
        """
                SELECT * FROM todos"""
    )
    res = cur.fetchall()
    return res


def select_all_finished(cur: sqlite3.Cursor) -> list:
    cur.execute(
        """
                SELECT * FROM todos WHERE not end_date is NULL"""
    )
    res = cur.fetchall()
    return res


def select_unfinished(cur: sqlite3.Cursor) -> list:
    cur.execute(
        """
                SELECT * FROM todos WHERE end_date is NULL"""
    )
    res = cur.fetchall()
    return res


def add_to_do(
    con: sqlite3.Connection,
    cur: sqlite3.Cursor,
    task: str,
    start_date_str: str,
    due_date_str: str,
    end_date_str: str | None = None,
) -> None:
    start_date = datetime.datetime.strptime(start_date_str, "%d-%m-%Y").date()
    due_date = datetime.datetime.strptime(due_date_str, "%d-%m-%Y").date()
    end_date = (
        datetime.datetime.strptime(end_date_str, "%d-%m-%Y").date()
        if end_date_str
        else None
    )
    cur.execute(
        """ INSERT INTO todos(task, start_date, due_date, end_date) 
                VALUES(?, ?, ?, ?)""",
        (task, start_date, due_date, end_date),
    )
    con.commit()


def display_table(data, header):
    table = PrettyTable(header)
    table.align = "l"
    for row in data:
        table.add_row(row)
    print(table)


def set_end_date(cur, end_date_str: str | None, task_id: int) -> None:
    if end_date_str:
        end_date = datetime.datetime.strptime(end_date_str, "%d-%m-%Y").date()
    else:
        end_date = datetime.date.today()
    cur.execute("UPDATE todos SET end_date = ? WHERE ID = ?", (end_date, task_id))
    con.commit()


parser = argparse.ArgumentParser(description="CLI-based attempt at a to-do-list")
parser.add_argument(
    "-f", "--finished", help="display the finished tasks", action="store_true"
)
parser.add_argument(
    "-u", "--unfinished", help="display the unfinished tasks", action="store_true"
)
parser.add_argument("-a", "--all", help="display all tasks", action="store_true")
parser.add_argument("-n", "--new", help="add new entry", type=str)
parser.add_argument(
    "-s",
    "--set_end_date",
    help="set enddate, and thus mark a task as finished. takes ID of task and (optional) date, else today's date",
    type=str,
)

args = parser.parse_args()

if args.finished:
    list = select_all_finished(cur)
    display_table(list, HEADERS)

if args.unfinished:
    print("unfinished entries")
    list = select_unfinished(cur)
    display_table(list, HEADERS)

if args.all:
    list = select_all(cur)
    print("all entries: ")
    display_table(list, HEADERS)

if args.new:
    new_arg_list = args.new.split(",")
    if len(new_arg_list) == 3:
        task, start_date, due_date = new_arg_list
        add_to_do(con, cur, task.strip(), start_date.strip(), due_date.strip())

if args.set_end_date:
    arg_list = args.set_end_date.split(",")
    if len(arg_list) == 1:
        set_end_date(cur, None, task_id=int(arg_list[0]))
    elif len(arg_list) == 2:
        set_end_date(cur, arg_list[0], int(arg_list[1]))


con.commit()
con.close() 