from utils import load_bais
from pathlib import Path
from utils import plot_lines_chart
from datetime import datetime
from zoneinfo import ZoneInfo

if __name__ == "__main__":
    print("Updating IC/IM data...")
    IC_data = load_bais("IC")
    IC_data.to_csv(Path("data/IC_data.csv"), index=False, encoding="utf-8-sig")
    IM_data = load_bais("IM")
    IM_data.to_csv(Path("data/IM_data.csv"), index=False, encoding="utf-8-sig")
    fig = plot_lines_chart(
        x_data=IC_data["日期"],
        ys_data=[IC_data["年化基差(%)"], IM_data["年化基差(%)"]],
        names=["IC年化基差(%)", "IM年化基差(%)"],
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
        </body>
    </html>"""
    # Write the combined figure to an HTML file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
