import os
import ujson
import datetime
import platform
import sqlite3
from typing import List, Optional
from jetsonface import FaceProcessHelper
from pydantic import BaseModel
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Body

tmp = Jinja2Templates(directory='templates')

if platform.system() != "Windows":
    os.system("sudo chmod 777 /dev/ttyTHS1")

# configure region
app = FastAPI(title="FRAM api", version="1.1.0")
app.mount(path="/static/facelib", app=StaticFiles(directory="./facelib"), name="static_face_lib")
app.mount(path="/static/", app=StaticFiles(directory="./static"), name="static")
fr_obj = FaceProcessHelper("./models/", "./fonts/msyh.ttc", [0, 0])
face_lib_dir = "./facelib/"
face_config_json_path = os.path.join(face_lib_dir, "facelib.json")

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
    flags = [info.get("id") for info in src_face_infos]
    for dst_info in dst_face_infos:
        cur_flag = dst_info.get("id", "-1")
        if cur_flag in flags:
            idx = flags.index(cur_flag)
            # os.remove(os.path.join(face_lib_dir, src_face_infos[idx]["filename"]))
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


@app.get("/", include_in_schema=False)
async def index(request: Request):
    return tmp.TemplateResponse('dashboard.html', {'request': request})


@app.get("/dashboard", include_in_schema=False)
async def dashboard(request: Request):
    # authorize_token(token)
    # request.cookies.update({"token": token})
    return tmp.TemplateResponse("dashboard.html", {"request": request})


@app.get("/attendinfo", include_in_schema=False)
async def attendinfo(request: Request):
    return tmp.TemplateResponse('attendinfo.html', {'request': request})


@app.get("/faceinfo", include_in_schema=False)
async def faceinfo(request: Request):
    with open(face_config_json_path, encoding="utf8") as fp:
        res = ujson.load(fp)
    return tmp.TemplateResponse('faceinfo.html', {'request': request, "facelibs": res})


@app.put("/api/add_face_libs")
async def add_face_libs(files: List[UploadFile] = File(...)):
    res_list = []
    for file in files:
        res = dict()
        # if request file provide the id ,it can be used,otherwise, generate automatically id.Such as
        # upload file's name is "HR0878_艾超.jpg",otherwise 艾超.jpg

        id_ = file.filename.split("_")[0]
        name = file.filename.split("_")[1].split(".")[0]

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
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                 detail="file open failed ,please check your file so that can be read successful")

        dst_face_infos = packing_face_info(id_, name, update_time)
        save_in_json(dst_face_infos)
        res_list.append(res)
    return res_list


@app.get("/api/get_face_libraries")
async def get_face_libraries():
    # authorize_token(token)
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
        flags = [info.get("id") for info in res]
        idx = flags.index(delete_info.face_id)
        os.remove(os.path.join(face_lib_dir, res[idx]["filename"]))
        res.remove(res[idx])
        with open(face_config_json_path, "w", encoding="utf8") as fw:
            ujson.dump(res, fw, ensure_ascii=False)
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                             {"message": f"failed + 【{e}】"})
    return {"message": "success"}


@app.post("/api/get_attended_infos")
async def get_attended_infos(start_time: datetime.datetime = Body(...),
                             end_time: datetime.datetime = Body(...)):
    """
    获取打卡流水，按照时间段来
    :param start_time: 打卡起始时间
    :param end_time: 打卡结束时间
    :return:
    """
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
        return res
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                             {"message": f"query error, fault detail is {e},please try again serval seconds "})


@app.get("/api/down_facelib")
async def down_facelib(staff_id: str):
    file_name = staff_id + ".jpg"
    return FileResponse(path="./facelib/" + file_name, filename=file_name)


@app.get("/api/clear_data")
async def clear_data(start_time: Optional[datetime.datetime] = None,
                     end_time: Optional[datetime.datetime] = None):
    if start_time is None:
        start_time = (datetime.datetime.now() - datetime.timedelta(days=100000)).strftime("%Y-%m-%d %H:%M:%S %f")
    if end_time is None:
        end_time = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S %f")
    try:
        conn = sqlite3.connect("attend.db")
        cursor = conn.cursor()
        cursor.execute(f"delete * from attend where attend_time >'{start_time}' and attend_time <='{end_time}'")
        return {"message": "success delete "}
    except Exception as e:
        return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                             f"delete data failed, fault detail is {e},please try again serval seconds ")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
