import pymysql
import pandas as pd
from django.shortcuts import render
from pyecharts.charts import Bar, Map3D, Radar, Pie, WordCloud, Bar3D, Line
from pyecharts import options as opts
from pyecharts.globals import ChartType
from pyecharts.commons.utils import JsCode
from django.http import JsonResponse
import re
import jieba
from collections import Counter

def extract_price(price_str):
    match = re.search(r'(\d+(\.\d+)?)', str(price_str))
    if match:
        return float(match.group(1))
    return None

def create_bar1(city_counts):
    bar = (
        Bar(init_opts=opts.InitOpts(width="400px", height="300px"))
        .add_xaxis(city_counts['city'].tolist())
        .add_yaxis(
            series_name="房源数量",
            y_axis=city_counts['total'].tolist(),
            label_opts=opts.LabelOpts(is_show=False),  # 隐藏数据标签
            itemstyle_opts=opts.ItemStyleOpts(color="#5470C6")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="各城市房源数量对比",
                pos_left="center",
                pos_top="20px",
                title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")
            ),
            xaxis_opts=opts.AxisOpts(
                name="城市",
                axislabel_opts=opts.LabelOpts(rotate=0)
            ),
            yaxis_opts=opts.AxisOpts(
                name="房源数量（套）",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter="{b}<br/>数量: {c}套"
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return bar.render_embed()

def create_bar2(city_avg_price):
    bar = (
        Bar(init_opts=opts.InitOpts(width="400px", height="300px"))
        .add_xaxis(city_avg_price['城市'].tolist())
        .add_yaxis(
            series_name="",
            y_axis=city_avg_price['均价'].tolist(),
            label_opts=opts.LabelOpts(
                is_show=True,
                position="top",
                formatter="{c}元"
            ),
            itemstyle_opts=opts.ItemStyleOpts(color="#37A2FF"),
            bar_width="40%"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="各城市二手房均价对比",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")
            ),
            xaxis_opts=opts.AxisOpts(
                name="城市",
                axislabel_opts=opts.LabelOpts(
                    rotate=30,
                    interval=0
                )
            ),
            yaxis_opts=opts.AxisOpts(
                name="均价（元/㎡）",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter="{b}<br/>均价: {c}元/㎡"
            ),
            datazoom_opts=[opts.DataZoomOpts()]
        )
    )
    return bar.render_embed()

def create_map3d(city_counts):
    guangxi_coords = {
        "南宁市": [108.479, 23.1152],
        "柳州市": [109.4282, 24.3269],
        "桂林市": [110.3055, 25.2736],
        "梧州市": [111.3055, 23.4856],
        "北海市": [109.1369, 21.4813],
        "防城港市": [108.3636, 21.6869],
        "钦州市": [108.6388, 21.9817],
        "贵港市": [109.6137, 23.1118],
        "玉林市": [110.1647, 22.6366],
        "百色市": [106.6318, 23.9013],
        "贺州市": [111.5526, 24.4116],
        "河池市": [108.0854, 24.6929],
        "来宾市": [109.2318, 23.7418],
        "崇左市": [107.3579, 22.4151]
    }
    map3d_data = [
        (city + "市", [guangxi_coords[city + "市"][0], guangxi_coords[city + "市"][1], total / 5])
        for city, total in zip(city_counts["city"], city_counts["total"])
        if (city + "市") in guangxi_coords
    ]
    map3d = (
        Map3D(init_opts=opts.InitOpts(width="700px", height="600px"))
        .add_schema(
            maptype="广西",
            itemstyle_opts=opts.ItemStyleOpts(
                color="rgb(5,101,123)",
                opacity=1,
                border_width=0.8,
                border_color="rgb(62,215,213)",
            ),
            map3d_label=opts.Map3DLabelOpts(
                is_show=False,
                formatter=JsCode("function(data){return data.name + ' ' + data.value[2];}"),
            ),
            emphasis_label_opts=opts.LabelOpts(
                is_show=False,
                color="#fff",
                font_size=10,
                background_color="rgba(0,23,11,0)",
            ),
            light_opts=opts.Map3DLightOpts(
                main_color="#fff",
                main_intensity=1.2,
                main_shadow_quality="high",
                is_main_shadow=False,
                main_beta=10,
                ambient_intensity=0.3,
            ),
        )
        .add(
            series_name="二手房总数/5",
            data_pair=map3d_data,
            type_=ChartType.BAR3D,
            bar_size=1,
            shading="lambert",
            label_opts=opts.LabelOpts(
                is_show=False,
                formatter=JsCode("function(data){return data.name + ' ' + data.value[2];}"),
            ),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="广西二手房数据分布", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")))
    )
    return map3d.render_embed()

def create_radar(huxin_counts_modified):
    huxin_list = huxin_counts_modified['huxin'].tolist()
    total_values = huxin_counts_modified['total'].tolist()
    schema = [
        {"name": huxin, "max": max(total_values) + 2000}
        for huxin in huxin_list
    ]
    radar = (
        Radar(init_opts=opts.InitOpts(width="200px", height="200px"))
        .add_schema(schema=schema)
        .add(
            series_name="户型数量",
            data=[total_values],
            color="#FF6600",
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False)  # 隐藏数据标签
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="户型数量对比雷达图", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return radar.render_embed()

def create_pie(huxin_counts_modified):
    data_pie = list(zip(huxin_counts_modified['huxin'], huxin_counts_modified['total']))
    pie = (
        Pie(init_opts=opts.InitOpts(width="200px", height="200px"))
        .add(
            series_name="户型分布",
            data_pair=data_pie,
            radius=["0%", "70%"],
            center=["50%", "50%"],
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1,
                border_color="#fff"
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="户型分布饼图",
                subtitle=None,
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")
            ),
            legend_opts=opts.LegendOpts(is_show=False),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{a}<br/>{b}: {c} ({d}%)"
            )
        )
        .set_series_opts(
            emphasis_opts=opts.EmphasisOpts(
                label_opts=opts.LabelOpts(font_size=14)
            )
        )
    )
    return pie.render_embed()

def create_wordcloud(word_freq):
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(width="400px", height="400px"))
        .add(
            series_name="标题关键词",
            data_pair=word_freq,
            word_size_range=[12, 60],
            shape="circle",
            mask_image=None,
            word_gap=10,
            rotate_step=45,
            tooltip_opts=opts.TooltipOpts(
                formatter="{b}: {c}"
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="标题关键词词云", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")),
            tooltip_opts=opts.TooltipOpts(is_show=True)
        )
    )
    return wordcloud.render_embed()

def get_top_keywords(texts, top_n=50):
    words = []
    for text in texts:
        words.extend(jieba.lcut(text))
    stopwords = ['的', '是', '和', '在', '有']  # 自定义停用词
    words_filtered = [
        word for word in words 
        if len(word) > 1 and word not in stopwords
    ]
    return Counter(words_filtered).most_common(top_n)

def create_bar3d_map(data_for_chart, grouped):
    bar3d = (
        Bar3D(init_opts=opts.InitOpts(width="700px", height="400px"))
        .add(
            series_name="均价(元/㎡)",
            data=data_for_chart,
            xaxis3d_opts=opts.Axis3DOpts(
                type_="category",
                data=sorted(grouped['方位'].unique()),
                name="方位",
                axislabel_opts=opts.LabelOpts(interval=0, rotate=0)
            ),
            yaxis3d_opts=opts.Axis3DOpts(
                type_="category",
                data=sorted(grouped['城市'].unique()),
                name="城市",
                axislabel_opts=opts.LabelOpts(
                    interval=0,
                    rotate=45,
                    font_size=10
                )
            ),
            zaxis3d_opts=opts.Axis3DOpts(type_="value", name="均价"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="各城市不同方位房价分布3D图", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")),
            visualmap_opts=opts.VisualMapOpts(
                max_=grouped['均价'].max(),
                min_=grouped['均价'].min(),
                range_color=[
                    "#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8",
                    "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"
                ],
            ),
            tooltip_opts=opts.TooltipOpts()
        )
    )
    return bar3d.render_embed()

def create_line(data_subset):
    line = (
        Line(init_opts=opts.InitOpts(width="800px", height="400px"))
        .add_xaxis(data_subset['时间'].tolist())
        .add_yaxis(
            series_name="",
            y_axis=data_subset['均价'].tolist(),
            symbol="circle",
            symbol_size=8,
            label_opts=opts.LabelOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(width=3),
            itemstyle_opts=opts.ItemStyleOpts(color="#FF6600")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="广西二手房建造年份与均价关系",
                subtitle="数据范围：第35-45年",
                pos_left="center",
                pos_top="10px",
                title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")
            ),
            xaxis_opts=opts.AxisOpts(
                name="建造年份",
                axislabel_opts=opts.LabelOpts(rotate=45)
            ),
            yaxis_opts=opts.AxisOpts(
                name="均价（元/㎡）",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter="{b}年<br/>均价: {c}元/㎡"
            )
        )
    )
    return line.render_embed()

# Create your views here.

def city_table(request):
    # 连接数据库
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='ershoufang'
    )
    df = pd.read_sql("SELECT * FROM ershoufang_list", conn)
    conn.close()

    # 处理均价字段
    df['均价'] = df['均价'].apply(extract_price)

    # 统计城市数量
    city_counts = df['城市'].value_counts().reset_index()
    city_counts.columns = ['city', 'total']

    # 计算各城市均价
    city_avg_price = df.groupby(['城市'])['均价'].mean().round(2).reset_index()

    # 统计户型数量并合并为前5+其他
    huxin_counts = df['户型'].value_counts().reset_index()
    huxin_counts.columns = ['huxin', 'total']
    top_huxin = huxin_counts.head(5).copy()
    other_total = huxin_counts.iloc[5:]['total'].sum()
    other_row = pd.DataFrame({'huxin': ['其他户型'], 'total': [other_total]})
    huxin_counts_modified = pd.concat([top_huxin, other_row], ignore_index=True)

    # 获取前50个高频词
    word_freq = get_top_keywords(df['标题'], top_n=50)

    # 按方位和城市分组计算均价均值
    grouped = df.groupby(['方位', '城市'])['均价'].mean().round(2).reset_index()
    data_for_chart = []
    directions = sorted(grouped['方位'].unique())  # x轴 - 方位
    cities = sorted(grouped['城市'].unique())      # y轴 - 城市
    direction_to_idx = {d: i for i, d in enumerate(directions)}
    city_to_idx = {c: i for i, c in enumerate(cities)}
    idx_to_direction = {i: d for d, i in direction_to_idx.items()}
    idx_to_city = {i: c for c, i in city_to_idx.items()}
    for _, row in grouped.iterrows():
        x_idx = direction_to_idx[row['方位']]
        y_idx = city_to_idx[row['城市']]
        data_for_chart.append([x_idx, y_idx, row['均价']])

    # 按时间分组计算均价均值
    set_time = df.groupby(['时间'])['均价'].mean().round(2).reset_index()
    # 提取35-45行数据（含）
    data_subset = set_time.iloc[34:45]

    chart_html1 = create_bar1(city_counts)
    chart_html2 = create_bar2(city_avg_price)
    chart_html3 = create_map3d(city_counts)
    radar_html = create_radar(huxin_counts_modified)
    pie_html = create_pie(huxin_counts_modified)
    wordcloud_html = create_wordcloud(word_freq)
    bar3d_map_html = create_bar3d_map(data_for_chart, grouped)
    line_html = create_line(data_subset)

    return render(request, 'city_table.html', {
        'chart_html1': chart_html1,
        'chart_html2': chart_html2,
        'chart_html3': chart_html3,
        'radar_html': radar_html,
        'pie_html': pie_html,
        'wordcloud_html': wordcloud_html,
        'bar3d_map_html': bar3d_map_html,
        'line_html': line_html
    })

def city_data_api(request):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='ershoufang'
    )
    df = pd.read_sql("SELECT * FROM ershoufang_list", conn)
    conn.close()

    # 处理均价字段
    df['均价'] = df['均价'].apply(extract_price)

    # 统计城市数量
    city_counts = df['城市'].value_counts().reset_index()
    city_counts.columns = ['city', 'total']

    # 计算各城市均价
    city_avg_price = df.groupby(['城市'])['均价'].mean().round(2).reset_index()

    # 统计户型数量并合并为前5+其他
    huxin_counts = df['户型'].value_counts().reset_index()
    huxin_counts.columns = ['huxin', 'total']
    top_huxin = huxin_counts.head(5).copy()
    other_total = huxin_counts.iloc[5:]['total'].sum()
    other_row = pd.DataFrame({'huxin': ['其他户型'], 'total': [other_total]})
    huxin_counts_modified = pd.concat([top_huxin, other_row], ignore_index=True)

    # 获取前50个高频词
    word_freq = get_top_keywords(df['标题'], top_n=50)

    # 按方位和城市分组计算均价均值
    grouped = df.groupby(['方位', '城市'])['均价'].mean().round(2).reset_index()
    data_for_chart = []
    directions = sorted(grouped['方位'].unique())  # x轴 - 方位
    cities = sorted(grouped['城市'].unique())      # y轴 - 城市
    direction_to_idx = {d: i for i, d in enumerate(directions)}
    city_to_idx = {c: i for i, c in enumerate(cities)}
    idx_to_direction = {i: d for d, i in direction_to_idx.items()}
    idx_to_city = {i: c for c, i in city_to_idx.items()}
    for _, row in grouped.iterrows():
        x_idx = direction_to_idx[row['方位']]
        y_idx = city_to_idx[row['城市']]
        data_for_chart.append([x_idx, y_idx, row['均价']])

    # 按时间分组计算均价均值
    set_time = df.groupby(['时间'])['均价'].mean().round(2).reset_index()
    # 提取35-45行数据（含）
    data_subset = set_time.iloc[34:45]

    chart_html1 = create_bar1(city_counts)
    chart_html2 = create_bar2(city_avg_price)
    chart_html3 = create_map3d(city_counts)
    radar_html = create_radar(huxin_counts_modified)
    pie_html = create_pie(huxin_counts_modified)
    wordcloud_html = create_wordcloud(word_freq)
    bar3d_map_html = create_bar3d_map(data_for_chart, grouped)
    line_html = create_line(data_subset)

    return JsonResponse({
        'chart_html1': chart_html1,
        'chart_html2': chart_html2,
        'chart_html3': chart_html3,
        'radar_html': radar_html,
        'pie_html': pie_html,
        'wordcloud_html': wordcloud_html,
        'bar3d_map_html': bar3d_map_html,
        'line_html': line_html
    })

def map3d_data_api(request):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='ershoufang'
    )
    df = pd.read_sql("SELECT * FROM ershoufang_list", conn)
    conn.close()
    df['均价'] = df['均价'].apply(extract_price)
    city_counts = df['城市'].value_counts().reset_index()
    city_counts.columns = ['city', 'total']
    return JsonResponse({
        'city_counts': city_counts.to_dict(orient='records')
    })
