import psycopg2
conn = psycopg2.connect(dbname='VicktoriaCostume', user='postgres',
                        password='3041', host='localhost')
print("Database opened successfully")
cur = conn.cursor()
cur.close()

async  def GetUserById(id):
    cur = conn.cursor()
    cur.execute(f"""
    SELECT tg_id, fullname, is_admin, phone 
    FROM public."user" 
    WHERE tg_id='{id}'
""")
    rows = cur.fetchone()
    cur.close()
    return rows
async def GetAllUsers():
    cur = conn.cursor()
    cur.execute("SELECT tg_id, fullname, is_admin, phone FROM public.user;")
    rows = cur.fetchall()
    print(rows)
    cur.close()
    return rows

async def GetAllUsersWithCostume():
    cur = conn.cursor()
    cur.execute("""SELECT "user", costume
	FROM public.basket;""")
    rows = cur.fetchall()
    result ="Список:\n"

    for row in rows:
        tg_id, fullname, is_admin, phone = await GetUserById(row[0])
        costume = await GetCostumeById(row[1])
        result+=f"{fullname},{phone},{costume[0]}\n"
    print(result)
    if(result=="Список:\n"):
        result+="Пуст"
    cur.close()

    return result



async def GetUserCostumes(id) -> str:
    cur = conn.cursor()
    cur.execute(f"""
   SELECT costume
	FROM public.basket where "user"='{id}'
""")
    rows = cur.fetchall()
    cur.close()
    print(rows)
    text = "Список:\n"
    for row in rows:
        print(row[0])
        desc = await GetCostumeById(row[0])
        text+=f"{desc[0]}\n"
    if(text=="Список:\n"):
       text+="Пусто. Молодец!"
    return text


async def GetCostumeById(id):
    cur = conn.cursor()
    cur.execute(f"""
  SELECT "desc"
	FROM public.costume Where id='{id}'
""")
    rows = cur.fetchone()
    cur.close()
    return rows


async def InsertUser(tg_id, fullname,phone):
    cur = conn.cursor()
    cur.execute("INSERT INTO public.user(tg_id, fullname,phone) VALUES (%s, %s,%s);",(tg_id,fullname,phone))
    conn.commit()
    cur.close()
async def InsertScannedCostume(tg_id, costume_id):
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO public.basket(
	"user", costume)
	VALUES (%s, %s);
    """,(tg_id,costume_id))
    conn.commit()
    cur.close()
async def UpdateUserName(tg_id, fullname):
    cur = conn.cursor()
    cur.execute(f"""
    UPDATE public."user"
	SET fullname='{fullname}'
	WHERE tg_id='{tg_id}';
    """)
    conn.commit()
    cur.close()

async def UpdateUserPhone(tg_id, phone):
    cur = conn.cursor()
    cur.execute(f"""
    UPDATE public."user"
	SET phone='{phone}'
	WHERE tg_id='{tg_id}';
    """)
    conn.commit()
    cur.close()


async def DeleteFromBasket(costume_id):
    cur = conn.cursor()
    cur.execute(f"""
        DELETE FROM public.basket
	    WHERE basket.costume='{costume_id}';
        """)
    conn.commit()
    cur.close()
