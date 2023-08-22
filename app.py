import binascii
import codecs

import streamlit as st
import requests
import pandas as pd
from annotated_text import annotated_text
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad

# 全局配置
st.set_page_config(page_title='数据审核', layout='wide')

# 读取Excel文件
data = pd.read_excel('平台字典.xlsx', index_col='代码')

# 将数据转换为字典
dictionary = data.to_dict()


def bs64_password(password):
    data = password
    data_obj = bytes(data, 'utf-8')
    key = '12345678'
    key_obj = bytes(key, 'utf-8')
    cipher = DES.new(key_obj, DES.MODE_ECB)
    ct = cipher.encrypt(pad(data_obj, 8))
    pwd = codecs.decode(binascii.b2a_base64(ct), 'UTF-8')
    pwd = pwd.strip('\n')
    return pwd


session = requests.Session()
user_y_name = st.sidebar.text_input('用户名')
user_y_password = st.sidebar.text_input('密码', type='password')
pj = st.sidebar.selectbox(
    "请选择项目",
    ('fxpk', 'jspk', 'qppk')
)

if st.sidebar.button('登录'):
    st.sidebar.write('登录成功！')

login_url = 'http://139.224.72.67:8081/outletcloud/outlet-auth/app/login'
data = {
    "username": user_y_name,
    "password": bs64_password(user_y_password),
    "projectSerial": pj
}
token = session.post(login_url, json=data).json()['data']['password']
session.headers = {

    "Api-Client": "outlet-api-pushi-release",
    'Token': token,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
}
uid_url = 'http://139.224.72.67:8081/outletcloud/outlet-api/outlet/approved/_list'
data_uid = {
    "firstResult": 0,
    "maxResult": 1,
    "projectSerial": pj,
    "reportTimeOrder": "DESC"
}
list = session.post(uid_url, json=data_uid)
uids = []
for i in list.json()['data']['list']:
    uid = i['outletUid']
    taskId = i['taskId']
    reportType = i['reportType']
    uids.append([uid, taskId, reportType])
for o in uids:
    uid = o[0]
    taskId = o[1]
    reportType = o[2]
    data1 = {
        'outletUid': uid,
        'module': '1002'
    }
    data2 = {
        'outletUid': uid,
        'module': '1001'
    }

    url_data = 'http://139.224.72.67:8081/outletcloud/outlet-api/ubiOutletInfo/queryInteriorOutletDetail'
    info = session.post(url=url_data, data=data1).json()
    info_pc = session.post(url=url_data, data=data2).json()
    if info['data']['ubiOutletInfoTraceDto']['name'] != '':

        paichazhaopian = []
        img = info_pc['data']['ubiOutletInfoInvDto']['outletPhotos']
        for j in img:
            paichazhaopian.append(j['imageUrl'])

        zhoubianhuanjingzhaopian = []
        img = info['data']['ubiOutletInfoTraceDto']['aroundPhoto']
        for k in img:
            zhoubianhuanjingzhaopian.append(k['imageUrl'])

        reportTime = info['data']['ubiOutletInfoTraceDto']['reportTime']
        # 排口名称
        name = info['data']['ubiOutletInfoTraceDto']['name']
        # 排查备注
        remark = info['data']['ubiOutletInfoTraceDto']['remark']
        # 溯源方式
        traceMode = info['data']['ubiOutletInfoTraceDto']['traceMode']
        # 溯源手段
        try:
            traceMethod = info['data']['ubiOutletInfoTraceDto']['traceMethod']
        except:
            traceMethod = '错误'

        # 大类
        try:
            outletMaxType = info['data']['ubiOutletInfoTraceDto']['outletMaxType']
        except:
            outletMaxType = '错误'
        # 中类
        try:
            outletMiddleType = info['data']['ubiOutletInfoTraceDto']['outletMiddleType']
        except:
            outletMiddleType = '错误'
        # 备注
        outletTypeRemark = info['data']['ubiOutletInfoTraceDto']['outletTypeRemark']
        # 管道材质
        pipelineMaterial = info['data']['ubiOutletInfoTraceDto']['pipelineMaterial']
        # 入河方式
        entryRiverTypeValue = info['data']['ubiOutletInfoTraceDto']['entryRiverTypeValue']
        # 排水特征
        dischargeTypeValue = info['data']['ubiOutletInfoTraceDto']['dischargeTypeValue']
        # 排水水质特征
        entryRiverTypeValueRemark = info['data']['ubiOutletInfoTraceDto']['entryRiverTypeValueRemark']
        # 排水方式
        dischargeType = info['data']['ubiOutletInfoTraceDto']['dischargeType']
        # 污水疑似来源
        try:
            sewageSuspectedSourceValue = \
                info['data']['ubiOutletInfoTraceDto']['sewageSuspectedSourceValue'][0]
        except:
            sewageSuspectedSourceValue = '错误'
        # 污水来源
        sewageSource = info['data']['ubiOutletInfoTraceDto']['sewageSource']
        # 污水来源数量
        sewageSourceNumber = info['data']['ubiOutletInfoTraceDto']['sewageSourceNumber']




        # 是否混排
        try:
            flagMixture = '否' if info['data']['ubiOutletInfoTraceDto']['flagMixture'] == '0' else '是'
        except:
            flagMixture = '错误'
        st.markdown(f'上报人:{info["data"]["ubiOutletInfoTraceDto"]["userName"]}')
        st.markdown(f'排口编码: {uid}')
        st.markdown(f'上传时间: {reportTime}')
        # if info['data']['ubiOutletInfoTraceDto']['flagTraceDifficult'] == 1:
        #     st.title(f'是否难点: :red[是]')
        # else:
        #     st.title(f'是否难点: 否')
        st.text(f'------------------------------------------------------------------------')

        if dictionary["名称"][int(outletMiddleType)] in name or outletTypeRemark in name:
            st.markdown(f'排口名称: {name}')
        else:
            annotated_text('排口名称:', (name, "", "#faf"))
        if outletTypeRemark != "":
            st.markdown(
                f'排口类型: {dictionary["名称"][int(outletMaxType)]}-{dictionary["名称"][int(outletMiddleType)]}-{outletTypeRemark}')
        else:
            try:
                st.markdown(
                    f'排口类型: {dictionary["名称"][int(outletMaxType)]}-{dictionary["名称"][int(outletMiddleType)]}')
            except:
                st.markdown(
                    f'排口类型: :red[{outletMaxType}]')
        st.text(f'------------------------------------------------------------------------')
        st.markdown(f'管道材质: {dictionary["名称"][int(pipelineMaterial)]}')
        st.markdown(f'入河方式: {dictionary["名称"][int(entryRiverTypeValue)]}')
        st.text(f'------------------------------------------------------------------------')
        st.markdown(f'排水特征: {dictionary["名称"][int(dischargeTypeValue)]}')
        st.markdown(f'排水方式: {dictionary["名称"][int(dischargeType)]}')
        st.text(f'------------------------------------------------------------------------')
        if flagMixture == '错误':
            annotated_text('是否混排:', (flagMixture, "", "#faf"))

        else:
            st.markdown(f'是否混排: {flagMixture}')
        if sewageSuspectedSourceValue == '错误':
            annotated_text('污水疑似来源:', (sewageSuspectedSourceValue, "", "#faf"))

        else:
            st.markdown(f'污水疑似来源: {dictionary["名称"][int(sewageSuspectedSourceValue)]}')
        st.markdown(f'污水来源: {sewageSource}')

        if sewageSourceNumber == '错误':
            annotated_text('污水来源数量:', (sewageSourceNumber, "", "#faf"))

        else:
            st.markdown(f'污水来源数量: {sewageSourceNumber}')
        st.text(f'------------------------------------------------------------------------')
        if traceMethod == '错误':

            annotated_text('溯源手段:', (traceMethod, "", "#faf"))

        else:
            st.markdown(f'溯源手段: {dictionary["名称"][int(traceMethod[0])]}')

        st.header('排查照片')
        columns = st.columns(2)
        images = [paichazhaopian[0], paichazhaopian[1]]

        for i1 in range(len(columns)):
            with columns[i1]:
                st.image(images[i1])

        st.header('周边环境照片')
        columns = st.columns(2)
        images = [zhoubianhuanjingzhaopian[0], zhoubianhuanjingzhaopian[1]]

        for i2 in range(len(columns)):
            with columns[i2]:
                st.image(images[i2])
        nodes = []
        # 节点数量
        node_len = len(info['data']['ubiOutletInfoTraceDto']['node'])
        if node_len > 0:
            # 节点名称/类型
            for j in range(node_len):
                lon_lat = []
                imgs = []
                # 节点名称
                nodeSerial = info['data']['ubiOutletInfoTraceDto']['node'][j]['nodeSerial']
                # 节点类型
                nodeType = info['data']['ubiOutletInfoTraceDto']['node'][j]['nodeType']
                # 节点照片
                nodePhoto = info['data']['ubiOutletInfoTraceDto']['node'][j]['nodePhoto']
                for p in range(len(nodePhoto)):
                    try:
                        # 节点经度
                        img_lon = info['data']['ubiOutletInfoTraceDto']['node'][j]['nodePhoto'][p][
                            'lon']
                        # 节点纬度
                        img_lat = info['data']['ubiOutletInfoTraceDto']['node'][j]['nodePhoto'][p][
                            'lat']
                    except:
                        img_lon, img_lat = '无', '无'

                    nodePhoto_img = info['data']['ubiOutletInfoTraceDto']['node'][j]['nodePhoto'][p][
                        'rndOssPath']
                    if nodePhoto_img == '':
                        nodePhoto_img = info['data']['ubiOutletInfoTraceDto']['node'][j]['nodePhoto'][p][
                            'imageUrl']
                    imgs.append(nodePhoto_img)
                    lon_lat.append((img_lon, img_lat))
                nodes.append((nodeSerial, nodeType, imgs, lon_lat))
            st.header('节点信息')
            for i3 in nodes:
                columns = st.columns(len(i3[2]))
                for j1 in range(len(columns)):
                    with columns[j1]:
                        if i3[3] == ['无', '无']:
                            st.text(f'节点：{i3[0]}  类型：{dictionary["名称"][int(i3[1])]} 经纬度：无')
                        else:
                            st.text(f'节点：{i3[0]}  类型：{dictionary["名称"][int(i3[1])]} 经纬度：有')
                        st.image(i3[2][j1])
    # 审核
    sh_url = 'http://139.224.72.67:8081/outletcloud/outlet-api/outlet/approvalReport'
    res = st.text_area(f'审核理由（留空即为通过）{uid}')
    but = st.button('提交', key=uid)

    if res != '':
        approvalType = 220304
    else:
        approvalType = 220305

    sh_data = {
        "outletUid": uid,
        "approvalType": approvalType,
        "approvalRemark": res,
        "reportType": reportType,
        "disposalMethod": 0,
        "outsideSelectEntity": {},
        "taskId": taskId
    }
    if but:
        shenhe = session.post(url=sh_url, json=sh_data)
        st.success(shenhe.json()['msg'])
        st.sidebar.success(shenhe.json()['msg'])
    re = st.sidebar.button('刷新')
    if re:
        st.experimental_rerun()
