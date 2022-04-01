import os
import uuid
import ujson
import datetime
import platform
import psutil
import subprocess
import sqlite3
from jose import JWTError, jwt
from typing import List, Optional
from jetsonface import FaceProcessHelper
from pydantic import BaseModel
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, File, UploadFile, HTTPException, status, BackgroundTasks, Depends, Body, Form

auth_users = [
    {"id": "HR0878", "name": "艾超", "password": "1234"},
    {"id": "HR0771", "name": "程坤", "password": "1234"}
]

tmp = Jinja2Templates(directory='templates')

auth_users_ids = [user["id"] for user in auth_users]

if platform.system() != "Windows":
    os.system("sudo chmod 777 /dev/ttyTHS1")

# configure region
app = FastAPI(title="FRAM api")
app.mount(path="/static/facelib", app=StaticFiles(directory="./facelib"), name="static_face_lib")
app.mount(path="/static/", app=StaticFiles(directory="./static"), name="static")
fr_obj = FaceProcessHelper("./models/", "./fonts/msyh.ttc", [0, 0])
face_lib_dir = "./facelib/"

face_config_json_path = os.path.join(face_lib_dir, "facelib.json")
main_pid = -1
provide_id = True

main_program = "main.py"
if platform.system() == "Windows":
    python_interpreter = "python"
else:
    python_interpreter = "python3"

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "ed970259a19edfedf1010199c7002d183bd15bcaec612481b29bac1cb83d8137"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_jwt_token(data: dict, expire_delta: Optional[datetime.timedelta] = None):
    # 如果传入了过期时间, 那么就是用该时间, 否则使用默认的时间
    expire = datetime.datetime.now() + expire_delta if expire_delta else datetime.datetime.now() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 需要加密的数据data必须为一个字典类型, 在数据中添加过期时间键值对, 键exp的名称是固定写法
    data.update({'exp': expire})
    # 进行jwt加密
    token = jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


# function region

def save_in_json(dst_face_infos: List[dict]):
    if not os.path.exists(face_config_json_path):
        open(face_config_json_path, "w").close()
    try:
        with open(face_config_json_path, "r", encoding="utf8") as fr:
            src_face_infos = ujson.load(fr)
            print(type(src_face_infos))
    except ValueError as e:
        src_face_infos = []

    final_face_infos = update_info(src_face_infos, dst_face_infos)

    with open(face_config_json_path, "w", encoding="utf8") as fw:
        ujson.dump(final_face_infos, fw, ensure_ascii=False)


def update_info(src_face_infos: List[dict], dst_face_infos: List[dict]):
    # in general, if private id , it will be searched by id.
    # otherwise searched by name
    # searched by name do not suggest
    if provide_id:
        flag_str = "id"
    else:
        flag_str = "name"
    flags = [info.get(flag_str) for info in src_face_infos]
    for dst_info in dst_face_infos:
        cur_flag = dst_info.get(flag_str, "-1")
        if cur_flag in flags:
            idx = flags.index(cur_flag)
            os.remove(os.path.join(face_lib_dir, src_face_infos[idx]["filename"]))
            src_face_infos[idx] = dst_info
        else:
            src_face_infos.append(dst_info)
    return src_face_infos


def packing_face_info(id_: str, name_: str, update_time: str):
    res = dict()
    res["id"] = id_
    res["name"] = name_
    res["filename"] = id_ + ".jpg"
    res["update_time"] = update_time
    return [res]


def run_fram():
    global main_pid
    p = subprocess.Popen(f"{python_interpreter} {main_program}",
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    main_pid = p.pid
    p.stderr.read()


def sql_fetch_json(cursor: sqlite3.Cursor):
    """
    Convert the pymysql SELECT result to json format
    :param cursor:
    :return:
    """
    keys = []
    for column in cursor.description:
        keys.append(column[0])
    key_number = len(keys)

    json_data = []
    for row in cursor.fetchall():
        item = dict()
        for q in range(key_number):
            value = row[q]
            if keys[q].__contains__("time"):
                value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S %f").strftime("%Y-%m-%dT%H:%M:%S.%f")
            item[keys[q]] = value
        json_data.append(item)
    return json_data


@app.get("/")
async def index(request: Request):
    return tmp.TemplateResponse('login.html', {'request': request})


@app.get("/login")
async def login(request: Request):
    return tmp.TemplateResponse('login.html', {'request': request})


@app.get("/attendinfo")
async def attendinfo(request: Request):
    return tmp.TemplateResponse('attendinfo.html', {'request': request})


@app.get("/faceinfo")
async def faceinfo(request: Request):
    with open(face_config_json_path, encoding="utf8") as fp:
        res = ujson.load(fp)
    return tmp.TemplateResponse('faceinfo.html', {'request': request, "facelibs": res})


@app.post('/login')
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in auth_users_ids:
        idx = auth_users_ids.index(username)
        user = auth_users[idx]
        # 密码应该使用加密的密码----本地简单使用了
        if password == user["password"]:
            # 使用user_id生成jwt token
            data = {'user_id': username}
            token = create_jwt_token(data)
            return tmp.TemplateResponse("dashboard.html", {"request": request, 'token': token})
        else:
            return tmp.TemplateResponse("login.html", {"request": request, 'password_info': "密码错误"})

    else:
        return tmp.TemplateResponse("login.html", {"request": request, 'username_info': "用户名错误"})


@app.put("/api/add_face_libs")
async def add_face_libs(files: List[UploadFile] = File(...), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        # 根据OAuth2规范, 认证失败需要在响应头中添加如下键值对
        headers={'WWW-Authenticate': "Bearer"}
    )
    # 验证token
    try:
        # 解密token, 返回被加密的字典
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        # 从字典中获取user_id数据
        user_id = payload.get('user_id')
        print(f'user_id: {user_id}')
        # 若没有user_id, 则返回认证异常
        if not user_id:
            raise credentials_exception
    except JWTError as e:
        print(f'认证异常: {e}')
        # 如果解密过程出现异常, 则返回认证异常
        raise credentials_exception
    # 解密成功, 返回token中包含的user_id
    # 执行该用户下的操作
    if user_id not in auth_users_ids:
        raise credentials_exception
    res_list = []
    for file in files:
        res = dict()
        # if request file provide the id ,it can be used,otherwise, generate automatically id.Such as
        # upload file's name is "bb287cda-8985-45af-a597-516bef5c7ca9_艾超.jpg",otherwise 艾超.jpg
        if provide_id:
            id_ = file.filename.split("_")[0]
            name = file.filename.split("_")[1].split(".")[0]
        else:
            id_ = str(uuid.uuid4())
            name = file.filename.split('.')[0]
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")
        file_path = face_lib_dir + id_ + ".jpg"

        res["staff_id"] = id_
        res["name"] = name
        res["update_time"] = update_time
        res["message"] = "success"
        try:
            f = await file.read()
            with open(file_path, "wb") as f_:
                f_.write(f)
            check_status = fr_obj.face_quality_authorize(file_path)
            if not check_status:
                os.remove(file_path)
                res["message"] = "face quality authorize failed"
        except IOError as e:
            res["message"] = "file open failed ,please check your file so that can be read successful"
            return [res]

        dst_face_infos = packing_face_info(id_, name, update_time)
        save_in_json(dst_face_infos)
        res_list.append(res)
    return res_list


@app.get("/api/get_face_libraries")
async def get_face_libraries():
    with open(face_config_json_path, encoding="utf8") as fp:
        res = ujson.load(fp)
    return res


class DeleteInfo(BaseModel):
    face_id: str


@app.delete("/api/delete_face")
async def delete_face(delete_info: DeleteInfo):
    try:
        with open(face_config_json_path, encoding="utf8") as fp:
            res = ujson.load(fp)
        del res[delete_info.face_id]
        os.remove("./facelib/face_id" + ".jpg")
        with open(face_config_json_path, "w", encoding="utf8") as fw:
            ujson.dump(res, fw, ensure_ascii=False)
    except Exception as e:
        return {"message": f"failed + 【{e}】"}
    return {"message": "success"}


@app.post("/api/get_attended_infos")
async def get_attended_infos(start_time: datetime.datetime = Body(...),
                             end_time: datetime.datetime = Body(...)):
    print(start_time.strftime("%Y-%m-%d %H:%M:%S %f"))
    res = dict()
    res["result"] = ""
    res["message"] = ""
    try:
        conn = sqlite3.connect("attend.db")
        cursor = conn.cursor()
        cursor.execute(f"select staff_id,name,attend_time from attend \
        where attend_time >'{start_time}' and attend_time <='{end_time}'")
        attend_info = sql_fetch_json(cursor)
        res["result"] = attend_info
    except Exception as e:
        res["message"] = f"query error, fault detail is {e},please try again serval seconds "
    return res


@app.get("/api/down_facelib")
async def down_facelib(staff_id: str):
    file_name = staff_id + ".jpg"
    return FileResponse(path="./facelib/" + file_name, filename=file_name)


@app.get("/api/clear_data")
async def clear_data(start_time: Optional[datetime.datetime] = None,
                     end_time: Optional[datetime.datetime] = None):
    if start_time is None:
        start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")
    if end_time is None:
        end_time = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S %f")
    try:
        conn = sqlite3.connect("attend.db")
        cursor = conn.cursor()
        cursor.execute(f"delete * from attend where attend_time >'{start_time}' and attend_time <='{end_time}'")
        return {"message": "success delete "}
    except Exception as e:
        return {"message": f"delete data failed, fault detail is {e},please try again serval seconds "}


class DateTimeModel(BaseModel):
    date: datetime.date
    time: datetime.time


@app.put("/api/update_sys_time")
async def update_sys_time(date_time: DateTimeModel):
    date_str = datetime.date.strftime(date_time.date, "%m/%d%Y")
    time_str = datetime.time.strftime(date_time.time, "%H:%M:%S")
    if platform.system() != "Windows":
        os.system(f"sudo date -s {date_str}")
        os.system(f"sudo date -s {time_str}")


@app.get("/api/start_fram/")
async def start_fram(back_task: BackgroundTasks):
    back_task.add_task(run_fram)
    return {"message": "frame start successfully"}


@app.get("/api/stop_frame/")
async def stop_frame():
    global main_pid
    try:
        if platform.system() == 'Windows':
            p = psutil.Process(main_pid)
            p.terminate()
            p.wait()
        else:
            os.system("ps aux | grep main.py | awk '{print $2}' | xargs kill -9")
        return {"message": "stop_frame successfully"}
    except Exception as e:
        HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, f"stop_frame failed,detail is :{e}"
        )


@app.get("/api/restart_fram")
async def restart_fram(back_task: BackgroundTasks):
    global main_pid
    try:
        if platform.system() == 'Windows':
            p = psutil.Process(main_pid)
            p.terminate()
        else:
            os.system("ps aux | grep main.py | awk '{print $2}' | xargs kill -9")
        back_task.add_task(run_fram)
        return {"message": "restart successfully"}
    except Exception as e:
        HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, f"restart failed,detail is :{e}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
