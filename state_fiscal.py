
import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_tax_revenue_data():
    df=pd.read_excel('https://www2.census.gov/programs-surveys/qtax/tables/2023/q3t3.xlsx', skiprows=5)
    last_c = ''
    for x in df.columns:
        if x.startswith('Unnamed'):
            df.rename(columns={x: last_c}, inplace=True)
        else:
            last_c = x
    new_tax_code = []
    next_label = ''
    for i, row in df.iterrows():
        n = str(row['Tax Description']).replace('\xa0\xa0\xa0\xa0','').strip()
        if row.drop(['Tax Description']).isna().all():
            next_label = n
        else:
            if next_label == '':
                new_tax_code.append(n)
            else:
                new_tax_code.append(next_label + '|' + n)
    df = df[:32]
    df.loc[0,'Tax Description'] = 'fiscal_quarter'
    df=df.drop(columns=['Code']).set_index('Tax Description').T.reset_index().rename(columns={'index':'state'})
    df.set_index(['state','fiscal_quarter'], inplace=True)
    df = df.stack().rename('revenue').replace('X',0).astype(float).apply(lambda x: x*1e3/1e9).reset_index()
    df.rename(columns={'Tax Description':'tax_category'}, inplace=True)
    df['tax_category'] = df['tax_category'].str.strip()
    df['state'] = df['state'].str.replace('*','')
    return df


tax_translation_dict = {
    "Total Taxes": "总税收",
    "Property taxes": "财产税",
    "General sales and gross receipts": "一般销售和总收入税",
    "Motor fuels": "汽油税",
    "Alcoholic beverages": "酒精饮料税",
    "Public utilities": "公用事业税",
    "Insurance premiums": "保险费税",
    "Tobacco products": "烟草产品税",
    "Sports betting (including pari-mutuels)": "体育博彩（包括相对博彩）",
    "Amusements": "娱乐税",
    "Other selective sales and gross receipts": "其他选择性销售和总收入税",
    "Motor vehicles": "汽车税",
    "Motor vehicle operators": "汽车操作员税",
    "Corporations in general": "一般公司税",
    "Hunting and fishing": "狩猎和钓鱼税",
    "Occupation and businesses": "职业和商业税",
    "Other license taxes": "其他许可证税",
    "Individual income": "个人所得税",
    "Corporation net income": "公司净收入税",
    "Death and gift": "遗产和赠与税",
    "Severance": "离职税",
    "Documentary and stock transfer": "文件和股票转让税",
    "Other taxes, NEC": "其他未分类税收"
}

translation_dict = {
    "U.S. Total (excludes Washington, D.C.)": "美国总计（不包括华盛顿特区）",
    "Alabama": "亚拉巴马州",
    "Alaska": "阿拉斯加州",
    "Arizona": "亚利桑那州",
    "Arkansas": "阿肯色州",
    "California": "加利福尼亚州",
    "Colorado": "科罗拉多州",
    "Connecticut": "康涅狄格州",
    "Delaware": "特拉华州",
    "Florida": "佛罗里达州",
    "Georgia": "乔治亚州",
    "Hawaii": "夏威夷州",
    "Idaho": "爱达荷州",
    "Illinois": "伊利诺伊州",
    "Indiana": "印第安纳州",
    "Iowa": "艾奥瓦州",
    "Kansas": "堪萨斯州",
    "Kentucky": "肯塔基州",
    "Louisiana": "路易斯安那州",
    "Maine": "缅因州",
    "Maryland": "马里兰州",
    "Massachusetts": "马萨诸塞州",
    "Michigan": "密歇根州",
    "Minnesota": "明尼苏达州",
    "Mississippi": "密西西比州",
    "Missouri": "密苏里州",
    "Montana": "蒙大拿州",
    "Nebraska": "内布拉斯加州",
    "Nevada": "内华达州",
    "New Hampshire": "新罕布什尔州",
    "New Jersey": "新泽西州",
    "New Mexico": "新墨西哥州",
    "New York": "纽约州",
    "North Carolina": "北卡罗来纳州",
    "North Dakota": "北达科他州",
    "Ohio": "俄亥俄州",
    "Oklahoma": "俄克拉荷马州",
    "Oregon": "俄勒冈州",
    "Pennsylvania": "宾夕法尼亚州",
    "Rhode Island": "罗得岛州",
    "South Carolina": "南卡罗来纳州",
    "South Dakota": "南达科他州",
    "Tennessee": "田纳西州",
    "Texas": "德克萨斯州",
    "Utah": "犹他州",
    "Vermont": "佛蒙特州",
    "Virginia": "弗吉尼亚州",
    "Washington": "华盛顿州",
    "West Virginia": "西弗吉尼亚州",
    "Wisconsin": "威斯康星州",
    "Wyoming": "怀俄明州",
    "Washington, D.C.": "华盛顿特区"
}

st.set_page_config(layout="wide")


tax_revenue = load_tax_revenue_data()
states = tax_revenue['state'].unique().tolist()
tax_categories = tax_revenue['tax_category'].unique().tolist()
fiscal_quarters = tax_revenue['fiscal_quarter'].unique().tolist()

state_total = "U.S. Total (excludes Washington, D.C.)"
category_total = "Total Taxes"


#--------------------------------  State Fiscal Revenue  --------------------------------#

st.title('美国各州财政收入')

tab1, tab2 = st.tabs(["税收-按州分类", "税收-按税种分类"])

with tab1:
    qt = st.selectbox('请选择财政季度/范围', fiscal_quarters, index=0, key='tab1a')
    categories=st.multiselect('请选择一个或多个税种', tax_categories, default=[], key='tab1b')
    
    for c in categories:
        fig = px.bar(
            tax_revenue.query(f'fiscal_quarter=="{qt}" & tax_category=="{c}" & state!="{state_total}" ')\
                .sort_values('revenue', ascending=False)\
                .assign(state=lambda x: x['state'].map(translation_dict))\
                .assign(tax_category=lambda x: x['tax_category'].map(tax_translation_dict)),
            x='state',
            y='revenue',
            title=f'各州税收收入：{c}',
        )
        fig.update_layout(
            xaxis_title='州名',
            yaxis_title='财政收入 (十亿美元)',
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    qt = st.selectbox('请选择财政季度/范围', fiscal_quarters, index=0, key='tab2a')
    states=st.multiselect('请选择州', states, default=[], key='tab2b')
    
    for s in states:
        fig = px.bar(
            tax_revenue.query(f'fiscal_quarter=="{qt}" & state=="{s}" & tax_category!="{category_total}" ')\
                .sort_values('revenue', ascending=False)\
                .assign(state=lambda x: x['state'].map(translation_dict))\
                .assign(tax_category=lambda x: x['tax_category'].map(tax_translation_dict)),
            x='tax_category',
            y='revenue',
            title=f'各税种税收收入{s}',
        )
        fig.update_layout(
            xaxis_title='税种',
            yaxis_title='财政收入 (十亿美元)',
        )
        st.plotly_chart(fig, use_container_width=True)