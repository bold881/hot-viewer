var express = require('express')
var router = express.Router()

router.use(function timelog  (req, res, next) {
    console.log('Time:  ', Date.now())
    next()
})

router.get('/', function(req,  res) {
    var options = {
        root: __dirname + '/weipy/'
    }
    res.sendFile('index.html', options, function (err) {
        if(err) {
            console.log(err)
            res.status(err.status).end()
        } else {
            console.log('Sent: ', 'weipy/index.html');
        }
    })
})

router.get('/about', function (req, res) {
    res.send('About weipy')
})

module.exports = router