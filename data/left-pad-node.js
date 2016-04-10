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

var N = parseInt(process.argv[2]);
for (var i = 0; i < 10; i++) {
  leftpad("hi", 10+N, 'x');
}
