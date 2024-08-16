var fm1 = document.createElement('form');
fm1.name = 'frmGlobalNudetect';
var in1 = document.createElement('input');
in1.type = 'hidden';
in1.name = 'nds-pmd';
fm1.appendChild(in1);
var fst1 = document.getElementsByTagName('body')[0];
fst1.insertBefore(fm1, fst1.firstChild);
! function() {
    var n, e, i, o, a, d, t;
    n = window, e = document, i = "script", o = "https://api-ticketmaster.nd.nudatasecurity.com/2.2/w/w-481390/sync/js/", (t = n.ndsapi || (n.ndsapi = {})).config = {
        q: [],
        ready: function(n) {
            this.q.push(n)
        }
    }, a = e.createElement(i), d = e.getElementsByTagName(i)[0], a.src = o, d.parentNode.insertBefore(a, d), a.onload = function() {
        t.load(o)
    };
    var s = window.ndsapi;
    s.config.ready(function() {
        s.setSessionId(epsSID)
    })
}()