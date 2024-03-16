//程式碼開始
var　CHANNEL_ACCESS_TOKEN　=　"3rWORuikyamxptl2guKgn4kIyCYVFiYOZjfRSZ3hgnTKl5kIx3jhvkq6FiLZlOo6HJS2g3WFQPdGTeA2hIDiNsR8jwdyKcC95QwKISrGcu/nZxCINEcE8goEWHXk6c/frIE56ge/OGbewI9uzCwOGAdB04t89/1O/w1cDnyilFU=";
var　spreadSheetID　=　"1Xx0TnoamQkH0_gaLOOzMyAmGBUwufYKGURHVxrzfOiw";
var　myID　=　"";
var　confirmMessage　=　"您所輸入的資料如下：";
var　cancelMessage　=　"您所輸入的資料已取消";
var　welcomeTitle　=　"定時提醒系統，請輸入相關資料進行設定";
var　finishTitle　=　"設定完成，時間到了會發出　Line　訊息通知您";
var　ignoreWord　=　["help","?"];
var　stopAlarmWord　=　"ok";　　　　//停止提醒用的關鍵字
var　spreadSheet　=　SpreadsheetApp.openById(spreadSheetID);
var　sheet　=　spreadSheet.getActiveSheet();
var　lastRow　=　sheet.getLastRow();
var　lastColumn　=　sheet.getLastColumn();
var　sheetData　=　sheet.getSheetValues(1,　1,　lastRow,　lastColumn);
//接收使用者訊息
function　doPost(e)　{
　　var　userData　=　JSON.parse(e.postData.contents);
　　console.log(userData);
　　//　取出　replayToken　和發送的訊息文字
　　var　replyToken　=　userData.events[0].replyToken;
　　var　clientID　=　userData.events[0].source.userId;
//　　if　(clientID　!=　myID)　{return;}
　　try　{
　　　　var　clientMessage　=　userData.events[0].message.text;
　　　　for　(var　i　=　0;　i　<　ignoreWord.length;　i++)　{
　　　　　　if　(clientMessage.toLowerCase()　==　ignoreWord[i].toLowerCase())　{　return;　}
　　　　}
　　　　if　(clientMessage.toLowerCase()　==　stopAlarmWord.toLowerCase())　{
　　　　　　stopAlarm(spreadSheetID);
　　　　　　return;
　　　　}
　　　　var　replyData　=　getUserAnswer(clientID,　clientMessage);
　　}
　　catch(err)　{
　　　　var　clientMessage　=　userData.events[0].postback.data;
　　　　switch　(clientMessage)　{
　　　　　　case　"DateMessage":
　　　　　　　　clientMessage　=　userData.events[0].postback.params.date;
　　　　　　　　var　replyData　=　getUserAnswer(clientID,　clientMessage);
　　　　　　　　break;
　　　　　　case　"TimeMessage":
　　　　　　　　clientMessage　=　userData.events[0].postback.params.time;
　　　　　　　　var　replyData　=　getUserAnswer(clientID,　clientMessage);
　　　　　　　　break;
　　　　　　default:
　　　　　　　　var　replyData　=　checkConfirmData(CHANNEL_ACCESS_TOKEN,　clientID,　clientMessage,　replyToken);
　　　　}
　　}
　　var　QandO　=　[sheetData[0],　sheetData[1],　sheetData[replyData[0]　-　1]];
　　switch　(replyData[1])　{
　　　　case　-2:
　　　　　　return;
　　　　case　-1:
　　　　　　var　replyMessage　=　cancelMessage;
　　　　　　break;
　　　　case　0:
　　　　　　var　replyMessage　=　confirmMessage　+　"\n\n";
　　　　　　replyMessage　+=　"提醒時間："　+　alarmTimeConvert(QandO[2][1],　QandO[2][2])　+　"\n\n";
　　　　　　replyMessage　+=　"提醒事項："　+　clientMessage;
　　　　　　sendConfirmMessage(CHANNEL_ACCESS_TOKEN,　replyToken,　replyMessage);
　　　　　　return;
　　　　case　1:
　　　　　　var　replyMessage　=　finishTitle;
　　　　　　break;
　　　　case　2:
　　　　　　pushMessage(CHANNEL_ACCESS_TOKEN,　clientID,　welcomeTitle);
　　　　　　var　replyMessage　=　　QandO[0][replyData[1]　-　1];
　　　　　　sendDateMessage(CHANNEL_ACCESS_TOKEN,　replyToken,　replyMessage);
　　　　　　return;
　　　　case　3:
　　　　　　var　replyMessage　=　　QandO[0][replyData[1]　-　1];
　　　　　　sendTimeMessage(CHANNEL_ACCESS_TOKEN,　replyToken,　replyMessage);
　　　　　　return;
　　　　default:
　　　　　　var　replyMessage　=　QandO[0][replyData[1]　-　1]　+　"\n\n"　+　QandO[1][replyData[1]　-　1];
　　}
　　sendReplyMessage(CHANNEL_ACCESS_TOKEN,　replyToken,　replyMessage);
}
//判斷使用者回答到第幾題
function　getUserAnswer(clientID,　clientMessage)　{
　　var　returnData　=　[];
　　for　(var　i　=　0;　i　<　lastRow;　i++)　{
　　　　if　(sheetData[i][0]　==　clientID　&&　sheetData[i][lastColumn　-　1]　==　"")　{
　　　　　　for　(var　j　=　1;　j　<=　lastColumn　-1;　j++)　{
　　　　　　　　if　(sheetData[i][j]　==　"")　{break;}
　　　　　　}
　　　　　　sheet.getRange(i　+　1,　j　+　1).setValue(clientMessage);
　　　　　　//如果使用者已經回答了最後一題，就把完成時間填上。不然就送出下一題給使用者
　　　　　　if　(j　+　3　==　lastColumn)　{
　　　　　　　　returnData　=　[i　+　1,　0];
　　　　　　}
　　　　　　else　{
　　　　　　　　returnData　=　[i　+　1,　j　+　2];
　　　　　　}
　　　　　　return　returnData;
　　　　　　break;
　　　　}
　　}
　　//如果使用者還沒有回答過任何資料，就新增加一列在最後，把使用者ID輸入並開始送出題目
　　sheet.insertRowAfter(lastRow);
　　sheet.getRange(lastRow　+　1,　1).setValue(clientID);
　　returnData　=　[lastRow　+　1,　2];
　　return　returnData;
}
//把試算表內的啟動時間轉換成正確的時間格式
function　alarmTimeConvert(dateData,　timeData)　{
　　var　alarmTime　=　new　Date　((+new　Date(dateData))　+　(+new　Date(timeData))　-　(+new　Date('1899/12/30　00:00:00')))　;
　　return　alarmTime;
}
//把「是否提醒」數值調成1
function　stopAlarm(spreadSheetID)　{
　　var　TimeNow　=　new　Date();
　　for　(var　i　=　2;　i　<　lastRow;　i++)　{
　　　　if　(sheetData[i][4]　==　0)　{
　　　　　　var　startTime　=　alarmTimeConvert(sheetData[i][1],　sheetData[i][2]);
　　　　　　if　(startTime　<　TimeNow)　{
　　　　　　　　sheet.getRange(i　+　1,　5).setValue('1');
　　　　　　}
　　　　}
　　}　　
}
//取得需要發送的訊息
function　getAlarmData()　{
　　var　TimeNow　=　new　Date();
　　var　pushContents　=　[];
　　var　j　=　0;
　　for　(var　i　=　2;　i　<　lastRow;　i++)　{
　　　　if　(sheetData[i][4]　===　0)　{
　　　　　　var　startTime　=　alarmTimeConvert(sheetData[i][1],　sheetData[i][2]);
　　　　　　if　(startTime　<　TimeNow)　{
　　　　　　　　pushContents[j]　=　[sheetData[i][0],　sheetData[i][3]];
　　　　　　　　j++;
　　　　　　}
　　　　}
　　}
　　if　(pushContents.length　!=　0)　{
　　　　for　(var　i　=　0;　i　<　5;　i++)　{
　　　　　　for　(var　j　=　0;　j　<　pushContents.length;　j++)　{
　　　　　　　　pushMessage(CHANNEL_ACCESS_TOKEN,　pushContents[j][0],　pushContents[j][1]);
　　　　　　}
　　　　　　Utilities.sleep(1000);
　　　　}
　　}
}
//主動傳送　Line　Bot　訊息給使用者
function　pushMessage(CHANNEL_ACCESS_TOKEN,　userID,　pushContent)　{
　　var　url　=　'https://api.line.me/v2/bot/message/push';
　　UrlFetchApp.fetch(url,　{
　　　　'headers':　{
　　　　　　'Content-Type':　'application/json;　charset=UTF-8',
　　　　　　'Authorization':　'Bearer　'　+　CHANNEL_ACCESS_TOKEN,
　　　　},
　　　　'method':　'post',
　　　　'payload':　JSON.stringify({
　　　　　　'to':　userID,
　　　　　　'messages':　[{
　　　　　　　　'type':　'text',
　　　　　　　　'text':pushContent,
　　　　　　}],
　　　　}),
　　});
}
//回送　Line　Bot　訊息給使用者
function　sendReplyMessage(CHANNEL_ACCESS_TOKEN,　replyToken,　replyMessage)　{
　　var　url　=　'https://api.line.me/v2/bot/message/reply';
　　UrlFetchApp.fetch(url,　{
　　　　'headers':　{
　　　　　　'Content-Type':　'application/json;　charset=UTF-8',
　　　　　　'Authorization':　'Bearer　'　+　CHANNEL_ACCESS_TOKEN,
　　　　},
　　　　'method':　'post',
　　　　'payload':　JSON.stringify({
　　　　　　'replyToken':　replyToken,
　　　　　　'messages':　[{
　　　　　　　　'type':　'text',
　　　　　　　　'text':replyMessage,
　　　　　　}],
　　　　}),
　　});
}
//分析確認按鈕按下的時機
function　checkConfirmData(CHANNEL_ACCESS_TOKEN,　clientID,　clientMessage,　replyToken)　{
　　var　returnData　=　[];
　　for　(var　i　=　lastRow　-　1;　i　>=　0;　i--)　{
　　　　if　(sheetData[i][0]　==　clientID　&&　sheetData[i][lastColumn　-　3]　!=　""　&&　sheetData[i][lastColumn　-　1]　==　"")　{
　　　　　　if　(clientMessage　==　"DecideConfirm")　{
　　　　　　　　sheet.getRange(i　+　1,　lastColumn　-　1).setValue(0);
　　　　　　　　sheet.getRange(i　+　1,　lastColumn).setValue(Date());
　　　　　　　　returnData　=　[i　+　1,　1];
　　　　　　}
　　　　　　else　if　(clientMessage　==　"DecideCancel"){
　　　　　　　　returnData　=　[i　+　1,　-1];
　　　　　　　　sheet.deleteRow(i　+　1);
　　　　　　}
　　　　　　return　returnData;
　　　　　　break;
　　　　}
　　}
　　//使用者亂按舊的確認或刪除按鈕時的處理方式
　　returnData　=　[1,　-2];
　　return　returnData;　　
}
//傳送選擇日期按鈕給使用者（使用　Line　Template　datetimepicker）
function　sendDateMessage(CHANNEL_ACCESS_TOKEN,　replyToken,　replyMessage)　{
　　var　dt　=　new　Date();
　　UrlFetchApp.fetch("https://api.line.me/v2/bot/message/reply",　{
　　　　"headers":　{
　　　　　　"Content-Type":　"application/json;　charset=UTF-8",
　　　　　　"Authorization":　"Bearer　"　+　CHANNEL_ACCESS_TOKEN,
　　　　},
　　　　"method":　"post",
　　　　"payload":　JSON.stringify({
　　　　　　"replyToken":　replyToken,
　　　　　　"messages":　[{
　　　　　　　　"type":　"template",
　　　　　　　　"altText":　replyMessage,
　　　　　　　　"template":　{
　　　　　　　　　　"type":　"buttons",
　　　　　　　　　　"text":　replyMessage,
　　　　　　　　　　"actions":　[
　　　　　　　　　　　　{
　　　　　　　　　　　　　　"type":"datetimepicker",
　　　　　　　　　　　　　　"label":"點選並輸入提醒日期",
　　　　　　　　　　　　　　"data":"DateMessage",
　　　　　　　　　　　　　　"mode":"date",
　　　　　　　　　　　　}
　　　　　　　　　　]
　　　　　　　　}
　　　　　　}],
　　　　}),
　　});
}
//傳送選擇時間按鈕給使用者（使用　Line　Template　datetimepicker）
function　sendTimeMessage(CHANNEL_ACCESS_TOKEN,　replyToken,　replyMessage)　{
　　var　dt　=　new　Date();
　　UrlFetchApp.fetch("https://api.line.me/v2/bot/message/reply",　{
　　　　"headers":　{
　　　　　　"Content-Type":　"application/json;　charset=UTF-8",
　　　　　　"Authorization":　"Bearer　"　+　CHANNEL_ACCESS_TOKEN,
　　　　},
　　　　"method":　"post",
　　　　"payload":　JSON.stringify({
　　　　　　"replyToken":　replyToken,
　　　　　　"messages":　[{
　　　　　　　　"type":　"template",
　　　　　　　　"altText":　replyMessage,
　　　　　　　　"template":　{
　　　　　　　　　　"type":　"buttons",
　　　　　　　　　　"text":　replyMessage,
　　　　　　　　　　"actions":　[
　　　　　　　　　　　　{
　　　　　　　　　　　　　　"type":"datetimepicker",
　　　　　　　　　　　　　　"label":"點選並輸入提醒時間",
　　　　　　　　　　　　　　"data":"TimeMessage",
　　　　　　　　　　　　　　"mode":"time",
　　　　　　　　　　　　}
　　　　　　　　　　]
　　　　　　　　}
　　　　　　}],
　　　　}),
　　});
}
//傳送確認按鈕給使用者（使用　Line　Template　Confirm）
function　sendConfirmMessage(CHANNEL_ACCESS_TOKEN,　replyToken,　replyMessage)　{
　　UrlFetchApp.fetch("https://api.line.me/v2/bot/message/reply",　{
　　　　"headers":　{
　　　　　　"Content-Type":　"application/json;　charset=UTF-8",
　　　　　　"Authorization":　"Bearer　"　+　CHANNEL_ACCESS_TOKEN,
　　　　},
　　　　"method":　"post",
　　　　"payload":　JSON.stringify({
　　　　　　"replyToken":　replyToken,
　　　　　　"messages":　[{
　　　　　　　　"type":　"template",
　　　　　　　　"altText":　replyMessage,
　　　　　　　　"template":　{
　　　　　　　　　　"type":　"confirm",
　　　　　　　　　　"text":　replyMessage,
　　　　　　　　　　"actions":　[
　　　　　　　　　　　　{
　　　　　　　　　　　　　　"type":　"postback",
　　　　　　　　　　　　　　"label":　"確認",
　　　　　　　　　　　　　　"data":　"DecideConfirm"
　　　　　　　　　　　　},
　　　　　　　　　　　　{
　　　　　　　　　　　　　　"type":　"postback",
　　　　　　　　　　　　　　"label":　"取消",
　　　　　　　　　　　　　　"data":　"DecideCancel"
　　　　　　　　　　　　}
　　　　　　　　　　]
　　　　　　　　}
　　　　　　}],
　　　　}),
　　});
}
//程式碼結束