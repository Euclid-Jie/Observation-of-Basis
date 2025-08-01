from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from typing import Literal, List
import requests
import re
import urllib.parse
import json
import uuid
from typing import List
from pyecharts.charts import Line
from pyecharts import options as opts

__all__ = [
    "load_bais",
    "plot_lines_chart",
]


def load_bais(type=Literal["IF", "IC", "IM", "IH"]) -> pd.DataFrame:
    if type == "IF":
        data = "params=%7B%22head%22%3A%22IF%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IC":
        data = "params=%7B%22head%22%3A%22IC%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IM":
        data = "params=%7B%22head%22%3A%22IM%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    elif type == "IH":
        data = "params=%7B%22head%22%3A%22IH%22%2C%22N%22%3A251%7D&PageID=46803&websiteID=20906&ContentID=Content&UserID=&menup=0&_cb=&_cbdata=&_cbExec=1&_cbDispType=1&__pageState=0&__globalUrlParam=%7B%22PageID%22%3A%2246803%22%2C%22pageid%22%3A%2246803%22%7D&g_randomid=randomid_1051095574548506702800710985&np=%5B%2246803%40Content%40TwebCom_div_1_0%40220907102451613%22%5D&modename=amljaGFfZGFpbHlfY2hhcnRfN0Q5MTQ5NDE%3D&creator=cjzq"
    else:
        raise ValueError("type must be one of 'IF', 'IC', 'IM', 'IH'")
    decoded_data = urllib.parse.unquote(data)
    # 解析为字典格式
    parsed_params = urllib.parse.parse_qs(decoded_data)
    parsed_params["g_randomid"] = "randomid_" + str(uuid.uuid4().int)[:-11]
    updated_data = urllib.parse.urlencode(parsed_params, doseq=True)
    response = requests.post(
        "https://web.tinysoft.com.cn/website/loadContentDataAjax.tsl?ref=js",
        updated_data,
    )

    data = response.content.decode("utf-8", "ignore")
    data = json.loads(data)
    soup = BeautifulSoup(data["content"][0]["html"], "html.parser")
    script_content = soup.find("script").string
    match = re.search(r"var\s+SrcData\s*=\s*(\[.*?\]);", script_content, re.DOTALL)
    src_data_raw = match.group(1)
    # 将转义字符转换为实际字符
    src_data = json.loads(src_data_raw.encode().decode("unicode_escape"))
    data_df = pd.DataFrame(src_data)[
        [
            "日期",
            "主力合约",
            "期货价格",
            "现货价格",
            "基差",
            "到期日",
            "剩余天数",
            "期内分红",
            "矫正基差",
            "主力年化基差(%)",
            "年化基差(%)",
        ]
    ]
    # data_df["日期"] = pd.to_datetime(data_df["日期"])
    return data_df


# Function to generate a line chart with multiple lines
def plot_lines_chart(
    x_data: np.ndarray,
    ys_data: List[np.ndarray],
    names: List[str],
    range_start: int = 0,
    range_end: int = 100,
    lower_bound: float = None,
    up_bound: float = None,
):
    assert len(ys_data) == len(names), "Length of ys_data and names should be the same"
    line = Line(
        init_opts={
            "width": "1560px",
            "height": "600px",
            "is_horizontal_center": True,
        }
    ).add_xaxis(list(x_data))
    for i, y_data in enumerate(ys_data):
        line.add_yaxis(names[i], list(y_data), is_symbol_show=False)

    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(type_="category"),
        yaxis_opts=opts.AxisOpts(type_="value", min_=lower_bound, max_=up_bound),
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(font_weight="bold", font_size=20)
        ),
        datazoom_opts=[
            opts.DataZoomOpts(
                range_start=range_start, range_end=range_end, orient="horizontal"
            )
        ],
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    ).set_series_opts(
        linestyle_opts=opts.LineStyleOpts(width=2),
    )
    return line
