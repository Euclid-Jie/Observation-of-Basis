import sqlalchemy
from utils import load_bais
from utils import plot_lines_chart
from datetime import datetime
from zoneinfo import ZoneInfo
from config import SQL_PASSWORDS, SQL_HOST

def write_to_sql(data, table_name, engine):
    data.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False,
        dtype={
            "日期": sqlalchemy.types.Date,
            "主力合约": sqlalchemy.types.String(20),
            "到期日": sqlalchemy.types.Date,
            "剩余天数": sqlalchemy.types.Integer,
        },
    )

if __name__ == "__main__":
    print("Starting sql data update process...")
    engine = sqlalchemy.create_engine(
        f"mysql+pymysql://dev:{SQL_PASSWORDS}@{SQL_HOST}:3306/UpdatedData?charset=utf8"
    )
    future_types = ["IF", "IC", "IM", "IH"]
    all_data = {}
    for future_type in future_types:
        data = load_bais(future_type)
        all_data[future_type] = data
        write_to_sql(data, f"{future_type}_data", engine)
        print(f"{future_type} data updated successfully.")

    print("Updating IF/IC/IM data...")
    IF_data = all_data.get("IF")
    IC_data = all_data.get("IC")
    IM_data = all_data.get("IM")
    fig = plot_lines_chart(
        x_data=IC_data["日期"],
        ys_data=[IF_data["年化基差(%)"], IC_data["年化基差(%)"], IM_data["年化基差(%)"]],
        names=["IF年化基差(%)", "IC年化基差(%)", "IM年化基差(%)"],
        range_start=75,
    )
    html = f"""<html>
        <head>
            <meta charset="UTF-8">
            <title>Value over Time</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }}
                table {{
                    margin: auto;
                    margin-bottom: 20px;
                    border-collapse: collapse;
                    width: 80%;
                }}
                table, th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }}
                th {{
                    background-color: #f59e00;
                    color: white;
                }}
                #timestamp {{
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    font-size: 12px;
                    color: #999;
                }}
            </style>
        </head>
        <body>
            <div>CopyRight © Euclid-Jie Last Updated: {datetime.now(ZoneInfo('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S")}</div>
            {fig.render_embed()}
            <div style="margin-top: 30px; font-size: 14px; line-height: 1.5; margin-left: 20px; font-family: 'Calibri', sans-serif;">
            <div style="font-weight: bold; margin-bottom: 10px;">基差计算说明</div>
            <div>年化基差算法: 每一天，针对主力合约计算基差(=期货价格-现货价格)，然后提取当天至该主力合约到期日之间的"期内分红"，进而计算出"矫正基差"(=基差+期内分红)，最后计算出年化基差率，公式如下:</div>
            <div style="margin: 10px 0;">年化基差率 = (矫正基差 ÷ 指数现货收盘价) × (365 ÷ 合约到期剩余天数)</div>
            <div>期内分红算法: 把合约剩余期限内每日的指数分红点位相加，如果是历史合约，指数每日的分红点位直接用对应的股息点指数来计算，如果是当前尚未到期的合约，未来期限内的每日分红点位用预测值计算。</div>
            <div>主力合约是根据昨持仓进行判断，昨持仓最大的即为当日主力合约。</div>
            </div>
        </body>
    </html>"""
    # Write the combined figure to an HTML file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
