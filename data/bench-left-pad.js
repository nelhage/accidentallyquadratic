function leftpad (str, len, ch) {
  str = String(str);

  var i = -1;

  if (!ch && ch !== 0) ch = ' ';

  len = len - str.length;

  while (++i < len) {
    str = ch + str;
  }

  return str;
}

var ts = [];
var N = 1000000;
for (var i = 0; i < N; i += N/50) {
// for (var i = 1; i < N; i *= 2) {
  var a = new Date();
  for (var j = 0; j < 100; j++) {
    leftpad("hi", 10+i, 'x');
  }
  var b = new Date();
  ts.push({i: i, t: b-a});
  if ('console' in this)
    console.log("%d,%d",i,b-a);
  else
    print(i,",",b-a);
}
console.log(ts);
