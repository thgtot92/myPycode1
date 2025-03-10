import warnings
import numpy as np
import pandas as pd
from pandas import DataFrame
from IPython.display import HTML
from pathlib import Path
import os

###HTML 파일 목록 읽기 (로컬 지정해주기)
folder_path = "./"  
file_paths = [f for f in os.listdir(folder_path) if f.endswith(".html")]

###합칠 HTML의 기본 구조 body쪽에 메시지가 있다.. 여기서 뽑아주면 될듯?
merged_html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>합쳐진 HTML 문서</title>
</head>
<body>
"""

###각 파일의 내용을 합치기
for file_path in file_paths:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        # body 태그 안의 내용만 추출
        body_content = content.split("<body>")[-1].split("</body>")[0]
        merged_html += body_content + "\n"

###합친파일 정리.
merged_html += """</body>
</html>
"""

###새로운 패쓰에 HTML 파일 저장함.
merged_file_path = "./merged_html_document.html"
with open(merged_file_path, "w", encoding="utf-8") as merged_file:
    merged_file.write(merged_html)

