# ================================================================


# ================================================================

from django.shortcuts import render
from tourbot.bot import *
# Create your views here.
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from linebot.models import (
    MessageEvent,
    TextSendMessage,
)

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    if request.method == "POST":
        signature = request.META["HTTP_X_LINE_SIGNATURE"]
        body = request.body.decode("utf-8")
        #
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                message = []
                first = event.message.text
                if first.split(" ")[0] == "店家":  # 輸入格式為："店家.編號"
                    try:
                        orderDetail = getShopDetail(first.split(" ")[1])  # 確認為店家
                        message.append(
                            TextSendMessage(text=f"為您查詢累積訂單及月結\n累積訂單為：{orderDetail[0]}\n總金額為{orderDetail[1]}")
                        )
                    except Exception:
                        message.append(TextSendMessage(text="此店家號碼不存在，或聯絡我們"))
                elif "b" in first:
                    for m in first.split(" "):
                        dic = getWholeValues(m)
                        if dic != 0:
                            msg = f"您所查詢的\n訂單編號為：{dic[0]}\n顧客姓名：{dic[1]}\n活動名稱：{dic[2]}\n活動金額：{dic[3]}"
                            message.append(TextSendMessage(text=msg))
                        else:
                            message.append(TextSendMessage(text="此訂單號碼不存在，或聯絡我們"))
                else:
                    message.append(TextSendMessage(text="輸入錯誤，若須查詢訂單編號，\n請輸入編號如：b01 b02\n(多筆以空格區分 至多五則)\n若須查詢月結與累積訂單數，請輸入'店家 編號'如：店家 a01\n其他錯誤請聯絡我們"))
                line_bot_api.reply_message(event.reply_token, message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()