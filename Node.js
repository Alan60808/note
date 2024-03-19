const express = require('express');
const line = require('@line/bot-sdk');

const app = express();

const config = {
  channelAccessToken: '3rWORuikyamxptl2guKgn4kIyCYVFiYOZjfRSZ3hgnTKl5kIx3jhvkq6FiLZlOo6HJS2g3WFQPdGTeA2hIDiNsR8jwdyKcC95QwKISrGcu/nZxCINEcE8goEWHXk6c/frIE56ge/OGbewI9uzCwOGAdB04t89/1O/w1cDnyilFU=',
  channelSecret: '60c382a7a969d7c0a80e26d8c792d34f'
};

const client = new line.Client(config);

app.post('/callback', express.json(), (req, res) => {
  const events = req.body.events;

  for (const event of events) {
    if (event.type === 'message') {
      if (event.message.text === '提醒我') {
        client.pushMessage(event.source.userId, {
          type: 'text',
          text: '您已設定提醒，時間為 10 分鐘後'
        });

        setTimeout(() => {
          client.pushMessage(event.source.userId, {
            type: 'text',
            text: '提醒：您有事情要做'
          });
        }, 10 * 60 * 1000);
      }
    }
  }

  res.end();
});

app.listen(3000);