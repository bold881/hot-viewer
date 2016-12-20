var express = require('express')
var router = express.Router()
var MongoClient = require('mongodb').MongoClient
    , assert = require('assert')

var url = 'mongodb://localhost:27017/weibo'
var collection;
MongoClient.connect(url, function(err, db) {
    assert.equal(null, err)
    collection = db.collection('hottop');
    console.log("Connected successfully to server");
})

router.use(function timelog  (req, res, next) {
    console.log('Time:  ', Date.now())
    next()
})

router.get('/', function(req,  res) {
    collection.find({}, {nk: 1, ctt: 1, lc: 1, ccc: 1, rc: 1, ct: 1}).toArray(function(err, docs) {
        assert.equal(err, null);
        var responseText = 'HOT TOP<br>';
        var i = 0;
        docs.forEach(function(docItem) {
            i++;
            responseText += '<br><br>' + i + '<br>' + JSON.stringify(docItem);
        });

        res.send(responseText);
    });
})

router.get('/about', function (req, res) {
    res.send('About birds')
})

module.exports = router