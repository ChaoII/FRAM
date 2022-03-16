import datetime
import os.path
import time
import platform
import psutil
from typing import List, Optional
from jetsonface import FaceProcessHelper
from fastapi import FastAPI, File, UploadFile, HTTPException, status, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from multiprocessing import Process
import subprocess
import pandas as pd
import uuid
import ujson

# configure region
app = FastAPI(title="FRAM api")
app.mount(path="/static", app=StaticFiles(directory="./facelib"), name="static")

fr_obj = FaceProcessHelper("./models/", "./fonts/msyh.ttc", [0, 0])
face_lib_dir = "./facelib/"
tmp_json_filename = "tmp.json"
temp_json_path = os.path.join(face_lib_dir, tmp_json_filename)

face_config_json_path = os.path.join(face_lib_dir, "facelib.json")
main_pid = 0
provide_id = False

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


# function region
def check_face_quality(file_name_uuid: str, name: str) -> bool:
    ujson.dump([{
        "filename": file_name_uuid + ".jpg",
        "name": name
    }], open(temp_json_path, "w", encoding="utf8"))
    # 执行验证看是否能够计算出结果
    return fr_obj.create_face_feature_DB_by_json(face_lib_dir, tmp_json_filename)


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
        ujson.dump(final_face_infos, fw)


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
    res = subprocess.Popen(f"{python_interpreter} {main_program}",
                           shell=True,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    global main_pid
    main_pid = res.pid
    res.wait()


@app.put("/api/add_face_libs")
async def add_face_libs(files: List[UploadFile] = File(...)):
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

        res["id"] = id_
        res["name"] = name
        res["update_time"] = update_time
        res["message"] = "success"
        try:
            f = await file.read()
            with open(file_path, "wb") as f_:
                f_.write(f)
        except IOError as e:
            res["message"] = "file open failed ,please check your file so that can be read successful"
            return [res]
        check_status = check_face_quality(id_, name)
        if not check_status:
            os.remove(file_path)
            os.remove(temp_json_path)
            res["message"] = "can not find a face"
        else:
            dst_face_infos = packing_face_info(id_, name, update_time)
            save_in_json(dst_face_infos)
        res_list.append(res)
    return res_list


@app.get("/api/get_attended_infos")
async def get_attended_infos(date_time: Optional[str] = None):
    if date_time is None:
        file_name = datetime.date.today().strftime("%Y-%m-%d") + ".xls"
    else:
        date_obj = datetime.datetime.strptime(date_time, "%Y-%m-%d").date()
        file_name = date_obj.strftime("%Y-%m-%d") + ".xls"
    file_path = os.path.join("attend", file_name)
    res = dict()
    res["result"] = ""
    res["message"] = ""

    try:
        df = pd.read_excel(file_path)
        attend_info = df.to_dict(orient="records")
        res["result"] = attend_info
    except Exception as e:
        res["message"] = f"select error, fault detail is {e} "
    return res


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
