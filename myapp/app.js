var express = require('express')
var app = express()

app.get('/', function(req,  res) {
    res.send('GET homepage')
})

var birds = require('./birds')
var weipy = require('./weipy')

app.use('/birds', birds)
app.use('/weipy', weipy)
app.use(express.static('weipy'))

app.listen(3000, function () {
    console.log('Example app listening on port 3000!')
})